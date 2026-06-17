"""
Offline retrieval quality eval — Phase 4.

There's no labeled relevance dataset, so this uses a genre/tag-overlap
heuristic as a proxy: for a sample of seed anime, a FAISS neighbor is
"relevant" if it shares at least MIN_SHARED_GENRES genres or has tag
overlap >= MIN_TAG_OVERLAP with the seed. precision@k is then the
fraction of each seed's top-k neighbors that are relevant, averaged
across the sample.

Usage:
    uv run python -m scripts.eval [--k 10] [--sample 200] [--threshold 0.5]
"""

import argparse
import random
import sys

# Force UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.core import index as idx_store

MIN_SHARED_GENRES = 1
MIN_TAG_OVERLAP = 0.2  # jaccard


def _is_relevant(seed: dict, candidate: dict) -> bool:
    seed_genres = set(seed.get("genres") or [])
    cand_genres = set(candidate.get("genres") or [])
    if seed_genres and len(seed_genres & cand_genres) >= MIN_SHARED_GENRES:
        return True

    seed_tags = set(seed.get("tags") or [])
    cand_tags = set(candidate.get("tags") or [])
    if seed_tags and cand_tags:
        jaccard = len(seed_tags & cand_tags) / len(seed_tags | cand_tags)
        if jaccard >= MIN_TAG_OVERLAP:
            return True

    return False


def precision_at_k(seed_faiss_idx: int, k: int) -> float | None:
    index, meta = idx_store.load_index()
    seed = meta.get(str(seed_faiss_idx))
    if seed is None:
        return None

    vec = index.reconstruct(seed_faiss_idx)
    # +1 because the seed itself is always its own nearest neighbor
    results = idx_store.search(vec, top_k=k + 1)

    neighbors = [(i, s) for i, s in results if i != seed_faiss_idx][:k]
    if not neighbors:
        return None

    relevant = sum(1 for i, _ in neighbors if _is_relevant(seed, idx_store.get_anime(i)))
    return relevant / len(neighbors)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--sample", type=int, default=200)
    parser.add_argument("--threshold", type=float, default=0.5, help="Minimum mean precision@k to pass")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    try:
        index, meta = idx_store.load_index()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    all_indices = [int(i) for i in meta.keys()]
    rng = random.Random(args.seed)
    sample_size = min(args.sample, len(all_indices))
    sample = rng.sample(all_indices, sample_size)

    print(f"Evaluating precision@{args.k} on {sample_size} seed anime (of {index.ntotal} total)...")

    scores: list[float] = []
    for faiss_idx in sample:
        score = precision_at_k(faiss_idx, args.k)
        if score is not None:
            scores.append(score)

    if not scores:
        print("ERROR: no scores computed.")
        sys.exit(1)

    mean_precision = sum(scores) / len(scores)
    print(f"\nmean precision@{args.k} = {mean_precision:.4f}  (over {len(scores)} seeds)")
    print(f"threshold = {args.threshold}")

    if mean_precision < args.threshold:
        print(f"\nFAIL: precision@{args.k} {mean_precision:.4f} is below threshold {args.threshold}")
        sys.exit(1)

    print(f"\nPASS: precision@{args.k} meets threshold.")


if __name__ == "__main__":
    main()

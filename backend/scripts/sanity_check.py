"""
Sanity check — Phase 1.

Embeds a text query and prints the top-10 nearest neighbors from the FAISS index.

Usage:
    uv run python -m scripts.sanity_check "calm slice-of-life with great art"
    uv run python -m scripts.sanity_check "dark psychological thriller"
"""

import json
import sys

# Force UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import faiss
import numpy as np

from app.core.config import DATA_DIR, OPENAI_API_KEY
from app.providers.openai_provider import OpenAIEmbeddingProviderSync

TOP_K = 10


def main() -> None:
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        query = "action adventure with beautiful animation"
        print(f"No query given — using default: \"{query}\"\n")

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set.")
        sys.exit(1)

    faiss_path = DATA_DIR / "anime.faiss"
    meta_path = DATA_DIR / "anime_meta.json"

    if not faiss_path.exists():
        print(f"ERROR: Index not found at {faiss_path}")
        print("Run the build script first:  uv run python -m scripts.build_index")
        sys.exit(1)

    # Load index + metadata
    index = faiss.read_index(str(faiss_path))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    # Embed query
    provider = OpenAIEmbeddingProviderSync()
    vec = np.array([provider.embed(query)], dtype=np.float32)
    faiss.normalize_L2(vec)

    # Search
    scores, indices = index.search(vec, TOP_K)

    # Print results
    print(f'\nQuery: "{query}"\n')
    print(f"{'#':<3}  {'Title':<42}  {'Score':>5}  {'Sim':>5}  Genres")
    print("─" * 90)
    for rank, (idx, sim) in enumerate(zip(indices[0], scores[0]), 1):
        if idx == -1:
            continue
        a = meta[str(idx)]
        title = (a.get("title") or a.get("title_romaji") or "Unknown")[:41]
        mean = a.get("mean_score") or 0
        genres = ", ".join((a.get("genres") or [])[:3])
        print(f"{rank:<3}  {title:<42}  {mean:>5}  {sim:>5.3f}  {genres}")


if __name__ == "__main__":
    main()

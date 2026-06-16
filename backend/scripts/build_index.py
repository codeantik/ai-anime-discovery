"""
Offline index builder — Phase 1.

Fetches top anime from AniList GraphQL, embeds via the configured provider,
writes a FAISS index to data/anime.faiss and metadata to data/anime_meta.json.
AniList pages are cached in data/cache/ so re-runs skip fetching.

Usage:
    uv run python -m scripts.build_index
"""

import json
import sys
import time
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows (avoids cp1252 UnicodeEncodeError)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import faiss
import httpx
import numpy as np

from app.core.config import (
    CACHE_DIR,
    DATA_DIR,
    MONGODB_URI,
    OPENAI_API_KEY,
)
from app.providers.openai_provider import OpenAIEmbeddingProviderSync

# ── AniList config ──────────────────────────────────────────────────────────
ANILIST_URL = "https://graphql.anilist.co"
MAX_PAGES = 50       # 50 × 50 = up to 2 500 anime
PER_PAGE = 50
REQUEST_DELAY = 0.8  # seconds between pages (~75 req/min, limit is 90)
EMBED_BATCH = 100    # texts per OpenAI embeddings call

ANIME_QUERY = """
query ($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    pageInfo { hasNextPage }
    media(
      sort: SCORE_DESC
      type: ANIME
      format_in: [TV, MOVIE, OVA, ONA]
      averageScore_greater: 55
    ) {
      id
      title { romaji english }
      description(asHtml: false)
      genres
      tags { name rank isGeneralSpoiler }
      startDate { year }
      format
      meanScore
      averageScore
      episodes
      coverImage { large }
      popularity
    }
  }
}
"""


# ── Helpers ──────────────────────────────────────────────────────────────────

def fetch_page(client: httpx.Client, page: int) -> dict:
    cache_file = CACHE_DIR / f"anilist_page_{page:03d}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    for attempt in range(5):
        resp = client.post(
            ANILIST_URL,
            json={"query": ANIME_QUERY, "variables": {"page": page, "perPage": PER_PAGE}},
            timeout=30,
        )
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 60))
            wait = retry_after + 5
            print(f"\n  Rate limited on page {page}. Waiting {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        break
    else:
        raise RuntimeError(f"Failed to fetch page {page} after 5 attempts (rate limit).")

    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"AniList error on page {page}: {data['errors']}")

    cache_file.write_text(json.dumps(data), encoding="utf-8")
    time.sleep(REQUEST_DELAY)
    return data


def build_embed_text(anime: dict) -> str:
    title = anime["title"].get("english") or anime["title"].get("romaji") or ""
    synopsis = (anime.get("description") or "").strip()[:500]
    genres = ", ".join(anime.get("genres") or [])
    tags = ", ".join(
        t["name"]
        for t in (anime.get("tags") or [])
        if t.get("rank", 0) >= 60 and not t.get("isGeneralSpoiler")
    )
    year = str(anime.get("startDate", {}).get("year") or "")
    fmt = anime.get("format") or ""
    return f"{title} | {genres} | {tags} | {fmt} {year} | {synopsis}".strip()


def fetch_catalog() -> list[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    all_anime: list[dict] = []
    with httpx.Client() as client:
        for page in range(1, MAX_PAGES + 1):
            data = fetch_page(client, page)
            media = data["data"]["Page"]["media"]
            all_anime.extend(media)
            has_next = data["data"]["Page"]["pageInfo"]["hasNextPage"]
            print(f"  Page {page:>3}: +{len(media):>3} anime  (total {len(all_anime):>5})", end="\r")
            if not has_next:
                break

    print()  # newline after \r progress

    # Deduplicate by anilist id
    seen: set[int] = set()
    unique: list[dict] = []
    for a in all_anime:
        if a["id"] not in seen:
            seen.add(a["id"])
            unique.append(a)
    return unique


def embed_all(texts: list[str], provider: OpenAIEmbeddingProviderSync) -> list[list[float]]:
    vectors: list[list[float]] = []
    total = len(texts)
    for i in range(0, total, EMBED_BATCH):
        batch = texts[i : i + EMBED_BATCH]
        vecs = provider.embed_batch(batch)
        vectors.extend(vecs)
        done = min(i + EMBED_BATCH, total)
        print(f"  Embedded {done:>5}/{total}", end="\r")
        if done < total:
            time.sleep(0.1)
    print()
    return vectors


def build_faiss_index(vectors: list[list[float]]) -> faiss.Index:
    matrix = np.array(vectors, dtype=np.float32)
    faiss.normalize_L2(matrix)
    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)
    return index


def build_meta(anime_list: list[dict], texts: list[str]) -> dict[str, dict]:
    meta: dict[str, dict] = {}
    for idx, (anime, text) in enumerate(zip(anime_list, texts)):
        meta[str(idx)] = {
            "faiss_idx": idx,
            "anilist_id": anime["id"],
            "title": anime["title"].get("english") or anime["title"].get("romaji"),
            "title_romaji": anime["title"].get("romaji"),
            "synopsis": (anime.get("description") or "").strip()[:800],
            "genres": anime.get("genres") or [],
            "tags": [
                t["name"]
                for t in (anime.get("tags") or [])
                if t.get("rank", 0) >= 60 and not t.get("isGeneralSpoiler")
            ],
            "year": (anime.get("startDate") or {}).get("year"),
            "format": anime.get("format"),
            "mean_score": anime.get("meanScore") or anime.get("averageScore"),
            "episodes": anime.get("episodes"),
            "cover_image": (anime.get("coverImage") or {}).get("large"),
            "popularity": anime.get("popularity"),
            "embed_text": text,
        }
    return meta


async def _upsert_mongodb(meta: dict[str, dict]) -> None:
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import UpdateOne

    client: AsyncIOMotorClient = AsyncIOMotorClient(MONGODB_URI)
    collection = client["anime_discovery"]["anime"]
    ops = [
        UpdateOne(
            {"anilist_id": doc["anilist_id"]},
            {"$set": doc},
            upsert=True,
        )
        for doc in meta.values()
    ]
    result = await collection.bulk_write(ops)
    client.close()
    print(f"  MongoDB: {result.upserted_count} inserted, {result.modified_count} updated.")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY not set. Copy .env.example → .env and fill it in.")
        sys.exit(1)

    print("── Step 1: Fetching anime catalog from AniList ─────────────────")
    anime_list = fetch_catalog()
    print(f"Fetched {len(anime_list)} unique anime.")

    print("\n── Step 2: Building embedding strings ──────────────────────────")
    texts = [build_embed_text(a) for a in anime_list]

    print("\n── Step 3: Embedding via OpenAI ────────────────────────────────")
    provider = OpenAIEmbeddingProviderSync()
    vectors = embed_all(texts, provider)
    print(f"Got {len(vectors)} vectors (dim={len(vectors[0])}).")

    print("\n── Step 4: Building FAISS index ────────────────────────────────")
    index = build_faiss_index(vectors)
    faiss_path = DATA_DIR / "anime.faiss"
    faiss.write_index(index, str(faiss_path))
    print(f"Saved → {faiss_path}  ({index.ntotal} vectors, dim={index.d})")

    print("\n── Step 5: Saving metadata ─────────────────────────────────────")
    meta = build_meta(anime_list, texts)
    meta_path = DATA_DIR / "anime_meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved → {meta_path}")

    if MONGODB_URI:
        print("\n── Step 6: Upserting to MongoDB ────────────────────────────────")
        import asyncio
        asyncio.run(_upsert_mongodb(meta))
    else:
        print("\nMONGODB_URI not set — skipping MongoDB upsert.")

    print("\n✓ Index build complete!")
    print("Run the sanity check:")
    print('  uv run python -m scripts.sanity_check "calm slice-of-life with great art"')


if __name__ == "__main__":
    main()

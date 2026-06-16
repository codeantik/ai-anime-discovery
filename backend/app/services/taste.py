"""Compute a personal taste vector from the user's MAL history."""

import logging

import faiss
import numpy as np

from app.core import index as idx_store
from app.core.mal_client import get_anime_list

logger = logging.getLogger(__name__)


async def get_taste_vector(access_token: str) -> np.ndarray | None:
    """
    Fetch user's completed+scored MAL list, find each title in the FAISS index
    by title match, then return a score-weighted centroid of their embeddings.
    Returns None if no matching anime are found.
    """
    try:
        mal_list = await get_anime_list(access_token, limit=100)
    except Exception as e:
        logger.warning(f"Could not fetch MAL list for taste vector: {e}")
        return None

    if not mal_list:
        return None

    index, meta = idx_store.load_index()

    # Build a lowercase-title → faiss_idx lookup
    title_to_idx: dict[str, int] = {}
    for faiss_idx_str, anime in meta.items():
        title = (anime.get("title") or anime.get("title_romaji") or "").lower().strip()
        if title:
            title_to_idx[title] = int(faiss_idx_str)
        romaji = (anime.get("title_romaji") or "").lower().strip()
        if romaji and romaji not in title_to_idx:
            title_to_idx[romaji] = int(faiss_idx_str)

    vectors: list[np.ndarray] = []
    weights: list[float] = []

    for item in mal_list:
        title_lower = item["title"].lower().strip()
        faiss_idx = title_to_idx.get(title_lower)
        if faiss_idx is None:
            continue
        vec = index.reconstruct(faiss_idx)
        vectors.append(vec)
        weights.append(max(item["score"], 1) / 10.0)  # 1-10 → 0.1-1.0

    if not vectors:
        logger.info("No FAISS matches found for user's MAL history.")
        return None

    logger.info(f"Taste vector built from {len(vectors)} matched anime.")
    centroid = np.average(vectors, axis=0, weights=weights).astype(np.float32)
    norm = np.linalg.norm(centroid)
    if norm > 0:
        centroid /= norm
    return centroid

"""Compute a personal taste vector from the user's AniList watch history."""

import logging

import numpy as np

from app.core import index as idx_store
from app.core.anilist_client import get_completed_list

logger = logging.getLogger(__name__)


async def get_taste_vector(access_token: str, user_id: int) -> np.ndarray | None:
    """
    Fetch user's completed+scored AniList anime, look each up directly by
    anilist_id in the FAISS index, and return a score-weighted centroid.
    Returns None if no matches found.
    """
    try:
        entries = await get_completed_list(access_token, user_id)
    except Exception as e:
        logger.warning(f"Could not fetch AniList history for taste vector: {e}")
        return None

    if not entries:
        return None

    index, _ = idx_store.load_index()

    vectors: list[np.ndarray] = []
    weights: list[float] = []

    for entry in entries:
        faiss_idx = idx_store.get_faiss_idx_by_anilist_id(entry["anilist_id"])
        if faiss_idx is None:
            continue
        vec = index.reconstruct(faiss_idx)
        vectors.append(vec)
        weights.append(entry["score"] / 10.0)

    if not vectors:
        logger.info("No FAISS matches found for user's AniList history.")
        return None

    logger.info(f"Taste vector built from {len(vectors)} matched anime.")
    centroid = np.average(vectors, axis=0, weights=weights).astype(np.float32)
    norm = np.linalg.norm(centroid)
    return (centroid / norm) if norm > 0 else None

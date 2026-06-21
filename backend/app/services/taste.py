"""Compute a personal taste vector from AniList watch history + explicit thumbs feedback."""

import logging

import numpy as np

from app.core import cache
from app.core import index as idx_store
from app.core.anilist_client import get_completed_list
from app.services.feedback import get_feedback_map

logger = logging.getLogger(__name__)

# Explicit thumbs feedback is a stronger signal than an implicit AniList score
# (max weight 1.0), so it gets outsized influence over the centroid direction.
FEEDBACK_WEIGHT = 2.5

TASTE_CACHE_TTL = 120  # seconds


def _cache_key(user_id: int) -> str:
    return f"taste:{user_id}"


async def get_taste_vector(access_token: str, user_id: int) -> np.ndarray | None:
    """
    Builds a centroid from the user's completed+scored AniList anime, nudged by
    any thumbs up/down feedback (liked anime pull the centroid toward them,
    disliked anime push it away). Returns None if there's no signal at all.

    Cached per user for TASTE_CACHE_TTL seconds — recomputing this hits the AniList
    API and reconstructs every matched FAISS vector, which is wasteful when a user
    submits the form or sends several chat messages back-to-back in one session.
    """
    cache_key = _cache_key(user_id)
    cached = cache.get(cache_key)
    if cached is not cache.MISSING:
        return cached

    vec = await _compute_taste_vector(access_token, user_id)
    cache.set(cache_key, vec, ttl=TASTE_CACHE_TTL)
    return vec


async def _compute_taste_vector(access_token: str, user_id: int) -> np.ndarray | None:
    try:
        entries = await get_completed_list(access_token, user_id)
    except Exception as e:
        logger.warning(f"Could not fetch AniList history for taste vector: {e}")
        entries = []

    index, _ = idx_store.load_index()
    weighted_sum = np.zeros(index.d, dtype=np.float32)
    matched = 0

    for entry in entries:
        faiss_idx = idx_store.get_faiss_idx_by_anilist_id(entry["anilist_id"])
        if faiss_idx is None:
            continue
        vec = index.reconstruct(faiss_idx)
        weighted_sum += (entry["score"] / 10.0) * vec
        matched += 1

    feedback = await get_feedback_map(user_id)
    for anilist_id, signal in feedback.items():
        faiss_idx = idx_store.get_faiss_idx_by_anilist_id(anilist_id)
        if faiss_idx is None:
            continue
        vec = index.reconstruct(faiss_idx)
        weighted_sum += signal * FEEDBACK_WEIGHT * vec
        matched += 1

    if matched == 0:
        logger.info("No taste signal (history or feedback) found for user.")
        return None

    logger.info(f"Taste vector built from {matched} signals ({len(feedback)} feedback).")
    norm = np.linalg.norm(weighted_sum)
    return (weighted_sum / norm) if norm > 0 else None

"""Taste profile — genre/tag breakdown of a user's taste, computed from the same
AniList history + thumbs feedback that drives the taste-vector centroid (see taste.py),
just aggregated by genre/tag instead of by embedding.
"""

import logging

from app.core import cache
from app.core.anilist_client import get_completed_list
from app.core.index import get_anime, get_faiss_idx_by_anilist_id
from app.services.feedback import get_feedback_map
from app.services.taste import FEEDBACK_WEIGHT, TASTE_CACHE_TTL

logger = logging.getLogger(__name__)

TOP_GENRES = 8
TOP_TAGS = 12


def _cache_key(user_id: int) -> str:
    return f"profile:{user_id}"


def _top_normalized(weights: dict[str, float], top_n: int) -> list[dict]:
    liked = {name: w for name, w in weights.items() if w > 0}
    total = sum(liked.values())
    if total <= 0:
        return []
    ranked = sorted(liked.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    return [{"name": name, "weight": w / total} for name, w in ranked]


async def get_taste_profile(access_token: str, user_id: int) -> dict | None:
    """
    Returns {"genres": [...], "tags": [...]} with normalized weights, or None if
    there's no taste signal (history or feedback) at all. Cached per user for
    TASTE_CACHE_TTL seconds (same window as the taste vector, invalidated together
    on feedback changes) since this also fetches AniList history.
    """
    cache_key = _cache_key(user_id)
    cached = cache.get(cache_key)
    if cached is not cache.MISSING:
        return cached

    profile = await _compute_taste_profile(access_token, user_id)
    cache.set(cache_key, profile, ttl=TASTE_CACHE_TTL)
    return profile


async def _compute_taste_profile(access_token: str, user_id: int) -> dict | None:
    try:
        entries = await get_completed_list(access_token, user_id)
    except Exception as e:
        logger.warning(f"Could not fetch AniList history for taste profile: {e}")
        entries = []

    genre_weights: dict[str, float] = {}
    tag_weights: dict[str, float] = {}
    matched = 0

    def _accumulate(anilist_id: int, weight: float) -> bool:
        faiss_idx = get_faiss_idx_by_anilist_id(anilist_id)
        if faiss_idx is None:
            return False
        anime = get_anime(faiss_idx)
        if anime is None:
            return False
        for genre in anime.get("genres", []):
            genre_weights[genre] = genre_weights.get(genre, 0.0) + weight
        for tag in anime.get("tags", []):
            tag_weights[tag] = tag_weights.get(tag, 0.0) + weight
        return True

    for entry in entries:
        if _accumulate(entry["anilist_id"], entry["score"] / 10.0):
            matched += 1

    feedback = await get_feedback_map(user_id)
    for anilist_id, signal in feedback.items():
        if _accumulate(anilist_id, signal * FEEDBACK_WEIGHT):
            matched += 1

    if matched == 0:
        logger.info("No taste signal (history or feedback) found for taste profile.")
        return None

    return {
        "genres": _top_normalized(genre_weights, TOP_GENRES),
        "tags": _top_normalized(tag_weights, TOP_TAGS),
    }

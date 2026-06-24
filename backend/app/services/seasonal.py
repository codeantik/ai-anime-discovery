"""Seasonal / new-release radar — live AniList lookup of the current season's airing or
upcoming anime (the catalog stores neither season nor status), intersected with the catalog
and ranked by taste-vector dot product for logged-in users or by mean_score otherwise.
"""

import logging
from datetime import UTC, datetime

import numpy as np

from app.core import cache
from app.core.anilist_client import get_seasonal_anime
from app.core.index import get_anime, get_faiss_idx_by_anilist_id, get_vector

logger = logging.getLogger(__name__)

# Live AniList season data changes slowly (new airing slots, status flips) — safe to
# cache for hours rather than refetching on every request.
SEASONAL_CACHE_TTL = 6 * 60 * 60

RADAR_STATUSES = {"RELEASING", "NOT_YET_RELEASED"}
MAX_RESULTS = 24


def current_season() -> tuple[str, int]:
    """AniList season convention: WINTER=Jan-Mar, SPRING=Apr-Jun, SUMMER=Jul-Sep, FALL=Oct-Dec."""
    now = datetime.now(UTC)
    if now.month <= 3:
        season = "WINTER"
    elif now.month <= 6:
        season = "SPRING"
    elif now.month <= 9:
        season = "SUMMER"
    else:
        season = "FALL"
    return season, now.year


async def _get_live_seasonal(season: str, year: int) -> list[dict]:
    cache_key = f"seasonal:{season}:{year}"
    cached = cache.get(cache_key)
    if cached is not cache.MISSING:
        return cached

    try:
        live = await get_seasonal_anime(season, year)
    except Exception as e:
        logger.warning(f"Could not fetch seasonal anime from AniList: {e}")
        live = []
    cache.set(cache_key, live, ttl=SEASONAL_CACHE_TTL)
    return live


async def get_seasonal(taste_vec: np.ndarray | None) -> dict:
    """
    Returns {"season", "year", "anime", "personalized"} — "anime" entries are catalog
    metadata dicts with "similarity" and "recommended_because" already filled in, ready
    to drop straight into AnimeRecommendation.
    """
    season, year = current_season()
    live = await _get_live_seasonal(season, year)

    matched: list[dict] = []
    for entry in live:
        if entry.get("status") not in RADAR_STATUSES:
            continue
        faiss_idx = get_faiss_idx_by_anilist_id(entry["id"])
        if faiss_idx is None:
            continue
        anime = get_anime(faiss_idx)
        if anime is None:
            continue
        matched.append({**anime, "status": entry["status"]})

    personalized = taste_vec is not None
    scored: list[tuple[dict, float]] = []
    for anime in matched:
        if personalized:
            vec = get_vector(anime["anilist_id"])
            raw = float(np.dot(taste_vec, vec)) if vec is not None else -1.0
        else:
            raw = (anime.get("mean_score") or 0) / 100
        scored.append((anime, raw))
    scored.sort(key=lambda pair: pair[1], reverse=True)

    recommendations = []
    for anime, raw in scored[:MAX_RESULTS]:
        because = (
            "Premiering soon this season."
            if anime["status"] == "NOT_YET_RELEASED"
            else "Currently airing this season."
        )
        recommendations.append(
            {**anime, "similarity": max(0.0, min(1.0, raw)), "recommended_because": because}
        )

    return {"season": season, "year": year, "anime": recommendations, "personalized": personalized}

"""Watchlist endpoints — save anime for later (private, separate from AniList/MAL list pushes)."""

import numpy as np
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.core.auth import CurrentUser, get_current_user
from app.core.index import get_anime, get_faiss_idx_by_anilist_id, get_vector
from app.models.recommend import AnimeRecommendation
from app.services.taste import get_taste_vector
from app.services.watchlist import add_bookmark, get_watchlist_ids, remove_bookmark

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


class AddBookmarkRequest(BaseModel):
    anilist_id: int


@router.get("")
async def list_watchlist(
    sort: str = Query("added", pattern="^(added|taste)$"),
    user: CurrentUser = Depends(get_current_user),
) -> list[AnimeRecommendation]:
    ids = await get_watchlist_ids(user.id)

    taste_vec = None
    if sort == "taste":
        taste_vec = await get_taste_vector(user.access_token, user.id)
        if taste_vec is not None:
            ids = sorted(
                ids,
                key=lambda anilist_id: _taste_score(taste_vec, anilist_id),
                reverse=True,
            )

    out: list[AnimeRecommendation] = []
    for anilist_id in ids:
        faiss_idx = get_faiss_idx_by_anilist_id(anilist_id)
        if faiss_idx is None:
            continue
        anime = get_anime(faiss_idx)
        if not anime:
            continue
        out.append(
            AnimeRecommendation(
                anilist_id=anime["anilist_id"],
                title=anime.get("title") or anime.get("title_romaji") or "Unknown",
                title_romaji=anime.get("title_romaji"),
                synopsis=anime.get("synopsis") or "",
                genres=anime.get("genres") or [],
                tags=anime.get("tags") or [],
                year=anime.get("year"),
                format=anime.get("format"),
                mean_score=anime.get("mean_score"),
                episodes=anime.get("episodes"),
                cover_image=anime.get("cover_image"),
                recommended_because="",
                similarity=1.0,
            )
        )
    return out


def _taste_score(taste_vec: np.ndarray, anilist_id: int) -> float:
    anime_vec = get_vector(anilist_id)
    return float(np.dot(taste_vec, anime_vec)) if anime_vec is not None else float("-inf")


@router.post("/add")
async def add_to_watchlist(
    body: AddBookmarkRequest,
    user: CurrentUser = Depends(get_current_user),
) -> dict:
    await add_bookmark(user.id, body.anilist_id)
    return {"status": "added", "anilist_id": body.anilist_id}


@router.delete("/{anilist_id}")
async def remove_from_watchlist(
    anilist_id: int,
    user: CurrentUser = Depends(get_current_user),
) -> dict:
    await remove_bookmark(user.id, anilist_id)
    return {"status": "removed", "anilist_id": anilist_id}

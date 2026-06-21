"""Shareable links — public read-only views of a single recommendation card or a watchlist."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.auth import CurrentUser, get_current_user
from app.core.index import get_anime, get_faiss_idx_by_anilist_id
from app.models.recommend import AnimeRecommendation, SharedResponse
from app.services.shares import create_card_share, create_watchlist_share, get_share
from app.services.watchlist import get_watchlist_ids

router = APIRouter(prefix="/api/share", tags=["share"])


class CreateCardShareRequest(BaseModel):
    anilist_id: int
    recommended_because: str = ""


def _to_recommendation(anime: dict, recommended_because: str) -> AnimeRecommendation:
    return AnimeRecommendation(
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
        recommended_because=recommended_because,
        similarity=1.0,
    )


@router.post("/card")
async def share_card(
    body: CreateCardShareRequest,
    user: CurrentUser = Depends(get_current_user),
) -> dict:
    token = await create_card_share(user.id, body.anilist_id, body.recommended_because)
    if token is None:
        raise HTTPException(500, "Failed to create share link.")
    return {"token": token}


@router.post("/watchlist")
async def share_watchlist(user: CurrentUser = Depends(get_current_user)) -> dict:
    token = await create_watchlist_share(user.id)
    if token is None:
        raise HTTPException(500, "Failed to create share link.")
    return {"token": token}


@router.get("/{token}")
async def get_shared(token: str) -> SharedResponse:
    share = await get_share(token)
    if not share:
        raise HTTPException(404, "This share link is invalid or has expired.")

    if share["type"] == "card":
        faiss_idx = get_faiss_idx_by_anilist_id(share["anilist_id"])
        anime = get_anime(faiss_idx) if faiss_idx is not None else None
        if not anime:
            raise HTTPException(404, "This shared anime is no longer available.")
        return SharedResponse(
            type="card",
            anime=[_to_recommendation(anime, share.get("recommended_because") or "")],
        )

    ids = await get_watchlist_ids(share["owner_id"])
    out: list[AnimeRecommendation] = []
    for anilist_id in ids:
        faiss_idx = get_faiss_idx_by_anilist_id(anilist_id)
        if faiss_idx is None:
            continue
        anime = get_anime(faiss_idx)
        if not anime:
            continue
        out.append(_to_recommendation(anime, ""))
    return SharedResponse(type="watchlist", anime=out)

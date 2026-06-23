import numpy as np
from fastapi import APIRouter, Depends, HTTPException

from app.core import anilist_client
from app.core.auth import CurrentUser, get_optional_user
from app.core.index import get_anime, get_faiss_idx_by_anilist_id, get_similar, get_vector
from app.models.recommend import AnimeDetail, AnimeRecommendation, Character, Trailer
from app.services.taste import get_taste_vector

router = APIRouter(prefix="/api", tags=["anime"])


@router.get("/anime/{anilist_id}/similar", response_model=list[AnimeRecommendation])
async def similar_anime(anilist_id: int, k: int = 8) -> list[AnimeRecommendation]:
    faiss_idx = get_faiss_idx_by_anilist_id(anilist_id)
    if faiss_idx is None:
        return []

    out: list[AnimeRecommendation] = []
    for idx, score in get_similar(faiss_idx, top_k=k):
        anime = get_anime(idx)
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
                similarity=score,
            )
        )
    return out


@router.get("/anime/{anilist_id}", response_model=AnimeDetail)
async def anime_detail(
    anilist_id: int,
    user: CurrentUser | None = Depends(get_optional_user),
) -> AnimeDetail:
    local = None
    faiss_idx = get_faiss_idx_by_anilist_id(anilist_id)
    if faiss_idx is not None:
        local = get_anime(faiss_idx)

    try:
        live = await anilist_client.get_anime_detail(anilist_id)
    except Exception:
        live = None
    if local is None and live is None:
        raise HTTPException(status_code=404, detail="Anime not found")

    title = (local or {}).get("title")
    title_romaji = (local or {}).get("title_romaji")
    synopsis = (local or {}).get("synopsis")
    genres = (local or {}).get("genres", [])
    tags = (local or {}).get("tags", [])
    year = (local or {}).get("year")
    fmt = (local or {}).get("format")
    mean_score = (local or {}).get("mean_score")
    episodes = (local or {}).get("episodes")
    cover_image = (local or {}).get("cover_image")

    status = None
    duration = None
    source = None
    banner_image = None
    studios: list[str] = []
    trailer = None
    characters: list[Character] = []

    if live:
        title = title or live["title"].get("english") or live["title"].get("romaji")
        title_romaji = title_romaji or live["title"].get("romaji")
        synopsis = synopsis or (live.get("description") or "").strip()
        genres = genres or (live.get("genres") or [])
        tags = tags or [
            t["name"] for t in (live.get("tags") or []) if not t.get("isGeneralSpoiler")
        ]
        year = year or (live.get("startDate") or {}).get("year")
        fmt = fmt or live.get("format")
        mean_score = mean_score or live.get("meanScore") or live.get("averageScore")
        episodes = episodes or live.get("episodes")
        cover_image = cover_image or (live.get("coverImage") or {}).get("extraLarge") or (live.get("coverImage") or {}).get("large")
        status = live.get("status")
        duration = live.get("duration")
        source = live.get("source")
        banner_image = live.get("bannerImage")
        studios = [s["name"] for s in (live.get("studios") or {}).get("nodes", [])]
        if live.get("trailer") and live["trailer"].get("site") and live["trailer"].get("id"):
            trailer = Trailer(site=live["trailer"]["site"], id=live["trailer"]["id"])
        characters = [
            Character(name=c["name"]["full"], image=(c.get("image") or {}).get("medium"))
            for c in (live.get("characters") or {}).get("nodes", [])
        ]

    taste_match = None
    if user is not None:
        taste_vec = await get_taste_vector(user.access_token, user.id)
        anime_vec = get_vector(anilist_id)
        if taste_vec is not None and anime_vec is not None:
            taste_match = max(0.0, min(1.0, float(np.dot(taste_vec, anime_vec))))

    return AnimeDetail(
        anilist_id=anilist_id,
        title=title or "",
        title_romaji=title_romaji,
        synopsis=synopsis or "",
        genres=genres,
        tags=tags,
        year=year,
        format=fmt,
        status=status,
        mean_score=mean_score,
        episodes=episodes,
        duration=duration,
        source=source,
        cover_image=cover_image,
        banner_image=banner_image,
        studios=studios,
        trailer=trailer,
        characters=characters,
        taste_match=taste_match,
    )

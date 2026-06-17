from fastapi import APIRouter, HTTPException

from app.core import anilist_client
from app.core.index import get_anime, get_faiss_idx_by_anilist_id
from app.models.recommend import AnimeDetail, Character, Trailer

router = APIRouter(prefix="/api", tags=["anime"])


@router.get("/anime/{anilist_id}", response_model=AnimeDetail)
async def anime_detail(anilist_id: int) -> AnimeDetail:
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
    )

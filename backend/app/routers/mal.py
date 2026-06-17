"""MAL list endpoints — add anime, fetch user list."""

from fastapi import APIRouter, Cookie, HTTPException
from pydantic import BaseModel

from app.core.mal_client import get_mal_id_from_anilist, update_anime_status

router = APIRouter(prefix="/api/mal", tags=["mal"])


class AddAnimeRequest(BaseModel):
    anilist_id: int
    status: str = "plan_to_watch"  # plan_to_watch | watching | completed | dropped


@router.post("/add")
async def add_to_mal(
    body: AddAnimeRequest,
    mal_access_token: str | None = Cookie(default=None),
) -> dict:
    if not mal_access_token:
        raise HTTPException(401, "Please connect your MyAnimeList account first.")

    mal_id = await get_mal_id_from_anilist(body.anilist_id)
    if not mal_id:
        raise HTTPException(404, f"Could not find MAL ID for AniList anime {body.anilist_id}.")

    result = await update_anime_status(mal_access_token, mal_id, body.status)
    return {"status": result.get("status"), "mal_id": mal_id}

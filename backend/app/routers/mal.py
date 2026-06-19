"""MAL list endpoints — add anime, fetch user list."""

from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel

from app.core.mal_client import get_mal_id_from_anilist, get_user_info, refresh_access_token, update_anime_status
from app.routers.mal_auth import _clear_token_cookies, _set_token_cookies

router = APIRouter(prefix="/api/mal", tags=["mal"])


class AddAnimeRequest(BaseModel):
    anilist_id: int
    status: str = "plan_to_watch"  # plan_to_watch | watching | completed | dropped


@router.post("/add")
async def add_to_mal(
    body: AddAnimeRequest,
    response: Response,
    mal_access_token: str | None = Cookie(default=None),
    mal_refresh_token: str | None = Cookie(default=None),
) -> dict:
    if not mal_access_token:
        raise HTTPException(401, "Please connect your MyAnimeList account first.")

    mal_id = await get_mal_id_from_anilist(body.anilist_id)
    if not mal_id:
        raise HTTPException(404, f"Could not find MAL ID for AniList anime {body.anilist_id}.")

    try:
        result = await update_anime_status(mal_access_token, mal_id, body.status)
    except Exception:
        if not mal_refresh_token:
            raise HTTPException(401, "Session expired — please reconnect MyAnimeList.")
        try:
            tokens = await refresh_access_token(mal_refresh_token)
        except Exception:
            _clear_token_cookies(response)
            raise HTTPException(401, "Session expired — please reconnect MyAnimeList.")
        result = await update_anime_status(tokens["access_token"], mal_id, body.status)
        user = await get_user_info(tokens["access_token"])
        _set_token_cookies(response, tokens["access_token"], tokens["refresh_token"], user["id"])

    return {"status": result.get("status"), "mal_id": mal_id}

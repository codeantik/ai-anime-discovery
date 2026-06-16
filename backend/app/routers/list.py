"""AniList list endpoints — add anime to user's list."""

from fastapi import APIRouter, Cookie, HTTPException
from pydantic import BaseModel

from app.core.anilist_client import save_list_entry

router = APIRouter(prefix="/api/list", tags=["list"])


class AddAnimeRequest(BaseModel):
    anilist_id: int
    status: str = "PLANNING"  # PLANNING | CURRENT | COMPLETED | DROPPED | PAUSED | REPEATING


@router.post("/add")
async def add_to_list(
    body: AddAnimeRequest,
    al_access_token: str | None = Cookie(default=None),
) -> dict:
    if not al_access_token:
        raise HTTPException(401, "Please connect your AniList account first.")
    result = await save_list_entry(al_access_token, body.anilist_id, body.status)
    return {"status": result.get("status"), "anilist_id": body.anilist_id}

"""AniList list endpoints — add anime to user's list."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.anilist_client import save_list_entry
from app.core.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/api/list", tags=["list"])


class AddAnimeRequest(BaseModel):
    anilist_id: int
    status: str = "PLANNING"  # PLANNING | CURRENT | COMPLETED | DROPPED | PAUSED | REPEATING


@router.post("/add")
async def add_to_list(
    body: AddAnimeRequest,
    user: CurrentUser = Depends(get_current_user),
) -> dict:
    result = await save_list_entry(user.access_token, body.anilist_id, body.status)
    return {"status": result.get("status"), "anilist_id": body.anilist_id}

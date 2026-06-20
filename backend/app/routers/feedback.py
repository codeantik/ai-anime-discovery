"""Thumbs up/down feedback endpoints — refines the personal taste vector over time."""

from fastapi import APIRouter, Cookie, HTTPException

from app.models.feedback import FeedbackRequest
from app.services.feedback import get_feedback_map, set_feedback

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


def _require_user_id(al_user_id: str | None) -> int:
    if not al_user_id:
        raise HTTPException(401, "Please connect your AniList account first.")
    return int(al_user_id)


@router.get("")
async def list_feedback(al_user_id: str | None = Cookie(default=None)) -> dict[int, int]:
    user_id = _require_user_id(al_user_id)
    return await get_feedback_map(user_id)


@router.post("")
async def post_feedback(
    body: FeedbackRequest,
    al_user_id: str | None = Cookie(default=None),
) -> dict:
    user_id = _require_user_id(al_user_id)
    await set_feedback(user_id, body.anilist_id, body.signal)
    return {"status": "ok", "anilist_id": body.anilist_id, "signal": body.signal}

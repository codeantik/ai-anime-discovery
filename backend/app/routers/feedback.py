"""Thumbs up/down feedback endpoints — refines the personal taste vector over time."""

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_current_user
from app.models.feedback import FeedbackRequest
from app.services.feedback import get_feedback_map, set_feedback

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.get("")
async def list_feedback(user: CurrentUser = Depends(get_current_user)) -> dict[int, int]:
    return await get_feedback_map(user.id)


@router.post("")
async def post_feedback(
    body: FeedbackRequest,
    user: CurrentUser = Depends(get_current_user),
) -> dict:
    await set_feedback(user.id, body.anilist_id, body.signal)
    return {"status": "ok", "anilist_id": body.anilist_id, "signal": body.signal}

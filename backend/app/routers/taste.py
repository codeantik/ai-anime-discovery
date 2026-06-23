"""Taste profile endpoints — genre/tag breakdown of a user's taste."""

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_optional_user
from app.models.recommend import TasteProfileResponse
from app.services.profile import get_taste_profile

router = APIRouter(prefix="/api/taste", tags=["taste"])


@router.get("/profile")
async def read_taste_profile(
    user: CurrentUser | None = Depends(get_optional_user),
) -> TasteProfileResponse:
    if user is None:
        return TasteProfileResponse(available=False)

    profile = await get_taste_profile(user.access_token, user.id)
    if profile is None:
        return TasteProfileResponse(available=False)

    return TasteProfileResponse(available=True, genres=profile["genres"], tags=profile["tags"])

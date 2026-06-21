"""Personalized 'new for you' digest endpoints."""

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_current_user, get_optional_user
from app.models.recommend import DigestResponse
from app.services.digest import get_digest, mark_viewed

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.get("")
async def read_digest(user: CurrentUser | None = Depends(get_optional_user)) -> DigestResponse:
    if user is None:
        return DigestResponse(available=False)

    doc = await get_digest(user.id, user.access_token)
    if doc is None:
        return DigestResponse(available=False)

    return DigestResponse(
        available=True,
        recommendations=doc["recommendations"],
        generated_at=doc["generated_at"],
        viewed=doc["viewed"],
    )


@router.post("/viewed")
async def viewed(user: CurrentUser = Depends(get_current_user)) -> dict:
    await mark_viewed(user.id)
    return {"status": "ok"}

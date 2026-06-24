"""Friend/group combined recommendations endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_current_user, get_optional_user
from app.models.recommend import DuoResponse
from app.services.duo import create_duo_invite, get_duo_recommendations

router = APIRouter(prefix="/api/duo", tags=["duo"])


@router.post("/invite")
async def invite(user: CurrentUser = Depends(get_current_user)) -> dict:
    token = await create_duo_invite(user.id, user.access_token)
    if token is None:
        raise HTTPException(
            400, "Build some taste signal first — rate a few anime or sync your AniList history."
        )
    return {"token": token}


@router.get("/{token}")
async def read_duo(
    token: str, guest: CurrentUser | None = Depends(get_optional_user)
) -> DuoResponse:
    result = await get_duo_recommendations(
        token,
        guest.id if guest else None,
        guest.access_token if guest else None,
    )
    if result is None:
        raise HTTPException(404, "This invite link is invalid or has expired.")
    return DuoResponse(combined=result["combined"], recommendations=result["recommendations"])

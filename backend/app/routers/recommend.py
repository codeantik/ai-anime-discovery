from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_optional_user
from app.models.recommend import RecommendRequest, RecommendResponse
from app.services import recommend as svc
from app.services.taste import get_taste_vector

router = APIRouter(prefix="/api", tags=["recommend"])


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(
    prefs: RecommendRequest,
    user: CurrentUser | None = Depends(get_optional_user),
) -> RecommendResponse:
    try:
        taste_vec = None
        if user is not None:
            taste_vec = await get_taste_vector(user.access_token, user.id)
        return await svc.recommend(prefs, taste_vec=taste_vec, user_id=user.id if user else None)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")

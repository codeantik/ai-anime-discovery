from fastapi import APIRouter, Cookie, HTTPException

from app.models.recommend import RecommendRequest, RecommendResponse
from app.services import recommend as svc
from app.services.taste import get_taste_vector

router = APIRouter(prefix="/api", tags=["recommend"])


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(
    prefs: RecommendRequest,
    al_access_token: str | None = Cookie(default=None),
    al_user_id: str | None = Cookie(default=None),
) -> RecommendResponse:
    try:
        taste_vec = None
        if al_access_token and al_user_id:
            taste_vec = await get_taste_vector(al_access_token, int(al_user_id))
        return await svc.recommend(prefs, taste_vec=taste_vec)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")

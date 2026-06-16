from fastapi import APIRouter, HTTPException

from app.models.recommend import RecommendRequest, RecommendResponse
from app.services import recommend as svc

router = APIRouter(prefix="/api", tags=["recommend"])


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(prefs: RecommendRequest) -> RecommendResponse:
    try:
        return await svc.recommend(prefs)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")

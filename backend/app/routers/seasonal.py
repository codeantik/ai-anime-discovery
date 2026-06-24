"""Seasonal / new-release radar endpoint."""

from fastapi import APIRouter, Depends

from app.core.auth import CurrentUser, get_optional_user
from app.models.recommend import AnimeRecommendation, SeasonalResponse
from app.services.seasonal import get_seasonal
from app.services.taste import get_taste_vector

router = APIRouter(prefix="/api/seasonal", tags=["seasonal"])


@router.get("")
async def read_seasonal(user: CurrentUser | None = Depends(get_optional_user)) -> SeasonalResponse:
    taste_vec = await get_taste_vector(user.access_token, user.id) if user is not None else None
    result = await get_seasonal(taste_vec)

    anime = [
        AnimeRecommendation(
            anilist_id=a["anilist_id"],
            title=a.get("title") or a.get("title_romaji") or "Unknown",
            title_romaji=a.get("title_romaji"),
            synopsis=a.get("synopsis") or "",
            genres=a.get("genres") or [],
            tags=a.get("tags") or [],
            year=a.get("year"),
            format=a.get("format"),
            mean_score=a.get("mean_score"),
            episodes=a.get("episodes"),
            cover_image=a.get("cover_image"),
            recommended_because=a["recommended_because"],
            similarity=a["similarity"],
        )
        for a in result["anime"]
    ]
    return SeasonalResponse(
        season=result["season"], year=result["year"], anime=anime, personalized=result["personalized"]
    )

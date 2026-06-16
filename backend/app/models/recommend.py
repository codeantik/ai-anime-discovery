from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    genres: list[str] = []
    mood: str = ""
    themes: list[str] = []
    era: str = ""       # "any" | "classic" | "2000s" | "2010s" | "recent"
    length: str = ""    # "any" | "movie" | "short" | "season" | "long"
    loved_titles: list[str] = []


class AnimeRecommendation(BaseModel):
    anilist_id: int
    title: str
    title_romaji: str | None = None
    synopsis: str
    genres: list[str]
    tags: list[str]
    year: int | None = None
    format: str | None = None
    mean_score: int | None = None
    episodes: int | None = None
    cover_image: str | None = None
    recommended_because: str
    similarity: float = Field(ge=0.0, le=1.0)


class RecommendResponse(BaseModel):
    recommendations: list[AnimeRecommendation]
    query_used: str
    total_candidates: int

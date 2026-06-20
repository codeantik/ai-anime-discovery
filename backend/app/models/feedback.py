from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    anilist_id: int
    signal: int = Field(ge=-1, le=1)  # 1 = like, -1 = dislike, 0 = clear

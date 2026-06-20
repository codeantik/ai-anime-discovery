from fastapi import APIRouter, Cookie, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_agent import run_chat
from app.services.taste import get_taste_vector

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    al_access_token: str | None = Cookie(default=None),
    al_user_id: str | None = Cookie(default=None),
) -> ChatResponse:
    try:
        taste_vec = None
        user_id = int(al_user_id) if al_user_id else None
        if al_access_token and user_id is not None:
            taste_vec = await get_taste_vector(al_access_token, user_id)

        messages = [m.model_dump() for m in body.messages]
        reply, recommendations = await run_chat(messages, taste_vec=taste_vec, user_id=user_id)
        return ChatResponse(reply=reply, recommendations=recommendations)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import CurrentUser, get_optional_user
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_agent import run_chat
from app.services.taste import get_taste_vector

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    user: CurrentUser | None = Depends(get_optional_user),
) -> ChatResponse:
    try:
        taste_vec = None
        if user is not None:
            taste_vec = await get_taste_vector(user.access_token, user.id)

        messages = [m.model_dump() for m in body.messages]
        reply, recommendations = await run_chat(
            messages, taste_vec=taste_vec, user_id=user.id if user else None
        )
        return ChatResponse(reply=reply, recommendations=recommendations)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

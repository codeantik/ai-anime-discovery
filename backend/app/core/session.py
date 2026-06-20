"""Signed JWT app session — independent of AniList/MAL tokens, proves "who is using the app"."""

from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import SESSION_SECRET

_ALGORITHM = "HS256"
_TTL = timedelta(days=30)


def create_session_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + _TTL,
    }
    return jwt.encode(payload, SESSION_SECRET, algorithm=_ALGORITHM)


def verify_session_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SESSION_SECRET, algorithms=[_ALGORITHM])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")

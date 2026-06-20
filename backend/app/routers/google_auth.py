"""Google OAuth2 sign-in — identity provider only, decoupled from AniList/MAL data links."""

import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, HTTPException, Response
from fastapi.responses import RedirectResponse

from app.core.config import FRONTEND_URL, GOOGLE_CLIENT_ID, GOOGLE_REDIRECT_URI, IS_PRODUCTION
from app.core.google_client import exchange_code, get_user_info
from app.core.session import create_session_token, verify_session_token
from app.services.users import get_or_create_user, get_user

router = APIRouter(prefix="/auth/google", tags=["auth"])

_SESSION_COOKIE = "app_session"
_STATE_COOKIE = "google_oauth_state"
_SESSION_TTL = 30 * 24 * 60 * 60  # matches session.py's JWT TTL
_STATE_TTL = 10 * 60  # just long enough to complete the consent screen


def _cookie_kwargs() -> dict:
    return dict(httponly=True, samesite="lax", secure=True) if IS_PRODUCTION else dict(httponly=True, samesite="lax", secure=False)


@router.get("/login")
async def google_login() -> RedirectResponse:
    state = secrets.token_urlsafe(32)
    params = urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    })
    redirect = RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")
    redirect.set_cookie(_STATE_COOKIE, state, max_age=_STATE_TTL, **_cookie_kwargs())
    return redirect


@router.get("/callback")
async def google_callback(
    code: str,
    state: str,
    google_oauth_state: str | None = Cookie(default=None),
) -> RedirectResponse:
    if not google_oauth_state or state != google_oauth_state:
        raise HTTPException(400, "Invalid OAuth state — please try signing in again.")
    try:
        tokens = await exchange_code(code)
        profile = await get_user_info(tokens["access_token"])
    except Exception as e:
        raise HTTPException(400, f"Token exchange failed: {e}")

    user = await get_or_create_user(
        google_sub=profile["sub"],
        email=profile.get("email", ""),
        name=profile.get("name", profile.get("email", "")),
        picture=profile.get("picture"),
    )
    session_token = create_session_token(user["_id"])

    redirect = RedirectResponse(FRONTEND_URL)
    redirect.delete_cookie(_STATE_COOKIE)
    redirect.set_cookie(_SESSION_COOKIE, session_token, max_age=_SESSION_TTL, **_cookie_kwargs())
    return redirect


@router.post("/logout")
async def google_logout(response: Response) -> dict:
    response.delete_cookie(_SESSION_COOKIE)
    return {"status": "logged out"}


@router.get("/me")
async def google_me(app_session: str | None = Cookie(default=None)) -> dict:
    user_id = verify_session_token(app_session) if app_session else None
    if not user_id:
        raise HTTPException(401, "Not authenticated")
    user = await get_user(user_id)
    if not user:
        raise HTTPException(401, "Not authenticated")
    return {"id": user["_id"], "name": user.get("name"), "email": user.get("email"), "picture": user.get("picture")}

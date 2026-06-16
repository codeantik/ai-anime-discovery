"""MAL OAuth2 PKCE-plain auth endpoints."""

import secrets
import string
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, HTTPException, Response
from fastapi.responses import RedirectResponse

from app.core.config import FRONTEND_URL, MAL_CLIENT_ID, MAL_REDIRECT_URI
from app.core.mal_client import exchange_code, get_user_info, refresh_access_token

router = APIRouter(prefix="/auth/mal", tags=["auth"])

_PKCE_CHARS = string.ascii_letters + string.digits + "-._~"
_ACCESS_COOKIE = "mal_access_token"
_REFRESH_COOKIE = "mal_refresh_token"
_PKCE_COOKIE = "mal_pkce"

# 30 days in seconds
_ACCESS_TTL = 60 * 60  # MAL access tokens last ~1 h; we refresh on 401
_REFRESH_TTL = 30 * 24 * 60 * 60


def _set_token_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    kw = dict(httponly=True, samesite="lax", secure=False)  # secure=True in prod (HTTPS)
    response.set_cookie(_ACCESS_COOKIE, access_token, max_age=_ACCESS_TTL, **kw)
    response.set_cookie(_REFRESH_COOKIE, refresh_token, max_age=_REFRESH_TTL, **kw)


def _clear_token_cookies(response: Response) -> None:
    response.delete_cookie(_ACCESS_COOKIE)
    response.delete_cookie(_REFRESH_COOKIE)


@router.get("/login")
async def mal_login() -> RedirectResponse:
    verifier = "".join(secrets.choice(_PKCE_CHARS) for _ in range(128))
    params = urlencode({
        "response_type": "code",
        "client_id": MAL_CLIENT_ID,
        "redirect_uri": MAL_REDIRECT_URI,
        "code_challenge": verifier,        # PKCE-plain: challenge == verifier
        "code_challenge_method": "plain",
        "state": secrets.token_urlsafe(16),
    })
    redirect = RedirectResponse(f"https://myanimelist.net/v1/oauth2/authorize?{params}")
    redirect.set_cookie(
        _PKCE_COOKIE, verifier,
        max_age=900, httponly=True, samesite="lax", secure=False,
    )
    return redirect


@router.get("/callback")
async def mal_callback(
    code: str,
    mal_pkce: str | None = Cookie(default=None),
) -> RedirectResponse:
    if not mal_pkce:
        raise HTTPException(400, "Missing PKCE verifier cookie — try logging in again.")

    tokens = await exchange_code(code, mal_pkce)

    redirect = RedirectResponse(FRONTEND_URL)
    _set_token_cookies(redirect, tokens["access_token"], tokens["refresh_token"])
    redirect.delete_cookie(_PKCE_COOKIE)
    return redirect


@router.post("/logout")
async def mal_logout(response: Response) -> dict:
    _clear_token_cookies(response)
    return {"status": "logged out"}


@router.get("/me", operation_id="mal_me")
async def mal_me(
    mal_access_token: str | None = Cookie(default=None),
    mal_refresh_token: str | None = Cookie(default=None),
    response: Response = None,  # type: ignore[assignment]
) -> dict:
    if not mal_access_token:
        raise HTTPException(401, "Not authenticated")

    try:
        user = await get_user_info(mal_access_token)
    except Exception:
        # Try token refresh
        if not mal_refresh_token:
            raise HTTPException(401, "Session expired")
        try:
            tokens = await refresh_access_token(mal_refresh_token)
            _set_token_cookies(response, tokens["access_token"], tokens["refresh_token"])
            user = await get_user_info(tokens["access_token"])
        except Exception:
            _clear_token_cookies(response)
            raise HTTPException(401, "Session expired — please log in again.")

    return {"id": user["id"], "name": user["name"], "picture": user.get("picture")}

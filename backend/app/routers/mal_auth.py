"""MAL OAuth2 auth endpoints — PKCE with code_challenge_method=plain."""

import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, HTTPException, Response
from fastapi.responses import RedirectResponse

from app.core.config import FRONTEND_URL, IS_PRODUCTION, MAL_CLIENT_ID, MAL_REDIRECT_URI
from app.core.mal_client import exchange_code, get_user_info, refresh_access_token

router = APIRouter(prefix="/auth/mal", tags=["auth"])

_ACCESS_COOKIE = "mal_access_token"
_REFRESH_COOKIE = "mal_refresh_token"
_USER_ID_COOKIE = "mal_user_id"
_VERIFIER_COOKIE = "mal_code_verifier"
_TOKEN_TTL = 30 * 24 * 60 * 60  # MAL refresh tokens last ~1 month
_VERIFIER_TTL = 10 * 60  # just long enough to complete the consent screen


def _cookie_kwargs() -> dict:
    return dict(httponly=True, samesite="lax", secure=True) if IS_PRODUCTION else dict(httponly=True, samesite="lax", secure=False)


def _set_token_cookies(response: Response, access_token: str, refresh_token: str, user_id: int) -> None:
    kw = _cookie_kwargs()
    response.set_cookie(_ACCESS_COOKIE, access_token, max_age=_TOKEN_TTL, **kw)
    response.set_cookie(_REFRESH_COOKIE, refresh_token, max_age=_TOKEN_TTL, **kw)
    response.set_cookie(_USER_ID_COOKIE, str(user_id), max_age=_TOKEN_TTL, **kw)


def _clear_token_cookies(response: Response) -> None:
    response.delete_cookie(_ACCESS_COOKIE)
    response.delete_cookie(_REFRESH_COOKIE)
    response.delete_cookie(_USER_ID_COOKIE)


@router.get("/login")
async def mal_login() -> RedirectResponse:
    code_verifier = secrets.token_urlsafe(64)[:128]
    params = urlencode({
        "response_type": "code",
        "client_id": MAL_CLIENT_ID,
        "redirect_uri": MAL_REDIRECT_URI,
        "code_challenge": code_verifier,
        "code_challenge_method": "plain",
    })
    redirect = RedirectResponse(f"https://myanimelist.net/v1/oauth2/authorize?{params}")
    redirect.set_cookie(_VERIFIER_COOKIE, code_verifier, max_age=_VERIFIER_TTL, **_cookie_kwargs())
    return redirect


@router.get("/callback")
async def mal_callback(
    code: str,
    mal_code_verifier: str | None = Cookie(default=None),
) -> RedirectResponse:
    if not mal_code_verifier:
        raise HTTPException(400, "Missing PKCE code verifier — please try connecting again.")
    try:
        tokens = await exchange_code(code, mal_code_verifier)
        user = await get_user_info(tokens["access_token"])
    except Exception as e:
        raise HTTPException(400, f"Token exchange failed: {e}")

    redirect = RedirectResponse(FRONTEND_URL)
    redirect.delete_cookie(_VERIFIER_COOKIE)
    _set_token_cookies(redirect, tokens["access_token"], tokens["refresh_token"], user["id"])
    return redirect


@router.post("/logout")
async def mal_logout(response: Response) -> dict:
    _clear_token_cookies(response)
    return {"status": "logged out"}


@router.get("/me")
async def mal_me(
    response: Response,
    mal_access_token: str | None = Cookie(default=None),
    mal_refresh_token: str | None = Cookie(default=None),
) -> dict:
    if not mal_access_token:
        raise HTTPException(401, "Not authenticated")
    try:
        user = await get_user_info(mal_access_token)
    except Exception:
        if not mal_refresh_token:
            _clear_token_cookies(response)
            raise HTTPException(401, "Session expired — please reconnect MyAnimeList.")
        try:
            tokens = await refresh_access_token(mal_refresh_token)
            user = await get_user_info(tokens["access_token"])
        except Exception:
            _clear_token_cookies(response)
            raise HTTPException(401, "Session expired — please reconnect MyAnimeList.")
        _set_token_cookies(response, tokens["access_token"], tokens["refresh_token"], user["id"])
    return {
        "id": user["id"],
        "name": user["name"],
        "picture": user.get("picture"),
    }

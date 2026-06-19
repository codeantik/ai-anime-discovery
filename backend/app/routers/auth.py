"""AniList OAuth2 auth endpoints."""

from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, HTTPException, Response
from fastapi.responses import RedirectResponse

from app.core.anilist_client import exchange_code, get_viewer
from app.core.config import ANILIST_CLIENT_ID, ANILIST_REDIRECT_URI, FRONTEND_URL, IS_PRODUCTION

router = APIRouter(prefix="/auth/anilist", tags=["auth"])

_ACCESS_COOKIE = "al_access_token"
_USER_ID_COOKIE = "al_user_id"
_TOKEN_TTL = 365 * 24 * 60 * 60  # AniList tokens last ~1 year


def _set_cookies(response: Response, access_token: str, user_id: int) -> None:
    # The frontend proxies all backend calls through its own origin (see
    # frontend/next.config.ts rewrites()), so this response is always seen by
    # the browser as first-party — Lax is sufficient even in production.
    kw = dict(httponly=True, samesite="lax", secure=True) if IS_PRODUCTION else dict(httponly=True, samesite="lax", secure=False)
    response.set_cookie(_ACCESS_COOKIE, access_token, max_age=_TOKEN_TTL, **kw)
    response.set_cookie(_USER_ID_COOKIE, str(user_id), max_age=_TOKEN_TTL, **kw)


def _clear_cookies(response: Response) -> None:
    response.delete_cookie(_ACCESS_COOKIE)
    response.delete_cookie(_USER_ID_COOKIE)


@router.get("/login")
async def anilist_login() -> RedirectResponse:
    params = urlencode({
        "client_id": ANILIST_CLIENT_ID,
        "redirect_uri": ANILIST_REDIRECT_URI,
        "response_type": "code",
    })
    return RedirectResponse(f"https://anilist.co/api/v2/oauth/authorize?{params}")


@router.get("/callback")
async def anilist_callback(code: str) -> RedirectResponse:
    try:
        tokens = await exchange_code(code)
    except Exception as e:
        raise HTTPException(400, f"Token exchange failed: {e}")
    access_token = tokens["access_token"]
    viewer = await get_viewer(access_token)

    redirect = RedirectResponse(FRONTEND_URL)
    _set_cookies(redirect, access_token, viewer["id"])
    return redirect


@router.post("/logout")
async def anilist_logout(response: Response) -> dict:
    _clear_cookies(response)
    return {"status": "logged out"}


@router.get("/me")
async def anilist_me(
    al_access_token: str | None = Cookie(default=None),
    response: Response = None,  # type: ignore[assignment]
) -> dict:
    if not al_access_token:
        raise HTTPException(401, "Not authenticated")
    try:
        viewer = await get_viewer(al_access_token)
    except Exception:
        _clear_cookies(response)
        raise HTTPException(401, "Session expired — please log in again.")
    return {
        "id": viewer["id"],
        "name": viewer["name"],
        "picture": (viewer.get("avatar") or {}).get("large"),
    }

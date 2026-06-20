"""Async HTTP helpers for Google OAuth2 — identity provider only, no app data scopes."""

import httpx

from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

_GOOGLE_OAUTH = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO = "https://www.googleapis.com/oauth2/v3/userinfo"


async def exchange_code(code: str) -> dict:
    """Exchange authorization code for an access token."""
    async with httpx.AsyncClient() as client:
        r = await client.post(
            _GOOGLE_OAUTH,
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": GOOGLE_REDIRECT_URI,
            },
        )
        r.raise_for_status()
        return r.json()


async def get_user_info(access_token: str) -> dict:
    """Returns {sub, email, name, picture, ...} for the authenticated Google account."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            _GOOGLE_USERINFO,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r.raise_for_status()
        return r.json()

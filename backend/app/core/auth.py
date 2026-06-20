"""Reusable session dependencies — single source of truth for "who is the caller".

Two independent identities exist:
- CurrentUser (get_current_user / get_optional_user): the AniList-linked account that
  owns watchlist/feedback/recommendation data. Unchanged by Google sign-in.
- AppUser (get_current_app_user / get_optional_app_user): "is someone signed into the
  app at all", proven by our own JWT session cookie issued after Google OAuth. Does
  not require an AniList link.
"""

from dataclasses import dataclass

from fastapi import Cookie, HTTPException

from app.core.session import verify_session_token


@dataclass
class CurrentUser:
    id: int
    access_token: str


async def get_current_user(
    al_access_token: str | None = Cookie(default=None),
    al_user_id: str | None = Cookie(default=None),
) -> CurrentUser:
    """Require a logged-in AniList session; raises 401 otherwise."""
    if not al_access_token or not al_user_id:
        raise HTTPException(401, "Please connect your AniList account first.")
    return CurrentUser(id=int(al_user_id), access_token=al_access_token)


async def get_optional_user(
    al_access_token: str | None = Cookie(default=None),
    al_user_id: str | None = Cookie(default=None),
) -> CurrentUser | None:
    """Same session lookup, but degrades to None for endpoints that work anonymously."""
    if not al_access_token or not al_user_id:
        return None
    return CurrentUser(id=int(al_user_id), access_token=al_access_token)


@dataclass
class AppUser:
    id: str  # Google "sub"


async def get_current_app_user(
    app_session: str | None = Cookie(default=None),
) -> AppUser:
    """Require a signed-in app session (Google); raises 401 otherwise."""
    user_id = verify_session_token(app_session) if app_session else None
    if not user_id:
        raise HTTPException(401, "Please sign in.")
    return AppUser(id=user_id)


async def get_optional_app_user(
    app_session: str | None = Cookie(default=None),
) -> AppUser | None:
    user_id = verify_session_token(app_session) if app_session else None
    return AppUser(id=user_id) if user_id else None

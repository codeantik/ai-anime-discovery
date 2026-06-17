"""Async HTTP helpers for MAL API v2 and AniList (for id lookups)."""

import httpx

from app.core.config import MAL_CLIENT_ID, MAL_CLIENT_SECRET, MAL_REDIRECT_URI

_MAL_API = "https://api.myanimelist.net/v2"
_MAL_OAUTH = "https://myanimelist.net/v1/oauth2"
_ANILIST_GQL = "https://graphql.anilist.co"


async def exchange_code(code: str, code_verifier: str) -> dict:
    """Exchange authorization code for access + refresh tokens."""
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_MAL_OAUTH}/token",
            data={
                "client_id": MAL_CLIENT_ID,
                "client_secret": MAL_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": MAL_REDIRECT_URI,
                "code_verifier": code_verifier,
            },
        )
        r.raise_for_status()
        return r.json()


async def refresh_access_token(refresh_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_MAL_OAUTH}/token",
            data={
                "client_id": MAL_CLIENT_ID,
                "client_secret": MAL_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        r.raise_for_status()
        return r.json()


async def get_user_info(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{_MAL_API}/users/@me",
            params={"fields": "id,name,picture"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r.raise_for_status()
        return r.json()


async def get_anime_list(access_token: str, limit: int = 100) -> list[dict]:
    """Return user's completed/watching anime with scores."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{_MAL_API}/users/@me/animelist",
            params={
                "fields": "list_status,title,num_episodes",
                "status": "completed",
                "sort": "list_score",
                "limit": limit,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r.raise_for_status()
        data = r.json()
    return [
        {
            "mal_id": item["node"]["id"],
            "title": item["node"]["title"],
            "score": item["list_status"].get("score", 0),
        }
        for item in data.get("data", [])
        if item["list_status"].get("score", 0) > 0
    ]


async def update_anime_status(access_token: str, mal_id: int, status: str = "plan_to_watch") -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.patch(
            f"{_MAL_API}/anime/{mal_id}/my_list_status",
            data={"status": status},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        r.raise_for_status()
        return r.json()


async def get_mal_id_from_anilist(anilist_id: int) -> int | None:
    """Query AniList GraphQL to get the MAL ID for a given AniList ID."""
    query = """
    query ($id: Int) {
      Media(id: $id, type: ANIME) { idMal }
    }
    """
    async with httpx.AsyncClient() as client:
        r = await client.post(
            _ANILIST_GQL,
            json={"query": query, "variables": {"id": anilist_id}},
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        data = r.json()
    return data.get("data", {}).get("Media", {}).get("idMal")

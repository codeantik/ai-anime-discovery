"""Async helpers for AniList OAuth2 and GraphQL API."""

import httpx

from app.core.config import ANILIST_CLIENT_ID, ANILIST_CLIENT_SECRET, ANILIST_REDIRECT_URI

_OAUTH_TOKEN = "https://anilist.co/api/v2/oauth/token"
_GQL = "https://graphql.anilist.co"


async def exchange_code(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            _OAUTH_TOKEN,
            json={
                "grant_type": "authorization_code",
                "client_id": int(ANILIST_CLIENT_ID),
                "client_secret": ANILIST_CLIENT_SECRET,
                "redirect_uri": ANILIST_REDIRECT_URI,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        r.raise_for_status()
        return r.json()


async def _gql(query: str, variables: dict | None = None, token: str | None = None) -> dict:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient() as client:
        r = await client.post(_GQL, json={"query": query, "variables": variables or {}}, headers=headers)
        r.raise_for_status()
        return r.json()


async def get_viewer(token: str) -> dict:
    data = await _gql(
        """query { Viewer { id name avatar { large } } }""",
        token=token,
    )
    return data["data"]["Viewer"]


async def get_completed_list(token: str, user_id: int) -> list[dict]:
    """Return user's completed anime with scores, sorted score desc."""
    data = await _gql(
        """
        query ($userId: Int) {
          MediaListCollection(userId: $userId, type: ANIME, status: COMPLETED, sort: SCORE_DESC) {
            lists { entries { score media { id title { romaji english } } } }
          }
        }
        """,
        variables={"userId": user_id},
        token=token,
    )
    entries = []
    for lst in data["data"]["MediaListCollection"]["lists"]:
        for e in lst["entries"]:
            if e["score"] and e["score"] > 0:
                media = e["media"]
                entries.append({
                    "anilist_id": media["id"],
                    "title": media["title"].get("english") or media["title"].get("romaji") or "",
                    "score": e["score"],
                })
    return entries


async def save_list_entry(token: str, anilist_id: int, status: str = "PLANNING") -> dict:
    """Add/update an anime on the user's AniList."""
    data = await _gql(
        """
        mutation ($mediaId: Int, $status: MediaListStatus) {
          SaveMediaListEntry(mediaId: $mediaId, status: $status) { id status }
        }
        """,
        variables={"mediaId": anilist_id, "status": status},
        token=token,
    )
    return data["data"]["SaveMediaListEntry"]

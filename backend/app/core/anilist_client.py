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


async def get_anime_detail(anilist_id: int) -> dict | None:
    """Fetch extended detail fields for one anime (no auth required, no token param)."""
    data = await _gql(
        """
        query ($id: Int) {
          Media(id: $id, type: ANIME) {
            id
            title { romaji english }
            description(asHtml: false)
            genres
            tags { name rank isGeneralSpoiler }
            startDate { year }
            format
            status
            meanScore
            averageScore
            episodes
            duration
            source
            coverImage { large extraLarge }
            bannerImage
            studios(isMain: true) { nodes { name } }
            trailer { id site }
            characters(sort: ROLE, perPage: 8) {
              nodes { name { full } image { medium } }
            }
          }
        }
        """,
        variables={"id": anilist_id},
    )
    media = data.get("data", {}).get("Media")
    return media


async def get_seasonal_anime(season: str, year: int, per_page: int = 50) -> list[dict]:
    """Live lookup of a season's anime — ids + status only (no auth required); the
    catalog doesn't store season/status, so this is the live complement to it."""
    data = await _gql(
        """
        query ($season: MediaSeason, $year: Int, $perPage: Int) {
          Page(page: 1, perPage: $perPage) {
            media(season: $season, seasonYear: $year, type: ANIME, sort: POPULARITY_DESC) {
              id
              status
            }
          }
        }
        """,
        variables={"season": season, "year": year, "perPage": per_page},
    )
    return data["data"]["Page"]["media"]


async def get_all_list_ids(token: str, user_id: int) -> list[int]:
    """Return all anime IDs currently on the user's list (any status)."""
    data = await _gql(
        """
        query ($userId: Int) {
          MediaListCollection(userId: $userId, type: ANIME) {
            lists { entries { media { id } } }
          }
        }
        """,
        variables={"userId": user_id},
        token=token,
    )
    ids: list[int] = []
    for lst in data["data"]["MediaListCollection"]["lists"]:
        for e in lst["entries"]:
            ids.append(e["media"]["id"])
    return ids


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

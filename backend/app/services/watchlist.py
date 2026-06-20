"""Per-user watchlist — save anime for later, independent of AniList/MAL list pushes."""

import logging

from app.core.db import get_db

logger = logging.getLogger(__name__)

COLLECTION = "watchlist"


async def get_watchlist_ids(user_id: int) -> list[int]:
    db = get_db()
    if db is None:
        return []
    try:
        doc = await db[COLLECTION].find_one({"_id": user_id}, {"anime_ids": 1})
    except Exception as e:
        logger.warning(f"Failed to read watchlist for user {user_id}: {e}")
        return []
    return doc.get("anime_ids", []) if doc else []


async def add_bookmark(user_id: int, anilist_id: int) -> None:
    db = get_db()
    if db is None:
        return
    try:
        await db[COLLECTION].update_one(
            {"_id": user_id},
            {"$addToSet": {"anime_ids": anilist_id}},
            upsert=True,
        )
    except Exception as e:
        logger.warning(f"Failed to add bookmark for user {user_id}: {e}")


async def remove_bookmark(user_id: int, anilist_id: int) -> None:
    db = get_db()
    if db is None:
        return
    try:
        await db[COLLECTION].update_one(
            {"_id": user_id},
            {"$pull": {"anime_ids": anilist_id}},
        )
    except Exception as e:
        logger.warning(f"Failed to remove bookmark for user {user_id}: {e}")

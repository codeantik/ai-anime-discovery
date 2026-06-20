"""Per-user recommendation history — avoids re-suggesting the same titles across sessions."""

import logging

from app.core.db import get_db

logger = logging.getLogger(__name__)

COLLECTION = "recommendation_history"


async def get_seen_ids(user_id: int) -> set[int]:
    db = get_db()
    if db is None:
        return set()
    try:
        doc = await db[COLLECTION].find_one({"_id": user_id}, {"shown_ids": 1})
    except Exception as e:
        logger.warning(f"Failed to read recommendation history for user {user_id}: {e}")
        return set()
    return set(doc.get("shown_ids", [])) if doc else set()


async def record_shown(user_id: int, anilist_ids: list[int]) -> None:
    if not anilist_ids:
        return
    db = get_db()
    if db is None:
        return
    try:
        await db[COLLECTION].update_one(
            {"_id": user_id},
            {"$addToSet": {"shown_ids": {"$each": anilist_ids}}},
            upsert=True,
        )
    except Exception as e:
        logger.warning(f"Failed to record recommendation history for user {user_id}: {e}")

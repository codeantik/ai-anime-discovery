"""Per-user thumbs up/down feedback — nudges the taste vector and hard-excludes dislikes."""

import logging

from app.core.db import get_db

logger = logging.getLogger(__name__)

COLLECTION = "feedback"


async def get_feedback_map(user_id: int) -> dict[int, int]:
    """Returns {anilist_id: signal} where signal is 1 (like) or -1 (dislike)."""
    db = get_db()
    if db is None:
        return {}
    try:
        doc = await db[COLLECTION].find_one({"_id": user_id}, {"signals": 1})
    except Exception as e:
        logger.warning(f"Failed to read feedback for user {user_id}: {e}")
        return {}
    if not doc:
        return {}
    return {int(k): v for k, v in doc.get("signals", {}).items()}


async def get_disliked_ids(user_id: int) -> set[int]:
    feedback = await get_feedback_map(user_id)
    return {anilist_id for anilist_id, signal in feedback.items() if signal == -1}


async def set_feedback(user_id: int, anilist_id: int, signal: int) -> None:
    db = get_db()
    if db is None:
        return
    try:
        if signal == 0:
            await db[COLLECTION].update_one(
                {"_id": user_id}, {"$unset": {f"signals.{anilist_id}": ""}}
            )
        else:
            await db[COLLECTION].update_one(
                {"_id": user_id},
                {"$set": {f"signals.{anilist_id}": signal}},
                upsert=True,
            )
    except Exception as e:
        logger.warning(f"Failed to set feedback for user {user_id}: {e}")

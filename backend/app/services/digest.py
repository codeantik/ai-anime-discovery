"""Personalized 'new for you' digest — a periodically refreshed batch of taste-vector-only
recommendations, snapshotted in Mongo so the NavBar can cheaply show an unread badge.
"""

import logging
from datetime import UTC, datetime, timedelta

from app.core.db import get_db
from app.models.recommend import RecommendRequest
from app.services.recommend import recommend
from app.services.taste import get_taste_vector

logger = logging.getLogger(__name__)

COLLECTION = "digest"

# Regenerating hits AniList + FAISS + the LLM, so only refresh once a day per user.
DIGEST_REFRESH = timedelta(hours=24)


async def get_digest(user_id: int, access_token: str) -> dict | None:
    """
    Returns {generated_at, viewed, recommendations} or None if there isn't enough
    taste signal yet to personalize a digest. Reuses a cached snapshot until it's
    older than DIGEST_REFRESH; only calls the recommend pipeline on a stale/missing one.
    """
    db = get_db()
    if db is None:
        return None

    try:
        doc = await db[COLLECTION].find_one({"_id": user_id})
    except Exception as e:
        logger.warning(f"Failed to read digest for user {user_id}: {e}")
        doc = None

    fresh_enough = (
        doc is not None
        and doc.get("recommendations")
        and datetime.now(UTC) - doc["generated_at"].replace(tzinfo=UTC) < DIGEST_REFRESH
    )
    if fresh_enough:
        return doc

    taste_vec = await get_taste_vector(access_token, user_id)
    if taste_vec is None:
        return doc  # no signal yet — surface the stale digest (if any) rather than nothing

    response = await recommend(RecommendRequest(), taste_vec=taste_vec, user_id=user_id)
    if not response.recommendations:
        return doc

    new_doc = {
        "_id": user_id,
        "generated_at": datetime.now(UTC),
        "viewed": False,
        "recommendations": [r.model_dump() for r in response.recommendations],
    }
    try:
        await db[COLLECTION].replace_one({"_id": user_id}, new_doc, upsert=True)
    except Exception as e:
        logger.warning(f"Failed to persist digest for user {user_id}: {e}")
    return new_doc


async def mark_viewed(user_id: int) -> None:
    db = get_db()
    if db is None:
        return
    try:
        await db[COLLECTION].update_one({"_id": user_id}, {"$set": {"viewed": True}})
    except Exception as e:
        logger.warning(f"Failed to mark digest viewed for user {user_id}: {e}")

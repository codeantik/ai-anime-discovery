"""Public shareable links for a single anime card or a user's watchlist."""

import logging
import secrets
from datetime import datetime, timezone

from app.core.db import get_db

logger = logging.getLogger(__name__)

COLLECTION = "shares"


async def create_card_share(owner_id: int, anilist_id: int, recommended_because: str) -> str | None:
    db = get_db()
    if db is None:
        return None
    token = secrets.token_urlsafe(16)
    try:
        await db[COLLECTION].insert_one(
            {
                "_id": token,
                "type": "card",
                "owner_id": owner_id,
                "anilist_id": anilist_id,
                "recommended_because": recommended_because,
                "created_at": datetime.now(timezone.utc),
            }
        )
    except Exception as e:
        logger.warning(f"Failed to create card share for user {owner_id}: {e}")
        return None
    return token


async def create_watchlist_share(owner_id: int) -> str | None:
    db = get_db()
    if db is None:
        return None
    try:
        existing = await db[COLLECTION].find_one({"type": "watchlist", "owner_id": owner_id})
        if existing:
            return existing["_id"]
        token = secrets.token_urlsafe(16)
        await db[COLLECTION].insert_one(
            {
                "_id": token,
                "type": "watchlist",
                "owner_id": owner_id,
                "created_at": datetime.now(timezone.utc),
            }
        )
    except Exception as e:
        logger.warning(f"Failed to create watchlist share for user {owner_id}: {e}")
        return None
    return token


async def create_digest_share(owner_id: int) -> str | None:
    db = get_db()
    if db is None:
        return None
    try:
        existing = await db[COLLECTION].find_one({"type": "digest", "owner_id": owner_id})
        if existing:
            return existing["_id"]
        token = secrets.token_urlsafe(16)
        await db[COLLECTION].insert_one(
            {
                "_id": token,
                "type": "digest",
                "owner_id": owner_id,
                "created_at": datetime.now(timezone.utc),
            }
        )
    except Exception as e:
        logger.warning(f"Failed to create digest share for user {owner_id}: {e}")
        return None
    return token


async def get_share(token: str) -> dict | None:
    db = get_db()
    if db is None:
        return None
    try:
        return await db[COLLECTION].find_one({"_id": token})
    except Exception as e:
        logger.warning(f"Failed to read share {token}: {e}")
        return None

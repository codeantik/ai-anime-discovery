"""App user accounts — identity only (Google sign-in). Independent of AniList/MAL linking."""

import logging

from pymongo import ReturnDocument

from app.core.db import get_db

logger = logging.getLogger(__name__)

COLLECTION = "users"


async def get_or_create_user(google_sub: str, email: str, name: str, picture: str | None) -> dict:
    db = get_db()
    if db is None:
        return {"_id": google_sub, "email": email, "name": name, "picture": picture}
    profile = {"email": email, "name": name, "picture": picture}
    doc = await db[COLLECTION].find_one_and_update(
        {"_id": google_sub},
        {"$set": profile, "$setOnInsert": {"_id": google_sub}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return doc


async def get_user(user_id: str) -> dict | None:
    db = get_db()
    if db is None:
        return None
    try:
        return await db[COLLECTION].find_one({"_id": user_id})
    except Exception as e:
        logger.warning(f"Failed to read user {user_id}: {e}")
        return None

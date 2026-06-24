"""Friend/group combined recommendations — average two taste vectors and reuse the
existing recommend() pipeline, taste-vector-only (same pattern as digest.py).
"""

import logging
import secrets
from datetime import datetime, timezone

import numpy as np

from app.core.db import get_db
from app.models.recommend import RecommendRequest
from app.services.recommend import recommend
from app.services.taste import get_taste_vector

logger = logging.getLogger(__name__)

COLLECTION = "duo_invites"


async def create_duo_invite(owner_id: int, access_token: str) -> str | None:
    """Snapshots the owner's current taste vector under a new token so a guest can
    later combine it with their own. Returns None if the owner has no taste signal yet."""
    taste_vec = await get_taste_vector(access_token, owner_id)
    if taste_vec is None:
        return None

    db = get_db()
    if db is None:
        return None
    token = secrets.token_urlsafe(16)
    try:
        await db[COLLECTION].insert_one(
            {
                "_id": token,
                "owner_id": owner_id,
                "taste_vector": taste_vec.tolist(),
                "created_at": datetime.now(timezone.utc),
            }
        )
    except Exception as e:
        logger.warning(f"Failed to create duo invite for user {owner_id}: {e}")
        return None
    return token


async def get_duo_recommendations(
    token: str, guest_id: int | None, guest_access_token: str | None
) -> dict | None:
    """
    Returns {"combined", "recommendations"} or None if the invite token doesn't exist.
    "combined" is True once the guest has their own taste signal to blend in;
    otherwise falls back to the owner's vector alone (e.g. guest hasn't connected
    AniList yet, or is opening their own invite link).
    """
    db = get_db()
    if db is None:
        return None
    try:
        invite = await db[COLLECTION].find_one({"_id": token})
    except Exception as e:
        logger.warning(f"Failed to read duo invite {token}: {e}")
        invite = None
    if invite is None:
        return None

    owner_vec = np.array(invite["taste_vector"], dtype=np.float32)

    guest_vec = None
    if guest_id is not None and guest_id != invite["owner_id"] and guest_access_token:
        guest_vec = await get_taste_vector(guest_access_token, guest_id)

    if guest_vec is not None:
        blended = owner_vec + guest_vec
        norm = np.linalg.norm(blended)
        taste_vec = (blended / norm) if norm > 0 else owner_vec
        combined = True
    else:
        taste_vec = owner_vec
        combined = False

    response = await recommend(RecommendRequest(), taste_vec=taste_vec)
    return {"combined": combined, "recommendations": response.recommendations}

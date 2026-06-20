"""MongoDB (Motor) client singleton. Optional — falls back to None if MONGODB_URI unset."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import MONGODB_DB, MONGODB_URI

_client: AsyncIOMotorClient | None = None


def get_db() -> AsyncIOMotorDatabase | None:
    global _client
    if not MONGODB_URI:
        return None
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URI)
    return _client[MONGODB_DB]


def close_db() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None

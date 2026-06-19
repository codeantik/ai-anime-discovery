import os
from pathlib import Path

from dotenv import load_dotenv

_BACKEND = Path(__file__).parent.parent.parent  # backend/
_ROOT = _BACKEND.parent                          # project root

# Load order: backend/.env → root .env → root .env.local (later files win on override)
load_dotenv(_BACKEND / ".env")
load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT / ".env.local", override=True)

ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION: bool = ENVIRONMENT == "production"

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")

MONGODB_URI: str = os.getenv("MONGODB_URI", "")
MONGODB_DB: str = os.getenv("MONGODB_DB", "anime_discovery")

LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "ai-anime-discovery")

TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(_ROOT / "data")))
CACHE_DIR: Path = DATA_DIR / "cache"

# AniList OAuth2
ANILIST_CLIENT_ID: str = os.getenv("ANILIST_CLIENT_ID", "")
ANILIST_CLIENT_SECRET: str = os.getenv("ANILIST_CLIENT_SECRET", "")
ANILIST_REDIRECT_URI: str = os.getenv("ANILIST_REDIRECT_URI", "http://localhost:3000/api/backend/auth/anilist/callback")
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

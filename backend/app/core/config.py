import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).parent.parent.parent.parent  # project root
load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT / ".env.local", override=True)

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")

MONGODB_URI: str = os.getenv("MONGODB_URI", "")
MONGODB_DB: str = os.getenv("MONGODB_DB", "anime_discovery")

LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "ai-anime-discovery")

DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(_ROOT / "data")))
CACHE_DIR: Path = DATA_DIR / "cache"

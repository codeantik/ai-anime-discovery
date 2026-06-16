from app.core.config import LLM_PROVIDER
from app.providers.base import EmbeddingProvider, LLMProvider


def get_embedding_provider() -> EmbeddingProvider:
    if LLM_PROVIDER == "openai":
        from app.providers.openai_provider import OpenAIEmbeddingProvider
        return OpenAIEmbeddingProvider()
    raise ValueError(f"Unsupported provider: {LLM_PROVIDER}. Supported: openai")


def get_llm_provider() -> LLMProvider:
    if LLM_PROVIDER == "openai":
        from app.providers.openai_provider import OpenAILLMProvider
        return OpenAILLMProvider()
    raise ValueError(f"Unsupported provider: {LLM_PROVIDER}. Supported: openai")

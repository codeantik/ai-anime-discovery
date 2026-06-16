from openai import AsyncOpenAI, OpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL, OPENAI_EMBEDDING_MODEL
from app.providers.base import EmbeddingProvider, LLMProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self._async = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def embed(self, text: str) -> list[float]:
        resp = await self._async.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL, input=[text]
        )
        return resp.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        resp = await self._async.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL, input=texts
        )
        return [item.embedding for item in resp.data]


class OpenAILLMProvider(LLMProvider):
    def __init__(self) -> None:
        self._async = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def complete(self, prompt: str) -> str:
        resp = await self._async.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""

    async def complete_json(self, prompt: str) -> dict:
        import json

        resp = await self._async.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content or "{}")


# Sync versions used by offline build scripts
class OpenAIEmbeddingProviderSync:
    def __init__(self) -> None:
        self._client = OpenAI(api_key=OPENAI_API_KEY)

    def embed(self, text: str) -> list[float]:
        resp = self._client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL, input=[text]
        )
        return resp.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL, input=texts
        )
        return [item.embedding for item in resp.data]

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Embed a single string and return the vector."""

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of strings."""


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str:
        """Return a plain text completion."""

    @abstractmethod
    async def complete_json(self, prompt: str) -> dict:
        """Return a parsed JSON completion."""

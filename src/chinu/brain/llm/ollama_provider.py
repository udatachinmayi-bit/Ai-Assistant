"""Ollama LLM provider implementation."""

from typing import Any, AsyncGenerator, Dict, List

from ollama import AsyncClient

from chinu.brain.llm.base import AsyncLLM
from chinu.brain.llm.config import OllamaConfig


class OllamaProvider(AsyncLLM):
    """LLM provider for local Ollama models."""

    def __init__(self, config: OllamaConfig) -> None:
        """Initialize the Ollama provider."""
        self.config = config
        self.client = AsyncClient(host=self.config.host)

    async def chat_completion(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Generate a chat completion stream from Ollama."""
        stream = await self.client.chat(
            model=self.config.chat_model,
            messages=messages,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            content = chunk["message"]["content"]
            if content:
                yield content

    async def generate_embedding(self, text: str, **kwargs: Any) -> List[float]:
        """Generate an embedding using Ollama's models."""
        response = await self.client.embeddings(
            model=self.config.embedding_model, prompt=text, **kwargs
        )
        return response["embedding"]
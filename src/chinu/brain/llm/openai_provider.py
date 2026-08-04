"""OpenAI LLM provider implementation."""

from typing import Any, AsyncGenerator, Dict, List

from openai import AsyncOpenAI

from chinu.brain.llm.base import AsyncLLM
from chinu.brain.llm.config import OpenAIConfig


class OpenAIProvider(AsyncLLM):
    """LLM provider for OpenAI models."""

    def __init__(self, config: OpenAIConfig) -> None:
        """Initialize the OpenAI provider."""
        self.config = config
        self.client = AsyncOpenAI(api_key=self.config.api_key)

    async def chat_completion(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Generate a chat completion stream from OpenAI."""
        stream = await self.client.chat.completions.create(
            model=self.config.chat_model,
            messages=messages,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    async def generate_embedding(self, text: str, **kwargs: Any) -> List[float]:
        """Generate an embedding using OpenAI's models."""
        response = await self.client.embeddings.create(
            model=self.config.embedding_model, input=[text], **kwargs
        )
        return response.data[0].embedding
"""Google Gemini LLM provider implementation."""

from typing import Any, AsyncGenerator, Dict, List

import google.generativeai as genai

from chinu.brain.llm.base import AsyncLLM
from chinu.brain.llm.config import GeminiConfig


class GeminiProvider(AsyncLLM):
    """LLM provider for Google Gemini models."""

    def __init__(self, config: GeminiConfig) -> None:
        """Initialize the Gemini provider."""
        self.config = config
        genai.configure(api_key=self.config.api_key)
        self.chat_model = genai.GenerativeModel(self.config.chat_model)
        self.embedding_model = genai.GenerativeModel(self.config.embedding_model)

    async def chat_completion(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Generate a chat completion stream from Gemini."""
        # Gemini uses a different message format, so we adapt it.
        # This is a simplified adaptation.
        history = [
            {"role": msg["role"], "parts": [msg["content"]]} for msg in messages[:-1]
        ]
        prompt = messages[-1]["content"]

        chat_session = self.chat_model.start_chat(history=history)
        response = await chat_session.send_message_async(prompt, stream=True, **kwargs)

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def generate_embedding(self, text: str, **kwargs: Any) -> List[float]:
        """Generate an embedding using Gemini's models."""
        response = await genai.embed_content_async(
            model=f"models/{self.config.embedding_model}", content=text, **kwargs
        )
        return response["embedding"]
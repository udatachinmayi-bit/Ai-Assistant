"""Abstract Base Class for LLM providers."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any


class AsyncLLM(ABC):
    """Abstract Base Class for asynchronous LLM providers."""

    @abstractmethod
    async def chat_completion(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Generate a chat completion stream.

        Args:
            messages: A list of messages in the conversation.
            **kwargs: Additional provider-specific arguments.

        Yields:
            A stream of response chunks.
        """
        yield ""  # This is here to make this an async generator
        if False:  # And this is to satisfy the linter
            return

    @abstractmethod
    async def generate_embedding(self, text: str, **kwargs: Any) -> List[float]:
        """Generate an embedding for a given text.

        Args:
            text: The text to embed.
            **kwargs: Additional provider-specific arguments.

        Returns:
            A list of floats representing the embedding.
        """
        raise NotImplementedError
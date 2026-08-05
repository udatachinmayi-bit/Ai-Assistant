"""Interfaces for the Text-to-Speech service."""

from abc import ABC, abstractmethod


class ITextToSpeechService(ABC):
    """Interface for the Text-to-Speech service."""

    @abstractmethod
    async def start(self) -> None:
        """Start the TTS service."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the TTS service."""
        pass

    @abstractmethod
    async def say(self, text: str, interrupt: bool = False) -> None:
        """Add text to the speech queue.

        Args:
            text: The text to speak.
            interrupt: Whether to interrupt the current speech.
        """
        pass

    @abstractmethod
    async def set_voice(self, voice: str) -> None:
        """Set the voice for the TTS engine.

        Args:
            voice: The name of the voice to use.
        """
        pass
"""Interfaces for the Voice Pipeline."""

from abc import ABC, abstractmethod


class IVoiceManager(ABC):
    """Interface for the main voice pipeline manager."""

    @abstractmethod
    async def start(self) -> None:
        """Start the voice pipeline."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the voice pipeline."""
        pass
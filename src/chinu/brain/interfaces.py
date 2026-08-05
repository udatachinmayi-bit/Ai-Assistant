"""Interfaces for the Brain service."""

from abc import ABC, abstractmethod


class IBrainService(ABC):
    """Interface for the main brain service."""

    @abstractmethod
    async def start(self) -> None:
        """Start the brain service."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the brain service."""
        pass
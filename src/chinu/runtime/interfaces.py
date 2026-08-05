"""Interfaces for the Assistant Runtime service."""

from abc import ABC, abstractmethod


class IAssistantRuntime(ABC):
    """Interface for the main assistant runtime service."""

    @abstractmethod
    async def start(self) -> None:
        """Start the assistant runtime service."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the assistant runtime service."""
        pass
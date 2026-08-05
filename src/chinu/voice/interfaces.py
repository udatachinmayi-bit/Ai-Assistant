"""Interfaces for the voice service."""

import abc


class IVoiceService(abc.ABC):
    """Interface for the Voice Service."""

    @abc.abstractmethod
    async def start(self) -> None:
        """Start the voice service."""
        raise NotImplementedError

    @abc.abstractmethod
    async def stop(self) -> None:
        """Stop the voice service."""
        raise NotImplementedError
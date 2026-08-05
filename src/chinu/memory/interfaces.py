"""Interfaces for memory-related services."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IMemoryService(ABC):
    """Interface for a service that manages conversation history."""

    @abstractmethod
    async def start(self) -> None:
        """Start the service and any background tasks."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the service and clean up resources."""
        pass

    @abstractmethod
    def save_message(self, role: str, content: str) -> None:
        """Save a message to the conversation history.

        Args:
            role: The role of the entity sending the message (e.g., 'user', 'assistant').
            content: The content of the message.
        """
        pass

    @abstractmethod
    def get_recent_messages(self, count: int) -> List[Dict[str, Any]]:
        """Retrieve the most recent messages from the history.

        Args:
            count: The number of recent messages to retrieve.

        Returns:
            A list of the most recent messages.
        """
        pass

    @abstractmethod
    def clear_session(self) -> None:
        """Clear the entire conversation history for the current session."""
        pass
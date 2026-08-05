"""A service for managing short-term conversation memory."""

from typing import List, Dict, Any
import asyncio

from chinu.core.interfaces.events import IEventBus
from chinu.logging_system.logger import get_logger
from chinu.memory.interfaces import IMemoryService

logger = get_logger("memory_service")


class MemoryService(IMemoryService):
    """Manages the short-term conversation history."""

    def __init__(self, event_bus: IEventBus) -> None:
        """Initialize the MemoryService.

        Args:
            event_bus: The application's event bus.
        """
        self._event_bus = event_bus
        self._history: List[Dict[str, Any]] = []
        self._is_running = False

    async def start(self) -> None:
        """Start the service and subscribe to conversation events."""
        if self._is_running:
            logger.warning("MemoryService is already running.")
            return

        logger.info("Starting MemoryService...")
        self._is_running = True
        await self._event_bus.subscribe_async("voice.transcribed", self._handle_user_message)
        await self._event_bus.subscribe_async("brain.response", self._handle_assistant_message)
        logger.info("MemoryService started and subscribed to conversation events.")

    async def stop(self) -> None:
        """Stop the service and unsubscribe from events."""
        if not self._is_running:
            logger.warning("MemoryService is not running.")
            return

        logger.info("Stopping MemoryService...")
        self._is_running = False
        await self._event_bus.unsubscribe_async("voice.transcribed", self._handle_user_message)
        await self._event_bus.unsubscribe_async("brain.response", self._handle_assistant_message)
        logger.info("MemoryService stopped.")

    async def _handle_user_message(self, event_data: dict) -> None:
        """Handle incoming user messages from the voice transcriber."""
        text = event_data.get("text")
        if text:
            self.save_message(role="user", content=text)

    async def _handle_assistant_message(self, event_data: dict) -> None:
        """Handle incoming assistant responses from the brain."""
        # For now, we'll just log the intent. In the future, this would be a full response.
        intent = event_data.get("intent")
        if intent:
            self.save_message(role="assistant", content=f"Intent: {intent}")

    def save_message(self, role: str, content: str) -> None:
        """Save a message to the conversation history."""
        message = {"role": role, "content": content}
        self._history.append(message)
        logger.debug(f"Saved message to memory: {message}")

    def get_recent_messages(self, count: int) -> List[Dict[str, Any]]:
        """Retrieve the most recent messages from the history."""
        return self._history[-count:]

    def clear_session(self) -> None:
        """Clear the entire conversation history."""
        self._history.clear()
        logger.info("Conversation memory cleared.")
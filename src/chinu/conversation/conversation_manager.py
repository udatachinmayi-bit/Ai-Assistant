"""Conversation Manager for Chinu AI."""

import asyncio
import time

from chinu.logging_system.logger import get_logger

logger = get_logger("conversation_manager")


class ConversationManager:
    """Manages the state and flow of a conversation."""

    def __init__(self, timeout: int = 15):
        """
        Initialize the ConversationManager.

        Args:
            timeout (int): The conversation timeout in seconds.
        """
        self.is_active = False
        self.last_interaction_time = 0
        self.timeout = timeout
        self._timeout_task: asyncio.Task | None = None

    async def start_conversation(self):
        """Start a new conversation."""
        self.is_active = True
        self.last_interaction_time = time.time()
        logger.info("🗣️ Conversation started.")
        self._start_timeout_task()

    async def end_conversation(self):
        """End the current conversation."""
        if self.is_active:
            self.is_active = False
            logger.info("Conversation ended.")
            if self._timeout_task and not self._timeout_task.done():
                self._timeout_task.cancel()

    def _start_timeout_task(self):
        """Start the background task to check for conversation timeout."""
        if self._timeout_task and not self._timeout_task.done():
            self._timeout_task.cancel()
        self._timeout_task = asyncio.create_task(self._check_timeout())

    async def _check_timeout(self):
        """Periodically check if the conversation has timed out."""
        while self.is_active:
            await asyncio.sleep(1)
            if time.time() - self.last_interaction_time > self.timeout:
                logger.info("Conversation timed out.")
                await self.end_conversation()
                break

    def reset_timer(self):
        """Reset the conversation timer."""
        if self.is_active:
            self.last_interaction_time = time.time()
            logger.info("Conversation timer reset.")
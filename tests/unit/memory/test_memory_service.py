"""Unit tests for the MemoryService."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, call

from chinu.core.event_bus import EventBus
from chinu.memory.short_term.memory_service import MemoryService


class TestMemoryService(unittest.TestCase):
    """Test suite for the MemoryService."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.event_bus = MagicMock(spec=EventBus)
        self.event_bus.subscribe_async = AsyncMock()
        self.event_bus.unsubscribe_async = AsyncMock()
        self.memory_service = MemoryService(event_bus=self.event_bus)

    def test_start_subscribes_to_events(self) -> None:
        """Test that start() subscribes to the correct events."""
        async def run_test() -> None:
            await self.memory_service.start()
            expected_calls = [
                call("voice.transcribed", self.memory_service._handle_user_message),
                call("brain.response", self.memory_service._handle_assistant_message),
            ]
            self.event_bus.subscribe_async.assert_has_calls(expected_calls, any_order=True)
            self.assertTrue(self.memory_service._is_running)

        asyncio.run(run_test())

    def test_stop_unsubscribes_from_events(self) -> None:
        """Test that stop() unsubscribes from the correct events."""
        async def run_test() -> None:
            self.memory_service._is_running = True
            await self.memory_service.stop()
            expected_calls = [
                call("voice.transcribed", self.memory_service._handle_user_message),
                call("brain.response", self.memory_service._handle_assistant_message),
            ]
            self.event_bus.unsubscribe_async.assert_has_calls(expected_calls, any_order=True)
            self.assertFalse(self.memory_service._is_running)

        asyncio.run(run_test())

    def test_save_and_get_messages(self) -> None:
        """Test saving and retrieving messages from history."""
        self.memory_service.save_message("user", "Hello")
        self.memory_service.save_message("assistant", "Hi there!")
        
        recent_messages = self.memory_service.get_recent_messages(2)
        self.assertEqual(len(recent_messages), 2)
        self.assertEqual(recent_messages[0]["content"], "Hello")
        self.assertEqual(recent_messages[1]["content"], "Hi there!")

    def test_clear_session(self) -> None:
        """Test clearing the conversation history."""
        self.memory_service.save_message("user", "This will be cleared.")
        self.memory_service.clear_session()
        recent_messages = self.memory_service.get_recent_messages(1)
        self.assertEqual(len(recent_messages), 0)

    def test_handle_user_message(self) -> None:
        """Test the handler for user messages."""
        async def run_test() -> None:
            with unittest.mock.patch.object(self.memory_service, 'save_message') as mock_save:
                await self.memory_service._handle_user_message({"text": "A user said this."})
                mock_save.assert_called_once_with(role="user", content="A user said this.")

        asyncio.run(run_test())

    def test_handle_assistant_message(self) -> None:
        """Test the handler for assistant messages."""
        async def run_test() -> None:
            with unittest.mock.patch.object(self.memory_service, 'save_message') as mock_save:
                await self.memory_service._handle_assistant_message({"intent": "CHAT"})
                mock_save.assert_called_once_with(role="assistant", content="Intent: CHAT")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
"""Unit tests for the BrainService."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

from chinu.brain.brain_service import BrainService
from chinu.brain.intent.intent_classifier import Intent
from chinu.core.event_bus import EventBus


class TestBrainService(unittest.TestCase):
    """Test suite for the BrainService."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.event_bus = MagicMock(spec=EventBus)
        self.event_bus.subscribe_async = AsyncMock()
        self.event_bus.unsubscribe_async = AsyncMock()
        self.event_bus.publish_async = AsyncMock()
        self.brain_service = BrainService(event_bus=self.event_bus)

    def test_start_subscribes_to_event(self) -> None:
        """Test that start() subscribes to the 'voice.transcribed' event."""
        async def run_test() -> None:
            await self.brain_service.start()
            self.event_bus.subscribe_async.assert_called_once_with(
                "voice.transcribed", self.brain_service.handle_transcription
            )
            self.assertTrue(self.brain_service._is_running)

        asyncio.run(run_test())

    def test_stop_unsubscribes_from_event(self) -> None:
        """Test that stop() unsubscribes from the 'voice.transcribed' event."""
        async def run_test() -> None:
            self.brain_service._is_running = True
            await self.brain_service.stop()
            self.event_bus.unsubscribe_async.assert_called_once_with(
                "voice.transcribed", self.brain_service.handle_transcription
            )
            self.assertFalse(self.brain_service._is_running)

        asyncio.run(run_test())

    def test_handle_transcription_publishes_response(self) -> None:
        """Test that handle_transcription processes text and publishes a response."""
        async def run_test() -> None:
            event_data = {"text": "open the browser"}
            await self.brain_service.handle_transcription(event_data)

            expected_response = {
                "intent": Intent.OPEN_APP.name,
                "text": "open the browser",
            }
            self.event_bus.publish_async.assert_called_once_with(
                "brain.response", expected_response
            )

        asyncio.run(run_test())

    def test_handle_transcription_with_no_text(self) -> None:
        """Test that handle_transcription handles events with no text."""
        async def run_test() -> None:
            event_data = {"text": ""}
            await self.brain_service.handle_transcription(event_data)
            self.event_bus.publish_async.assert_not_called()

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
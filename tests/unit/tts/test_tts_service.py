"""Unit tests for the TextToSpeechService."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from chinu.config.settings import TTSSettings, EdgeTTSConfig
from chinu.core.interfaces.events import IEventBus
from chinu.tts.tts_service import TextToSpeechService


class TestTextToSpeechService(unittest.TestCase):
    """Test suite for the TextToSpeechService."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.event_bus = AsyncMock(spec=IEventBus)
        self.config = TTSSettings(
            provider="edge_tts",
            edge_tts=EdgeTTSConfig(
                voice="en-US-AriaNeural",
                rate="+0%",
                volume="+0%",
            ),
        )
        
        # Patch the EdgeTTS class
        self.edge_tts_patch = patch('chinu.tts.tts_service.EdgeTTS', autospec=True)
        self.mock_edge_tts_class = self.edge_tts_patch.start()
        self.mock_edge_tts_instance = self.mock_edge_tts_class.return_value
        
        self.tts_service = TextToSpeechService(event_bus=self.event_bus, config=self.config)

    def tearDown(self) -> None:
        """Tear down the test case."""
        self.edge_tts_patch.stop()

    def test_start_subscribes_to_brain_response(self) -> None:
        """Test that start() subscribes to the 'brain.response' event."""
        async def run_test() -> None:
            await self.tts_service.start()
            self.event_bus.subscribe_async.assert_called_once_with(
                "brain.response", self.tts_service._handle_brain_response
            )
            self.assertTrue(self.tts_service._is_running)

        asyncio.run(run_test())

    def test_stop_unsubscribes_from_brain_response(self) -> None:
        """Test that stop() unsubscribes from the 'brain.response' event."""
        async def run_test() -> None:
            self.tts_service._is_running = True
            await self.tts_service.stop()
            self.event_bus.unsubscribe_async.assert_called_once_with(
                "brain.response", self.tts_service._handle_brain_response
            )
            self.mock_edge_tts_instance.stop.assert_called_once()
            self.assertFalse(self.tts_service._is_running)

        asyncio.run(run_test())

    def test_say_speaks_text(self) -> None:
        """Test that say() calls the TTS engine's speak method."""
        async def run_test() -> None:
            await self.tts_service.say("Hello, world!")
            self.mock_edge_tts_instance.speak.assert_called_once_with("Hello, world!")

        asyncio.run(run_test())

    def test_say_with_interrupt_stops_previous_speech(self) -> None:
        """Test that say() with interrupt=True stops the TTS engine."""
        async def run_test() -> None:
            await self.tts_service.say("Hello, world!", interrupt=True)
            self.mock_edge_tts_instance.stop.assert_called_once()
            self.mock_edge_tts_instance.speak.assert_called_once_with("Hello, world!")

        asyncio.run(run_test())

    def test_set_voice_updates_config(self) -> None:
        """Test that set_voice() updates the TTS engine's voice."""
        async def run_test() -> None:
            new_voice = "en-GB-SoniaNeural"
            await self.tts_service.set_voice(new_voice)
            self.assertEqual(self.tts_service._tts_engine.config.voice, new_voice)

        asyncio.run(run_test())

    def test_handle_brain_response_calls_say(self) -> None:
        """Test that the brain response handler calls say()."""
        async def run_test() -> None:
            response = {"text": "This is a test response."}
            with patch.object(self.tts_service, 'say', new_callable=AsyncMock) as mock_say:
                await self.tts_service._handle_brain_response(response)
                mock_say.assert_called_once_with("This is a test response.")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
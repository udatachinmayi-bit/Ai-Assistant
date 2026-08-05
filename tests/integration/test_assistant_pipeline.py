"""Integration tests for the full assistant pipeline."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from chinu.core.application import Application
from chinu.core.event_bus import EventBus
from chinu.brain.intent.intent_classifier import Intent


class TestAssistantPipeline(unittest.TestCase):
    """Test suite for the full assistant pipeline."""

    def setUp(self) -> None:
        """Set up the test case by bootstrapping the application."""
        self.app = Application()
        
        # Mock external dependencies
        self.mock_whisper = patch('chinu.voice.voice_manager.WhisperModel', autospec=True).start()
        self.mock_edge_tts = patch('chinu.tts.tts_service.EdgeTTS', autospec=True).start()
        
        self.app.bootstrap()
        
        # Get instances of services from the container
        self.event_bus = self.app.container.resolve(IEventBus)
        self.memory_service = self.app.container.resolve(IMemoryService)
        self.tts_service = self.app.container.resolve(ITextToSpeechService)

    def tearDown(self) -> None:
        """Tear down the test case."""
        patch.stopall()

    def test_full_pipeline(self) -> None:
        """Test the full pipeline from voice input to TTS output."""
        async def run_test() -> None:
            # Start the application
            await self.app.start()

            # 1. Simulate voice input by publishing a 'voice.transcribed' event
            user_input = "hello"
            await self.event_bus.publish_async("voice.transcribed", {"text": user_input})
            
            # Allow time for events to propagate
            await asyncio.sleep(0.1)

            # 2. Verify BrainService processes the input and publishes a response
            # We can check if the TTS service's 'say' method was called,
            # which is the end of the pipeline.
            self.tts_service._tts_engine.speak.assert_called_once()
            
            # 3. Verify MemoryService stores the conversation
            history = self.memory_service.get_recent_messages(2)
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["role"], "user")
            self.assertEqual(history[0]["content"], user_input)
            self.assertEqual(history[1]["role"], "assistant")
            
            # The content of the assistant's message depends on the BrainService's output
            # For a "hello" input, the intent is likely CHAT.
            expected_assistant_content = f"Intent: {Intent.CHAT.name}"
            self.assertEqual(history[1]["content"], expected_assistant_content)

            # Stop the application
            await self.app.stop()

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
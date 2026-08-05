"""Unit tests for the VoiceManager service."""

import asyncio
import unittest
from threading import Thread
from unittest.mock import AsyncMock, MagicMock, patch

from chinu.config.settings import VoiceSettings
from chinu.core.event_bus import EventBus
from chinu.voice.voice_manager import VoiceManager


class TestVoiceManager(unittest.TestCase):
    """Test suite for the VoiceManager service."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.event_bus = MagicMock(spec=EventBus)
        self.config = VoiceSettings(
            stt_model_path="tiny.en",
            stt_device="cpu",
            stt_compute_type="int8",
            mic_device=None,
            mic_sample_rate=16000,
            mic_block_size=1024,
            mic_channels=1,
        )

        # Patch WhisperModel to avoid downloading the model during tests
        with patch("chinu.voice.voice_manager.WhisperModel") as self.mock_whisper:
            self.mock_whisper.return_value = MagicMock()
            self.voice_manager = VoiceManager(
                event_bus=self.event_bus, config=self.config
            )

    @patch("chinu.voice.voice_manager.Thread")
    def test_start_creates_thread(self, mock_thread: MagicMock) -> None:
        """Test that start() creates and starts the worker thread."""
        async def run_test() -> None:
            await self.voice_manager.start()
            mock_thread.assert_called_once_with(
                target=self.voice_manager._run, daemon=True
            )
            self.voice_manager._worker_thread.start.assert_called_once()
            self.assertTrue(self.voice_manager._is_running)

        asyncio.run(run_test())

    def test_stop_joins_thread(self) -> None:
        """Test that stop() joins the worker thread."""
        async def run_test() -> None:
            # Mock the running thread
            self.voice_manager._is_running = True
            self.voice_manager._worker_thread = MagicMock(spec=Thread)

            await self.voice_manager.stop()

            self.voice_manager._worker_thread.join.assert_called_once()
            self.assertFalse(self.voice_manager._is_running)

        asyncio.run(run_test())

    @patch("sounddevice.RawInputStream")
    @patch("chinu.voice.voice_manager.VoiceManager._process_audio")
    def test_run_loop(
        self, mock_process_audio: MagicMock, mock_input_stream: MagicMock
    ) -> None:
        """Test the main _run loop to ensure it processes audio."""
        # Make _process_audio stop the loop after one iteration
        mock_process_audio.side_effect = lambda: setattr(
            self.voice_manager, "_is_running", False
        )

        self.voice_manager._is_running = True
        self.voice_manager._run()

        mock_input_stream.assert_called_once()
        mock_process_audio.assert_called_once()

    @patch("asyncio.run")
    def test_process_audio_publishes_event(self, mock_asyncio_run: MagicMock) -> None:
        """Test that _process_audio publishes an event on transcription."""
        # Mock the transcription result
        mock_segment = MagicMock()
        mock_segment.text = "hello world"
        self.voice_manager._model.transcribe.return_value = ([mock_segment], None)

        # Add some dummy data to the queue
        self.voice_manager._audio_queue.put(b"\x00" * 1024)

        self.voice_manager._process_audio()

        # Verify that publish_async was called correctly
        self.event_bus.publish_async.assert_called_once_with(
            "voice.transcribed", {"text": "hello world"}
        )
        mock_asyncio_run.assert_called_once_with(
            self.event_bus.publish_async(
                "voice.transcribed", {"text": "hello world"}
            )
        )


if __name__ == "__main__":
    unittest.main()
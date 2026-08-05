"""Voice Service for Chinu AI."""

import asyncio
import queue
import threading

import numpy as np
import sounddevice as sd
import torch
from faster_whisper import WhisperModel

from chinu.config.config_loader import SettingsConfig
from chinu.logging_system.logger import get_logger
from chinu.voice.interfaces import IVoiceService

logger = get_logger("voice_service")


class VoiceService(IVoiceService):
    """Service for handling voice input and output."""

    def __init__(self, config: SettingsConfig) -> None:
        """Initialize the VoiceService."""
        self._config = config
        self._is_running = False
        self._task: asyncio.Task | None = None
        self.whisper_model = self._config.voice.whisper_model
        self.model = WhisperModel(self.whisper_model, device="cpu", compute_type="int8")
        self.vad_model, _ = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
        self.audio_queue = queue.Queue()

    def _audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio callback status: {status}")
        self.audio_queue.put(bytes(indata))

    async def _process_audio(self):
        logger.info("Whisper Initialized.")
        logger.info("Listening...")
        while self._is_running:
            try:
                audio_data = self.audio_queue.get(timeout=1)
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                audio_tensor = torch.from_numpy(audio_np)
                speech_prob = self.vad_model(audio_tensor, 16000).item()
                if speech_prob > 0.5:
                    logger.info("Voice Started")
                    # Don't transcribe yet, just detect speech
                else:
                    logger.info("Voice Ended")

            except queue.Empty:
                continue

    async def _transcribe(self, audio_np):
        segments, _ = self.model.transcribe(audio_np, beam_size=5)
        for segment in segments:
            logger.info(f"Recognized: {segment.text}")
            await self._handle_transcription(segment.text)

    async def _handle_transcription(self, text):
        text_lower = text.lower().strip()
        if text_lower.startswith("chinu") or text_lower.startswith("sister"):
            logger.info("Wake Word Detected")
            parts = text.split(maxsplit=1)
            wake_word = parts[0]
            command = parts[1] if len(parts) > 1 else ""
            logger.info(f"Wake Word: {wake_word}")
            logger.info(f"Command: {command}")

    async def start(self) -> None:
        """Start the voice service."""
        if self._is_running:
            logger.warning("Voice service is already running.")
            return

        self._is_running = True
        self.stream = sd.InputStream(
            callback=self._audio_callback,
            channels=1,
            samplerate=16000,
            blocksize=1536,
            dtype="int16",
        )
        self.stream.start()
        self._task = asyncio.create_task(self._process_audio())
        logger.info("Voice Service Started")

    async def stop(self) -> None:
        """Stop the voice service."""
        if not self._is_running or not self._task:
            logger.warning("Voice service is not running.")
            return

        logger.info("Stopping voice service...")
        self._is_running = False
        self.stream.stop()
        self.stream.close()
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        logger.info("Voice service stopped.")

    async def _run(self) -> None:
        """Main loop for the voice service."""
        # The main logic is now in _process_audio
        pass
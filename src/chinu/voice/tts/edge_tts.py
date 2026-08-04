"""Edge-TTS Text-to-Speech (TTS) engine implementation."""

import asyncio

import edge_tts
from edge_tts import VoicesManager

from chinu.logging_system.logger import get_logger
from chinu.voice.tts.config import EdgeTTSConfig

logger = get_logger("edge_tts")


class EdgeTTS:
    """Text-to-Speech engine using the edge-tts library."""

    def __init__(self, config: EdgeTTSConfig) -> None:
        """Initialize the Edge-TTS engine."""
        self.config = config
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._is_speaking = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None

    async def speak(self, text: str) -> None:
        """Add text to the speech queue."""
        await self._queue.put(text)
        if not self._is_speaking.is_set():
            self._is_speaking.set()
            if self._task is None or self._task.done():
                self._task = asyncio.create_task(self._process_queue())

    async def stop(self) -> None:
        """Stop the current speech and clear the queue."""
        if self._is_speaking.is_set():
            self._stop_event.set()
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            self._clear_queue()
            self._is_speaking.clear()
            self._stop_event.clear()
            logger.info("TTS speech stopped and queue cleared.")

    def _clear_queue(self) -> None:
        """Clear all items from the queue."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    async def _process_queue(self) -> None:
        """Process the speech queue."""
        while not self._queue.empty():
            if self._stop_event.is_set():
                break
            text = await self._queue.get()
            await self._stream_audio(text)
        self._is_speaking.clear()

    async def _stream_audio(self, text: str) -> None:
        """Stream audio for the given text."""
        try:
            communicate = edge_tts.Communicate(
                text, self.config.voice, rate=self.config.rate, volume=self.config.volume
            )
            # This part is tricky as it requires an audio backend to play the sound.
            # For this implementation, we will just log the generation of speech.
            # A real implementation would use a library like `sounddevice` or `pyaudio`
            # to play the audio stream.
            logger.info(f"Generating speech for: {text}")
            async for _ in communicate.stream():
                if self._stop_event.is_set():
                    logger.info("TTS stream interrupted.")
                    break
            logger.info(f"Finished generating speech for: {text}")
        except Exception as e:
            logger.error(f"Failed to stream TTS audio: {e}", exc_info=True)

    @staticmethod
    async def list_voices() -> list[dict]:
        """List all available voices."""
        voices = await VoicesManager.create()
        return voices.voices
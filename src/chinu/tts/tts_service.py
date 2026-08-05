"""Text-to-Speech service for Chinu AI."""

import asyncio

from chinu.config.config_loader import SettingsConfig
from chinu.core.interfaces.events import IEventBus
from chinu.logging_system.logger import get_logger
from chinu.tts.interfaces import ITextToSpeechService
from chinu.voice.tts.edge_tts import EdgeTTS

logger = get_logger("tts_service")


class TextToSpeechService(ITextToSpeechService):
    """Service for converting text to speech."""

    def __init__(self, event_bus: IEventBus, config: SettingsConfig) -> None:
        """Initialize the TextToSpeechService."""
        self._event_bus = event_bus
        self._config = config.tts
        self._tts_engine = EdgeTTS(config.tts.edge_tts)
        self._is_running = False

    async def start(self) -> None:
        """Start the TTS service and subscribe to brain responses."""
        if self._is_running:
            logger.warning("TTS service is already running.")
            return

        logger.info("Starting TTS service...")
        await self._event_bus.subscribe_async("brain.response", self._handle_brain_response)
        self._is_running = True
        logger.info("TTS service started.")

    async def stop(self) -> None:
        """Stop the TTS service and unsubscribe from brain responses."""
        if not self._is_running:
            logger.warning("TTS service is not running.")
            return

        logger.info("Stopping TTS service...")
        await self._event_bus.unsubscribe_async("brain.response", self._handle_brain_response)
        await self._tts_engine.stop()
        self._is_running = False
        logger.info("TTS service stopped.")

    async def say(self, text: str, interrupt: bool = False) -> None:
        """Add text to the speech queue.

        Args:
            text: The text to speak.
            interrupt: Whether to interrupt the current speech.
        """
        if interrupt:
            await self._tts_engine.stop()
        await self._tts_engine.speak(text)

    async def set_voice(self, voice: str) -> None:
        """Set the voice for the TTS engine.

        Args:
            voice: The name of the voice to use.
        """
        self._tts_engine.config.voice = voice
        logger.info(f"TTS voice set to: {voice}")

    async def _handle_brain_response(self, response: dict) -> None:
        """Handle brain responses and speak the text."""
        text_to_speak = response.get("text")
        if text_to_speak:
            await self.say(text_to_speak)
"""Voice Service for Chinu AI."""

import asyncio

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

    async def start(self) -> None:
        """Start the voice service."""
        if self._is_running:
            logger.warning("Voice service is already running.")
            return

        logger.info("Voice Service Started")
        self._is_running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        """Stop the voice service."""
        if not self._is_running or not self._task:
            logger.warning("Voice service is not running.")
            return

        logger.info("Stopping voice service...")
        self._is_running = False
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        logger.info("Voice service stopped.")

    async def _run(self) -> None:
        """Main loop for the voice service."""
        while self._is_running:
            if self._config.app.debug:
                logger.info("Voice Runtime Alive")
            await asyncio.sleep(1)
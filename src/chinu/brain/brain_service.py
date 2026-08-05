"""Brain service for Chinu AI."""

import asyncio

from chinu.brain.intent.intent_classifier import Intent, IntentClassifier
from chinu.core.interfaces.events import IEventBus
from chinu.logging_system.logger import get_logger

logger = get_logger("brain_service")


class BrainService:
    """Manages intent classification and response generation."""

    def __init__(self, event_bus: IEventBus) -> None:
        """Initialize the BrainService.

        Args:
            event_bus: The application's event bus.
        """
        self._event_bus = event_bus
        self._intent_classifier = IntentClassifier()
        self._is_running = False

    async def start(self) -> None:
        """Start the brain service and subscribe to events."""
        if self._is_running:
            logger.warning("BrainService is already running.")
            return

        logger.info("Starting BrainService...")
        self._is_running = True
        await self._event_bus.subscribe_async("voice.transcribed", self.handle_transcription)
        logger.info("BrainService started and subscribed to 'voice.transcribed'.")

    async def stop(self) -> None:
        """Stop the brain service and unsubscribe from events."""
        if not self._is_running:
            logger.warning("BrainService is not running.")
            return

        logger.info("Stopping BrainService...")
        self._is_running = False
        await self._event_bus.unsubscribe_async("voice.transcribed", self.handle_transcription)
        logger.info("BrainService stopped.")

    async def handle_transcription(self, event_data: dict) -> None:
        """Handle the 'voice.transcribed' event.

        Args:
            event_data: The data from the 'voice.transcribed' event.
        """
        text = event_data.get("text")
        if not text:
            logger.warning("Received transcription event with no text.")
            return

        logger.info(f"Processing transcribed text: '{text}'")
        intent = self._intent_classifier.classify(text)
        logger.info(f"Classified intent as: {intent.name}")

        response_data = {"intent": intent.name, "text": text}
        await self._event_bus.publish_async("brain.response", response_data)
        logger.info(f"Published 'brain.response' with data: {response_data}")
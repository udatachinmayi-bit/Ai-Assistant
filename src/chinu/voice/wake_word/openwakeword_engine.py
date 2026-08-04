"""OpenWakeWord wake word engine implementation."""

import asyncio
from typing import TYPE_CHECKING

import numpy as np
import openwakeword

from chinu.logging_system.logger import get_logger
from chinu.voice.wake_word.config import OpenWakeWordConfig

if TYPE_CHECKING:
    from chinu.core.event_bus import EventBus

logger = get_logger("openwakeword")


class OpenWakeWordEngine:
    """Wake word engine using the openwakeword library."""

    def __init__(self, config: OpenWakeWordConfig, event_bus: "EventBus") -> None:
        """Initialize the OpenWakeWord engine.

        Args:
            config: Configuration for the wake word engine.
            event_bus: The application's event bus for publishing events.
        """
        self.config = config
        self.event_bus = event_bus
        self._model = self._load_model()
        self._is_running = False
        self._task: asyncio.Task | None = None

    def _load_model(self) -> openwakeword.Model:
        """Load the OpenWakeWord models."""
        logger.info("Loading OpenWakeWord models...")
        try:
            # Create custom wake word models
            openwakeword.create_custom_wake_word_model(
                self.config.wake_phrases,
                output_path="hey_chinu.onnx",
                metadata={"name": "Hey Chinu", "author": "Chinu AI"},
            )
            model = openwakeword.Model(
                wake_word_models=["hey_chinu.onnx"],
                inference_framework=self.config.inference_framework,
            )
            logger.info("OpenWakeWord models loaded successfully.")
            return model
        except Exception as e:
            logger.error(f"Failed to load OpenWakeWord models: {e}", exc_info=True)
            raise

    def process_audio(self, audio: np.ndarray) -> None:
        """Process a chunk of audio to detect a wake word.

        Args:
            audio: A NumPy array containing the audio data (int16).
        """
        if not self._is_running:
            return

        prediction = self._model.predict(audio)
        for model_name, score in prediction.items():
            if score > 0.5:  # Threshold for detection
                asyncio.create_task(self._publish_detection_event(model_name, score))

    async def _publish_detection_event(self, model_name: str, score: float) -> None:
        """Publish a wake word detection event to the event bus."""
        event_data = {"model_name": model_name, "score": score}
        logger.info("Wake word detected", **event_data)
        await self.event_bus.publish("wake_word.detected", event_data)

    def start(self) -> None:
        """Start the wake word detection engine."""
        if not self._is_running:
            self._is_running = True
            logger.info("Wake word engine started.")

    def stop(self) -> None:
        """Stop the wake word detection engine."""
        if self._is_running:
            self._is_running = False
            logger.info("Wake word engine stopped.")
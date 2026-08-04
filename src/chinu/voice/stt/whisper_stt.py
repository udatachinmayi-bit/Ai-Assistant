"""Faster-Whisper Speech-to-Text (STT) engine implementation."""

import numpy as np
import torch
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment, Word

from chinu.logging_system.logger import get_logger
from chinu.voice.stt.config import WhisperConfig

logger = get_logger("whisper_stt")


class WhisperSTT:
    """Speech-to-Text engine using the Faster-Whisper library."""

    def __init__(self, config: WhisperConfig) -> None:
        """Initialize the Whisper STT engine.

        Args:
            config: Configuration object for the STT engine.
        """
        self.config = config
        self._device = self._setup_device()
        self.model = self._load_model()

    def _setup_device(self) -> str:
        """Determine the best available device for inference."""
        if self.config.device == "auto":
            if torch.cuda.is_available():
                logger.info("CUDA is available. Using GPU for STT.")
                return "cuda"
            else:
                logger.info("CUDA not available. Using CPU for STT.")
                return "cpu"
        return self.config.device

    def _load_model(self) -> WhisperModel:
        """Load the Faster-Whisper model into memory."""
        logger.info(
            "Loading Whisper model...",
            model_size=self.config.model_size,
            device=self._device,
            compute_type=self.config.compute_type,
        )
        try:
            model = WhisperModel(
                self.config.model_size,
                device=self._device,
                compute_type=self.config.compute_type,
            )
            logger.info("Whisper model loaded successfully.")
            return model
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}", exc_info=True)
            raise

    def transcribe(
        self, audio: np.ndarray, language: str | None = None
    ) -> tuple[list[Segment], list[Word]]:
        """Transcribe an audio segment.

        Args:
            audio: NumPy array containing the audio data (float32).
            language: Optional language code for transcription.

        Returns:
            A tuple containing the list of segments and word-level timestamps.
        """
        lang = language or self.config.language
        segments, _ = self.model.transcribe(
            audio,
            language=lang,
            word_timestamps=True,
        )
        all_segments = list(segments)
        all_words: list[Word] = []
        for segment in all_segments:
            if segment.words:
                all_words.extend(segment.words)

        return all_segments, all_words
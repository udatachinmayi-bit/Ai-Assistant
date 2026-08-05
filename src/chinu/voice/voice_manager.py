"""Voice pipeline manager for Chinu AI."""

import asyncio
import queue
import tempfile
import wave
from threading import Thread

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

from chinu.config.settings import VoiceSettings
from chinu.core.interfaces.events import IEventBus
from chinu.logging_system.logger import get_logger
from chinu.voice.interfaces import IVoiceManager

logger = get_logger("voice_manager")


class VoiceManager(IVoiceManager):
    """Manages the voice pipeline, including microphone input and STT."""

    def __init__(self, event_bus: IEventBus, config: VoiceSettings) -> None:
        """Initialize the VoiceManager.

        Args:
            event_bus: The application's event bus.
            config: The voice settings.
        """
        self._event_bus = event_bus
        self._config = config
        self._is_running = False
        self._worker_thread: Thread | None = None
        self._audio_queue: queue.Queue = queue.Queue()

        # Initialize the STT model
        logger.info(f"Loading STT model: {self._config.stt_model_path}")
        self._model = WhisperModel(
            self._config.stt_model_path,
            device=self._config.stt_device,
            compute_type=self._config.stt_compute_type,
        )
        logger.info("STT model loaded successfully.")

    async def start(self) -> None:
        """Start the voice pipeline."""
        if self._is_running:
            logger.warning("VoiceManager is already running.")
            return

        logger.info("Starting VoiceManager...")
        self._is_running = True
        self._worker_thread = Thread(target=self._run, daemon=True)
        self._worker_thread.start()
        logger.info("VoiceManager started.")

    async def stop(self) -> None:
        """Stop the voice pipeline."""
        if not self._is_running:
            logger.warning("VoiceManager is not running.")
            return

        logger.info("Stopping VoiceManager...")
        self._is_running = False
        if self._worker_thread:
            self._worker_thread.join()
        logger.info("VoiceManager stopped.")

    def _audio_callback(self, indata: np.ndarray, frames: int, time, status) -> None:
        """This is called (from a separate thread) for each audio block."""
        if status:
            logger.warning(f"Sounddevice status: {status}")
        self._audio_queue.put(bytes(indata))

    def _run(self) -> None:
        """Main worker loop for the voice pipeline."""
        try:
            with sd.RawInputStream(
                samplerate=self._config.mic_sample_rate,
                blocksize=self._config.mic_block_size,
                device=self._config.mic_device,
                channels=self._config.mic_channels,
                dtype="int16",
                callback=self._audio_callback,
            ):
                logger.info("Microphone is now listening...")
                while self._is_running:
                    self._process_audio()
        except Exception as e:
            logger.error(f"An error occurred in the voice pipeline: {e}")
        finally:
            logger.info("Microphone has stopped listening.")

    def _process_audio(self) -> None:
        """Process audio from the queue and transcribe it."""
        try:
            audio_data = self._audio_queue.get(timeout=1)
            with tempfile.NamedTemporaryFile(
                delete=True, suffix=".wav", mode="w+b"
            ) as temp_audio_file:
                self._write_to_wav(temp_audio_file, audio_data)
                segments, _ = self._model.transcribe(
                    temp_audio_file.name, beam_size=5
                )
                transcribed_text = "".join(segment.text for segment in segments)

                if transcribed_text.strip():
                    logger.info(f"Transcribed text: {transcribed_text}")
                    asyncio.run(
                        self._event_bus.publish_async(
                            "voice.transcribed", {"text": transcribed_text}
                        )
                    )
        except queue.Empty:
            pass  # No audio to process
        except Exception as e:
            logger.error(f"Error processing audio: {e}")

    def _write_to_wav(self, file, audio_data: bytes) -> None:
        """Write audio data to a WAV file."""
        with wave.open(file, "wb") as wf:
            wf.setnchannels(self._config.mic_channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self._config.mic_sample_rate)
            wf.writeframes(audio_data)
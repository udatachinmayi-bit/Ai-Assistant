"""Voice Service for Chinu AI."""

import asyncio
import queue
import string  # ADD THIS IMPORT
import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from rapidfuzz import fuzz

from chinu.actions.action_router import ActionRouter
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
        
        # Initialize Whisper model
        whisper_model_name = self._config.voice.whisper_model
        logger.info(f"Loading Whisper model: {whisper_model_name}")
        self.model = WhisperModel(
            whisper_model_name, 
            device="cpu", 
            compute_type="int8"
        )
        
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.record_duration = 3.0
        self.samples_per_chunk = int(self.sample_rate * self.record_duration)
        
        # Queue for audio data
        self.audio_queue = queue.Queue()
        
        # State
        self.last_transcription = ""
        self.transcription_time = 0
        
        # Wake word configuration
        self.wake_words = ["chinu", "sister"]
        self.wake_threshold = 70
        
        # Action Router
        self.router = ActionRouter()
        
        logger.info("✅ VoiceService initialized with ActionRouter")

    def _audio_callback(self, indata, frames, time_info, status) -> None:
        """Callback for sounddevice input stream."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())

    def _detect_wake_word(self, text: str) -> tuple[str | None, str]:
        """Detect if text contains a wake word using improved fuzzy matching."""
        if not text.strip():
            return None, ""
        
        words = text.lower().split()
        if not words:
            return None, ""
        
        # Check each word against wake words
        for i, word in enumerate(words):
            for wake in self.wake_words:
                # Use multiple fuzzy matching strategies
                scores = [
                    fuzz.ratio(word, wake),
                    fuzz.partial_ratio(word, wake),
                    fuzz.token_sort_ratio(word, wake),
                ]
                max_score = max(scores)
                
                if max_score >= self.wake_threshold:
                    # Found a match
                    command = " ".join(words[i+1:]) if i+1 < len(words) else ""
                    logger.debug(f"Wake word match: '{word}' → '{wake}' (score: {max_score})")
                    return wake, command
        
        return None, ""

    async def _handle_transcription(self, text: str) -> None:
        """Handle transcribed text - detect wake word and execute commands."""
        # Detect wake word
        wake_word, command_text = self._detect_wake_word(text)
        
        if wake_word:
            logger.info(f"🎯 Wake word '{wake_word}' detected!")
            
            if command_text:
                # CLEAN THE COMMAND - Remove punctuation and extra spaces
                command_text = command_text.lower().strip()
                command_text = command_text.translate(
                    str.maketrans("", "", string.punctuation)
                )
                command_text = " ".join(command_text.split())
                
                logger.info(f"📝 Command: '{command_text}'")
                
                # Execute the command using the router (synchronous)
                try:
                    result = self.router.execute(command_text)
                    if result:
                        logger.info(f"✅ Command executed successfully: '{command_text}'")
                    else:
                        logger.warning(f"❌ Failed to execute command: '{command_text}'")
                except Exception as e:
                    logger.error(f"Error executing command: {e}")
            else:
                logger.info("👂 Listening for command...")
        else:
            logger.debug(f"Ignored: '{text}' (no wake word)")

    async def _process_audio_chunk(self) -> None:
        """Process a single audio chunk - record and transcribe."""
        audio_chunks = []
        samples_collected = 0
        
        while samples_collected < self.samples_per_chunk and self._is_running:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
                audio_chunks.append(chunk)
                samples_collected += len(chunk)
            except queue.Empty:
                await asyncio.sleep(0.01)
                continue
        
        if not audio_chunks or not self._is_running:
            return
        
        # Combine chunks
        audio_np = np.concatenate(audio_chunks, axis=0).flatten()
        
        # Convert to float32 for Whisper
        audio_float32 = audio_np.astype(np.float32) / 32768.0
        
        # Transcribe
        try:
            segments, _ = self.model.transcribe(
                audio_float32,
                language=None,  # Auto-detect language (supports multiple languages)
                beam_size=1,
                vad_filter=False,
                temperature=0.0
            )
            
            transcription = " ".join(segment.text for segment in segments)
            
            if transcription.strip():
                logger.info(f"📝 Transcribed: '{transcription}'")
                await self._handle_transcription(transcription)
            else:
                logger.debug("No speech detected")
                
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")

    async def _process_audio_loop(self) -> None:
        """Main loop that continuously processes audio chunks."""
        logger.info("🔄 Voice processing loop started")
        logger.info(f"🎤 Recording {self.record_duration} second chunks at {self.sample_rate}Hz")
        
        while self._is_running:
            try:
                await self._process_audio_chunk()
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
                await asyncio.sleep(0.1)
        
        logger.info("Voice processing loop ended")

    async def start(self) -> None:
        """Start the voice service."""
        if self._is_running:
            logger.warning("Voice service is already running.")
            return

        logger.info("🎤 Starting Voice Service...")
        
        try:
            # Start the input stream
            self.stream = sd.InputStream(
                callback=self._audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype="int16",
                blocksize=int(self.sample_rate * 0.1),
            )
            self.stream.start()
            logger.info("✅ Microphone opened successfully.")
            
            self._is_running = True
            self._task = asyncio.create_task(self._process_audio_loop())
            logger.info("✅ Voice Service Started")
            logger.info("💡 Say 'Chinu' followed by a command (e.g., 'Chinu open Chrome')")
            
        except Exception as e:
            logger.error(f"Failed to start voice service: {e}")
            raise

    async def stop(self) -> None:
        """Stop the voice service."""
        if not self._is_running:
            logger.warning("Voice service is not running.")
            return

        logger.info("Stopping voice service...")
        self._is_running = False
        
        if hasattr(self, 'stream'):
            try:
                self.stream.stop()
                self.stream.close()
                logger.info("Microphone stream closed.")
            except Exception as e:
                logger.error(f"Error closing audio stream: {e}")
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Error during task cancellation: {e}")
        
        logger.info("Voice service stopped.")

    async def _run(self) -> None:
        """Legacy method - kept for compatibility."""
        await self._process_audio_loop()
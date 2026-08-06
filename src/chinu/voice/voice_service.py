"""Voice Service for Chinu AI."""

import asyncio
import queue
import random
import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from rapidfuzz import fuzz

from chinu.actions.action_router import ActionRouter
from chinu.actions.action_result import ActionResult
from chinu.capabilities.capability_manager import CapabilityManager
from chinu.config.config_loader import SettingsConfig
from chinu.conversation.conversation_manager import ConversationManager
from chinu.logging_system.logger import get_logger
from chinu.nlu.intent_parser import IntentParser
from chinu.personality import replies
from chinu.voice.interfaces import IVoiceService
from chinu.voice.speech_service import SpeechService

logger = get_logger("voice_service")


class VoiceService(IVoiceService):
    """Service for handling voice input and output."""

    def __init__(self, config: SettingsConfig) -> None:
        """Initialize the VoiceService."""
        self._config = config
        self._is_running = False
        self._task: asyncio.Task | None = None
        self._stream: sd.InputStream | None = None
        
        # Initialize Whisper model
        whisper_model_name = self._config.voice.whisper_model
        logger.info(f"Loading Whisper model: {whisper_model_name}")
        self.model = WhisperModel(whisper_model_name, device="cpu", compute_type="int8")
        
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
        self.wake_threshold = 80
        
        # Core components
        self.router = ActionRouter()
        self.intent_parser = IntentParser()
        self.speech = SpeechService()
        self.conversation_manager = ConversationManager()
        self.capability_manager = CapabilityManager()
        
        # Personality
        self.is_speaking = False
        
        logger.info("✅ VoiceService initialized with all components")

    def _audio_callback(self, indata, frames, time_info, status) -> None:
        """Callback for sounddevice input stream."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        if not self.is_speaking:
            self.audio_queue.put(indata.copy())

    def _detect_wake_word(self, text: str) -> tuple[str | None, str]:
        """Detect if text contains a wake word."""
        if not text.strip():
            return None, ""
        
        words = text.lower().split()
        if not words:
            return None, ""
        
        for i, word in enumerate(words):
            for wake in self.wake_words:
                if fuzz.ratio(word, wake) >= self.wake_threshold:
                    command = " ".join(words[i+1:]) if i+1 < len(words) else ""
                    return wake, command
        
        return None, ""

    def _generate_reply(self, action_result: ActionResult) -> str:
        """Generates a spoken reply based on the action result."""
        action = action_result.action
        target = action_result.target
        query = action_result.query
        
        if action == "open_app" or action == "open_website":
            reply_template = random.choice(replies.OPEN_REPLIES)
            return reply_template.format(target=target)
        elif action == "google_search":
            reply_template = random.choice(replies.SEARCH_REPLIES)
            return reply_template.format(query=query)
        elif action == "youtube_play":
            reply_template = random.choice(replies.PLAY_REPLIES)
            return reply_template.format(query=query)
        elif action_result.success:
            return random.choice(replies.DONE_REPLIES)
        else:
            return random.choice(replies.ERROR_REPLIES)

    async def _handle_transcription(self, text: str) -> None:
        """Handle transcribed text."""
        if self.conversation_manager.is_active:
            self.conversation_manager.reset_timer()
            await self._process_command(text)
        else:
            wake_word, command_text = self._detect_wake_word(text)
            if wake_word:
                logger.info(f"🎯 Wake word: '{wake_word}'")
                await self.conversation_manager.start_conversation()
                
                if command_text:
                    await self._process_command(command_text)
                else:
                    self.is_speaking = True
                    await self.speech.speak(random.choice(replies.GREETING_REPLIES))
                    self.is_speaking = False
            else:
                logger.debug(f"Ignored: '{text}' (no wake word)")

    async def _process_command(self, command_text: str) -> None:
        """Process a command after wake word or during conversation."""
        logger.info(f"💬 Command: '{command_text}'")
        
        try:
            intent = self.intent_parser.parse(command_text)
            logger.info(f"🧠 Intent: {intent}")
            
            if intent['intent'] == "get_capabilities":
                description = self.capability_manager.get_capabilities_description()
                self.is_speaking = True
                await self.speech.speak(description)
                self.is_speaking = False
                return

            if intent['intent'] != "unknown":
                action_result = self.router.execute(intent)
                reply = self._generate_reply(action_result)
                
                self.is_speaking = True
                await self.speech.speak(reply)
                self.is_speaking = False
            else:
                self.is_speaking = True
                await self.speech.speak(random.choice(replies.ERROR_REPLIES))
                self.is_speaking = False
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            self.is_speaking = True
            await self.speech.speak(random.choice(replies.ERROR_REPLIES))
            self.is_speaking = False

    async def _process_audio_chunk(self) -> None:
        """Process a single audio chunk."""
        try:
            # Collect audio data
            audio_data = []
            samples_needed = self.samples_per_chunk
            collected = 0
            
            while collected < samples_needed:
                try:
                    chunk = self.audio_queue.get(timeout=0.5)
                    audio_data.append(chunk)
                    collected += len(chunk)
                except queue.Empty:
                    if not self._is_running:
                        return
                    continue
            
            if not audio_data:
                return
                
            # Combine audio chunks
            audio_array = np.concatenate(audio_data, axis=0)
            
            # Convert from (N,1) to (N,) - Whisper requires 1D array
            audio_array = audio_array.flatten()
            
            # Debug log to verify shape
            logger.info(f"Audio Shape: {audio_array.shape}, ndim={audio_array.ndim}")
            
            # Convert to float32 for Whisper
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Transcribe with auto-detection
            segments, _ = self.model.transcribe(
                audio_float,
                language=None,
                vad_filter=True,
                vad_parameters=dict(
                    threshold=0.5,
                    min_speech_duration_ms=250,
                    min_silence_duration_ms=500,
                )
            )
            
            # Process transcription
            for segment in segments:
                text = segment.text.strip()
                if text:
                    logger.info(f"📝 Transcription: '{text}'")
                    await self._handle_transcription(text)
                    
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}", exc_info=True)

    async def _process_audio_loop(self) -> None:
        """Main loop that continuously processes audio chunks."""
        logger.info("🔄 Voice processing loop started")
        
        while self._is_running:
            try:
                await self._process_audio_chunk()
            except Exception as e:
                logger.exception(f"Error in audio processing loop: {e}")
                await asyncio.sleep(0.1)

    async def start(self) -> None:
        """Start the voice service."""
        if self._is_running:
            logger.warning("Voice service is already running")
            return
        
        logger.info("🎤 Starting Voice Service...")
        
        try:
            # Initialize audio stream
            self._stream = sd.InputStream(
                callback=self._audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype="int16",
                blocksize=int(self.sample_rate * 0.1),
            )
            
            self._stream.start()
            logger.info("✅ Microphone opened successfully.")
            
            self._is_running = True
            
            # Start the processing loop
            self._task = asyncio.create_task(self._process_audio_loop())
            
            logger.info("✅ Voice Service Started")
            
        except Exception as e:
            logger.error(f"Failed to start voice service: {e}", exc_info=True)
            raise

    async def stop(self) -> None:
        """Stop the voice service."""
        if not self._is_running:
            logger.warning("Voice service is not running")
            return
        
        logger.info("🛑 Stopping Voice Service...")
        
        self._is_running = False
        
        # Stop and close audio stream
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
                logger.info("✅ Audio stream closed")
            except Exception as e:
                logger.error(f"Error closing audio stream: {e}")
        
        # Cancel the processing task
        if self._task and not self._task.done():
            try:
                self._task.cancel()
                await self._task
                logger.info("✅ Processing task cancelled")
            except asyncio.CancelledError:
                logger.info("✅ Processing task cancelled successfully")
            except Exception as e:
                logger.error(f"Error cancelling task: {e}")
        
        # Clear audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        logger.info("✅ Voice Service Stopped")
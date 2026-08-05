"""Voice Service for Chinu AI."""

import asyncio
import queue
import subprocess
import time
from pathlib import Path

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
        self.record_duration = 3.0  # Record 3 seconds at a time
        self.samples_per_chunk = int(self.sample_rate * self.record_duration)
        
        # Rolling window settings
        self.rolling_window_size = self.samples_per_chunk
        self.audio_buffer = np.array([], dtype=np.int16)
        
        # Queue for audio data
        self.audio_queue = queue.Queue()
        
        # State
        self.last_transcription = ""
        self.transcription_time = 0
        
        # Wake word configuration
        self.wake_words = ["chinu", "sister"]
        self.wake_threshold = 70  # Fuzzy match threshold (0-100)
        
        # Action Router
        self.action_router = ActionRouter()

    def _audio_callback(self, indata, frames, time_info, status) -> None:
        """Callback for sounddevice input stream."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())

    def _detect_wake_word(self, text: str) -> tuple[str | None, str]:
        """Detect if text contains a wake word using fuzzy matching."""
        if not text.strip():
            return None, ""
        
        words = text.lower().split()
        if not words:
            return None, ""
        
        first_word = words[0]
        
        # Check each wake word
        for wake in self.wake_words:
            # Check if first word matches wake word (fuzzy)
            if fuzz.ratio(first_word, wake) >= self.wake_threshold:
                # Return the matched wake word and the rest of the command
                command = " ".join(words[1:]) if len(words) > 1 else ""
                return wake, command
            
            # Also check if any word in the text contains the wake word
            if any(fuzz.ratio(word, wake) >= self.wake_threshold for word in words):
                # Find the position of the matched word
                for i, word in enumerate(words):
                    if fuzz.ratio(word, wake) >= self.wake_threshold:
                        command = " ".join(words[i+1:]) if i+1 < len(words) else ""
                        return wake, command
        
        return None, ""

    def _find_command(self, text: str) -> str | None:
        """Find a matching command in the text."""
        text_lower = text.lower().strip()
        
        # Check each command
        for command_name, triggers in self.commands.items():
            for trigger in triggers:
                if trigger in text_lower:
                    return command_name
        
        return None

    def _execute_command(self, command: str) -> bool:
        """Execute a command on Windows."""
        logger.info(f"Executing command: {command}")
        
        try:
            if command == "open chrome":
                subprocess.Popen(["start", "chrome"], shell=True)
                logger.info("✅ Opening Chrome...")
                return True
                
            elif command == "open edge":
                subprocess.Popen(["start", "microsoft-edge:"], shell=True)
                logger.info("✅ Opening Edge...")
                return True
                
            elif command == "open vscode":
                subprocess.Popen(["code"], shell=True)
                logger.info("✅ Opening VS Code...")
                return True
                
            elif command == "open notepad":
                subprocess.Popen(["notepad.exe"], shell=True)
                logger.info("✅ Opening Notepad...")
                return True
                
            elif command == "open calculator":
                subprocess.Popen(["calc.exe"], shell=True)
                logger.info("✅ Opening Calculator...")
                return True
                
            elif command == "open whatsapp":
                # Try to open WhatsApp from start menu
                subprocess.Popen(["start", "whatsapp:"], shell=True)
                logger.info("✅ Opening WhatsApp...")
                return True
                
            elif command == "open youtube":
                subprocess.Popen(["start", "https://www.youtube.com"], shell=True)
                logger.info("✅ Opening YouTube...")
                return True
                
            elif command == "open spotify":
                subprocess.Popen(["start", "spotify:"], shell=True)
                logger.info("✅ Opening Spotify...")
                return True
                
            elif command == "open terminal":
                subprocess.Popen(["start", "cmd"], shell=True)
                logger.info("✅ Opening Terminal...")
                return True
                
            elif command == "open file explorer":
                subprocess.Popen(["explorer.exe"], shell=True)
                logger.info("✅ Opening File Explorer...")
                return True
                
            elif command == "open settings":
                subprocess.Popen(["start", "ms-settings:"], shell=True)
                logger.info("✅ Opening Settings...")
                return True
                
            else:
                logger.warning(f"Unknown command: {command}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to execute command '{command}': {e}")
            return False

    async def _process_audio_chunk(self) -> None:
        """Process a single audio chunk - record and transcribe."""
        # Collect audio for 3 seconds
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
                language="en",
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

    async def _handle_transcription(self, text: str) -> None:
        """Handle transcribed text - detect wake word and execute commands."""
        # Detect wake word
        wake_word, command_text = self._detect_wake_word(text)
        
        if wake_word:
            logger.info(f"🎯 Wake word '{wake_word}' detected!")
            
            if command_text:
                logger.info(f"📝 Command: '{command_text}'")
                
                # Find and execute the command
                command = self._find_command(command_text)
                if command:
                    success = self._execute_command(command)
                    if success:
                        logger.info(f"✅ Command '{command}' executed successfully")
                    else:
                        logger.warning(f"❌ Failed to execute command '{command}'")
                else:
                    logger.info(f"🤔 Unknown command: '{command_text}'")
                    # Here you could add AI response for unknown commands
            else:
                logger.info("👂 Listening for command...")
        else:
            logger.debug(f"Ignored: '{text}' (no wake word)")

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
                blocksize=int(self.sample_rate * 0.1),  # 100ms chunks
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
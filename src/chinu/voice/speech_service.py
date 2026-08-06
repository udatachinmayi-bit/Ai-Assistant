"""
Speech Service for Chinu AI.

This module provides a class to generate and play speech using Microsoft Edge's
Neural Text-to-Speech (TTS) service.
"""

import asyncio
import os
import tempfile

import edge_tts
from edge_tts import VoicesManager
from playsound3 import playsound

from chinu.logging_system.logger import get_logger

logger = get_logger("speech_service")


class SpeechService:
    """A class to handle text-to-speech generation and playback."""

    def __init__(self, voice: str = "en-US-AvaNeural"):
        """
        Initializes the SpeechService.

        Args:
            voice: The name of the Edge TTS voice to use.
        """
        self.voice = voice
        logger.info(f"✅ SpeechService initialized with voice: {self.voice}")

    async def speak(self, text: str) -> None:
        """
        Generates speech from text, saves it to a temporary file, plays it,
        and then deletes the file.

        Args:
            text: The text to be spoken.
        """
        try:
            # Generate the speech
            logger.info(f"Generating speech: {text}")
            communicate = edge_tts.Communicate(text, self.voice)
            
            # Save to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_path = temp_audio.name
            
            await communicate.save(temp_path)
            logger.info("Speech generated successfully.")
            
            # Play the audio file
            logger.info("Playing speech...")
            await asyncio.to_thread(
                playsound,
                temp_path
            )
            logger.info("Speech finished.")

        except Exception as e:
            logger.error(f"Failed to speak text '{text}': {e}", exc_info=True)
        finally:
            # Clean up the temporary file
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    logger.info("Deleting temporary speech file...")
                    os.remove(temp_path)
                except Exception as e:
                    logger.error(f"Failed to delete temporary audio file {temp_path}: {e}")

    async def get_available_voices(self):
        """Returns a list of available voices."""
        voices = await VoicesManager.create()
        return voices.find()
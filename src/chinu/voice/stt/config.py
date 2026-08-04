"""Configuration for the Faster-Whisper Speech-to-Text engine."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class WhisperConfig(BaseModel):
    """Configuration for the Whisper STT engine.

    Attributes:
        model_size: Size of the Whisper model to use (e.g., "tiny", "base", "small").
        device: Device to use for inference ("auto", "cpu", "cuda").
        compute_type: Type of computation to use (e.g., "float16", "int8").
        language: Language code for transcription (e.g., "en", "es").
    """

    model_size: str = Field(
        default="base",
        description="Size of the Whisper model (e.g., 'tiny', 'base', 'small', 'medium', 'large-v2').",
    )
    device: Literal["auto", "cpu", "cuda"] = Field(
        default="auto",
        description="Device to use for inference ('auto', 'cpu', 'cuda').",
    )
    compute_type: Literal["float16", "int8", "int8_float16", "float32"] = Field(
        default="float16",
        description="Type of computation to use (e.g., 'float16', 'int8').",
    )
    language: Optional[str] = Field(
        default="en",
        description="Language code for transcription (e.g., 'en', 'es').",
    )
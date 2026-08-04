"""Configuration for the Edge-TTS Text-to-Speech engine."""

from pydantic import BaseModel, Field


class EdgeTTSConfig(BaseModel):
    """Configuration for the Edge-TTS engine.

    Attributes:
        voice: The voice to use for speech synthesis.
        rate: The speaking rate (e.g., "+20%").
        volume: The volume level (e.g., "+10%").
    """

    voice: str = Field(
        default="en-US-AriaNeural",
        description="The voice to use for speech synthesis.",
    )
    rate: str = Field(
        default="+0%",
        description="The speaking rate (e.g., '+20%%').",
    )
    volume: str = Field(
        default="+0%",
        description="The volume level (e.g., '+10%%').",
    )
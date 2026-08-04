"""Configuration for the OpenWakeWord wake word engine."""

from pydantic import BaseModel, Field


class OpenWakeWordConfig(BaseModel):
    """Configuration for the OpenWakeWord engine.

    Attributes:
        wake_phrases: A list of custom wake phrases to detect.
        inference_framework: The inference framework to use ('onnx' or 'tflite').
    """

    wake_phrases: list[str] = Field(
        default=["Hey Chinu", "Hello Chinu", "Okay Chinu"],
        description="A list of custom wake phrases to detect.",
    )
    inference_framework: str = Field(
        default="onnx",
        description="The inference framework to use ('onnx' or 'tflite').",
    )
"""Configuration loader module for Chinu AI.

Provides strongly typed configuration settings loaded from YAML files,
dotenv files (.env), and environment variable overrides.
"""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from chinu.core.interfaces.exceptions import ConfigurationError


class AppConfig(BaseModel):
    """General application settings."""

    name: str = Field(default="Chinu AI", description="Application name")
    environment: str = Field(default="development", description="Runtime environment")


class VoiceConfig(BaseModel):
    """Voice module configuration settings."""

    wake_word: str = Field(default="hey_chinu", description="Active wake word trigger")
    stt_engine: str = Field(default="faster_whisper", description="Speech-to-text engine")
    tts_engine: str = Field(default="edge_tts", description="Text-to-speech engine")
    stt_model_path: str = Field(default="tiny.en", description="Path to the STT model")
    stt_device: str = Field(default="cpu", description="Device for STT model (e.g., 'cpu', 'cuda')")
    stt_compute_type: str = Field(default="int8", description="Compute type for STT model")
    mic_device: int | None = Field(default=None, description="Microphone device index")
    mic_sample_rate: int = Field(default=16000, description="Microphone sample rate")
    mic_block_size: int = Field(default=1024, description="Microphone block size")
    mic_channels: int = Field(default=1, description="Microphone channels")


class BrainConfig(BaseModel):
    """AI Brain module configuration settings."""

    llm_provider: str = Field(default="anthropic", description="LLM provider name")


class AutomationConfig(BaseModel):
    """Automation engine configuration settings."""

    confirmation_required: bool = Field(
        default=True, description="Require user confirmation for high-risk actions"
    )


class DashboardConfig(BaseModel):
    """Dashboard module configuration settings."""

    host: str = Field(default="127.0.0.1", description="Host binding for dashboard API")
    port: int = Field(default=8765, description="Port number for dashboard API")


class LoggingConfig(BaseModel):
    """Logging system configuration settings."""

    level: str = Field(default="INFO", description="Global log level")
    file_path: str = Field(default="logs/chinu.log", description="Log file output path")
    log_to_console: bool = Field(default=True, description="Enable stdout console logging")


class EdgeTTSConfig(BaseModel):
    """Edge-TTS specific settings."""
    voice: str = Field(default="en-US-AriaNeural", description="Voice to use for speech synthesis")
    rate: str = Field(default="+0%", description="Speaking rate adjustment")
    volume: str = Field(default="+0%", description="Speaking volume adjustment")


class TTSConfig(BaseModel):
    """Text-to-Speech configuration settings."""
    provider: str = Field(default="edge_tts", description="TTS provider to use")
    edge_tts: EdgeTTSConfig = Field(default_factory=EdgeTTSConfig)


class SettingsConfig(BaseSettings):
    """Root configuration model combining all module settings."""

    app: AppConfig = Field(default_factory=AppConfig)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    brain: BrainConfig = Field(default_factory=BrainConfig)
    automation: AutomationConfig = Field(default_factory=AutomationConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


class ConfigLoader:
    """Handles loading, parsing, and caching application settings."""

    def __init__(self, default_yaml_path: Path | str | None = None) -> None:
        """Initialize ConfigLoader with optional default YAML path.

        Args:
            default_yaml_path: Optional path to settings YAML file.
        """
        if default_yaml_path is None:
            self._yaml_path = Path(__file__).parent / "settings.yaml"
        else:
            self._yaml_path = Path(default_yaml_path)

        self._cached_settings: SettingsConfig | None = None

    def load_config(self, yaml_path: Path | str | None = None) -> SettingsConfig:
        """Load configuration from YAML file, .env, and environment variables.

        Args:
            yaml_path: Optional explicit YAML file path to load from.

        Returns:
            SettingsConfig instance with all validated settings.

        Raises:
            ConfigurationError: If YAML file is malformed or path is invalid.
        """
        target_path = Path(yaml_path) if yaml_path is not None else self._yaml_path
        file_data: dict[str, Any] = {}

        if target_path.exists():
            try:
                with open(target_path, encoding="utf-8") as f:
                    content = yaml.safe_load(f)
                    if isinstance(content, dict):
                        file_data = content
            except Exception as exc:
                raise ConfigurationError(
                    f"Failed to parse configuration file '{target_path}': {exc}",
                    details={"path": str(target_path)},
                ) from exc
        elif yaml_path is not None:
            raise ConfigurationError(
                f"Configuration file not found: '{target_path}'",
                details={"path": str(target_path)},
            )

        try:
            settings = SettingsConfig(**file_data)
            self._cached_settings = settings
            return settings
        except Exception as exc:
            raise ConfigurationError(
                f"Validation error in configuration: {exc}",
                details={"file_data": file_data},
            ) from exc

    def get_config(self) -> SettingsConfig:
        """Get currently cached configuration or load default if not cached.

        Returns:
            SettingsConfig instance.
        """
        if self._cached_settings is None:
            return self.load_config()
        return self._cached_settings


_default_loader = ConfigLoader()


def get_config(yaml_path: Path | str | None = None) -> SettingsConfig:
    """Convenience function to get settings using the default loader.

    Args:
        yaml_path: Optional YAML path override.

    Returns:
        SettingsConfig instance.
    """
    if yaml_path is not None:
        return ConfigLoader(yaml_path).load_config()
    return _default_loader.get_config()
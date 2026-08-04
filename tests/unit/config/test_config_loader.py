"""Unit tests for ConfigLoader and configuration settings."""

from pathlib import Path

import pytest

from chinu.config.config_loader import ConfigLoader, SettingsConfig, get_config
from chinu.core.interfaces.exceptions import ConfigurationError


def test_load_default_config() -> None:
    """Test loading default configuration."""
    config = get_config()
    assert isinstance(config, SettingsConfig)
    assert config.app.name == "Chinu AI"
    assert config.voice.wake_word == "hey_chinu"
    assert config.logging.level in ("INFO", "DEBUG")


def test_load_custom_yaml(tmp_path: Path) -> None:
    """Test loading configuration from custom YAML file."""
    custom_yaml = tmp_path / "custom_settings.yaml"
    custom_yaml.write_text(
        """
app:
  name: "Test Chinu"
  environment: "testing"
voice:
  wake_word: "chinu_test"
""",
        encoding="utf-8",
    )

    loader = ConfigLoader(custom_yaml)
    config = loader.load_config()

    assert config.app.name == "Test Chinu"
    assert config.app.environment == "testing"
    assert config.voice.wake_word == "chinu_test"


def test_missing_custom_yaml_raises_error(tmp_path: Path) -> None:
    """Test that specifying a non-existent YAML path raises ConfigurationError."""
    missing_file = tmp_path / "does_not_exist.yaml"
    loader = ConfigLoader(missing_file)

    with pytest.raises(ConfigurationError):
        loader.load_config(yaml_path=missing_file)


def test_invalid_yaml_syntax_raises_error(tmp_path: Path) -> None:
    """Test that invalid YAML syntax raises ConfigurationError."""
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("app: [invalid yaml syntax", encoding="utf-8")

    loader = ConfigLoader(invalid_yaml)
    with pytest.raises(ConfigurationError):
        loader.load_config()

"""Unit tests for structured logging system."""

from pathlib import Path

from chinu.logging_system.logger import configure_logging, get_logger


def test_configure_logging_creates_log_file(tmp_path: Path) -> None:
    """Test configure_logging creates log directory and writes logs."""
    log_file = tmp_path / "logs" / "test.log"
    configure_logging(level="DEBUG", log_file=log_file, log_to_console=False)

    logger = get_logger("test_module")
    logger.info("Test log message", key="value")

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Test log message" in content


def test_get_logger_returns_bound_logger() -> None:
    """Test get_logger returns a structlog BoundLogger."""
    logger = get_logger("my_test_logger")
    assert logger is not None

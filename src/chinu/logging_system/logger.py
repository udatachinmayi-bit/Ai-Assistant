"""Centralized structured logging system for Chinu AI.

Configures structlog and standard library logging with console and file handlers.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Any

import structlog

_LOGGING_CONFIGURED = False


def configure_logging(
    level: str = "INFO",
    log_file: Path | str | None = None,
    log_to_console: bool = True,
) -> None:
    """Configure structlog and stdlib logging handlers and formatters.

    Args:
        level: Logging level string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        log_file: Optional path to log file. If provided, file parent dirs are created.
        log_to_console: Whether to log to standard console output.
    """
    global _LOGGING_CONFIGURED

    log_level = getattr(logging, level.upper(), logging.INFO)

    handlers: list[logging.Handler] = []

    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        handlers.append(console_handler)

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True,
    )

    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            (
                structlog.dev.ConsoleRenderer(colors=True)
                if log_to_console
                else structlog.processors.JSONRenderer()
            ),
        ],
    )

    for handler in handlers:
        handler.setFormatter(formatter)

    _LOGGING_CONFIGURED = True


def get_logger(name: str | None = None) -> Any:
    """Get a structlog logger instance.

    Args:
        name: Optional module/logger name.

    Returns:
        structlog BoundLogger instance.
    """
    if not _LOGGING_CONFIGURED:
        configure_logging()
    return structlog.get_logger(name)

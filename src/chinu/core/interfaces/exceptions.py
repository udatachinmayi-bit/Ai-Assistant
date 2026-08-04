"""Core exception types for Chinu AI.

All custom exceptions across the application inherit from ChinuError.
"""

from typing import Any


class ChinuError(Exception):
    """Base exception class for all Chinu AI errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize ChinuError.

        Args:
            message: Explanation of the error.
            details: Optional contextual metadata about the error.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(ChinuError):
    """Raised when configuration loading or validation fails."""


class ContainerError(ChinuError):
    """Raised when dependency resolution or registration fails in the DI container."""


class ServiceNotFoundError(ContainerError):
    """Raised when a requested service is not registered in the DI container/registry."""


class EventBusError(ChinuError):
    """Raised when event publication or subscription fails."""


class LifecycleError(ChinuError):
    """Raised when a lifecycle hook execution or transition fails."""


class PluginError(ChinuError):
    """Base class for errors occurring in the plugin system."""


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load, validate, or initialize."""

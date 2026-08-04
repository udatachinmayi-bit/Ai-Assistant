"""Core Engine package for Chinu AI.

Exposes application engine, event bus, DI container, service registry,
and lifecycle manager using lazy imports to prevent circular dependency cycles.
"""

from typing import Any

__all__ = [
    "Application",
    "ChinuEngine",
    "Container",
    "EventBus",
    "LifecycleManager",
    "ServiceRegistry",
]


def __getattr__(name: str) -> Any:
    """Lazy module attribute getter.

    Args:
        name: Attribute name.

    Returns:
        The requested class or attribute.

    Raises:
        AttributeError: If attribute is unknown.
    """
    if name == "Application":
        from chinu.core.application import Application

        return Application
    if name == "ChinuEngine":
        from chinu.core.engine import ChinuEngine

        return ChinuEngine
    if name == "Container":
        from chinu.core.container import Container

        return Container
    if name == "EventBus":
        from chinu.core.event_bus import EventBus

        return EventBus
    if name == "LifecycleManager":
        from chinu.core.lifecycle import LifecycleManager

        return LifecycleManager
    if name == "ServiceRegistry":
        from chinu.core.service_registry import ServiceRegistry

        return ServiceRegistry

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

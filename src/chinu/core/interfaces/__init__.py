"""Core interfaces and contracts for Chinu AI.

This package defines protocols, base exception types, and data models
consumed across all application modules.
"""

from chinu.core.interfaces.events import Event, EventHandler, IEventBus
from chinu.core.interfaces.exceptions import (
    ChinuError,
    ConfigurationError,
    ContainerError,
    EventBusError,
    LifecycleError,
    PluginError,
    PluginLoadError,
    ServiceNotFoundError,
)
from chinu.core.interfaces.lifecycle import ILifecycleManager, LifecycleHook, LifecycleStage
from chinu.core.interfaces.services import IContainer, IServiceRegistry

__all__ = [
    "ChinuError",
    "ConfigurationError",
    "ContainerError",
    "ServiceNotFoundError",
    "EventBusError",
    "LifecycleError",
    "PluginError",
    "PluginLoadError",
    "Event",
    "EventHandler",
    "IEventBus",
    "IContainer",
    "IServiceRegistry",
    "LifecycleStage",
    "LifecycleHook",
    "ILifecycleManager",
]

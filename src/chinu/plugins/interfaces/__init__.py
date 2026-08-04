"""Plugin interface contracts for Chinu AI."""

from chinu.plugins.interfaces.plugin import (
    IPlugin,
    IPluginLoader,
    PluginMetadata,
    PluginResult,
)

__all__ = [
    "IPlugin",
    "IPluginLoader",
    "PluginMetadata",
    "PluginResult",
]

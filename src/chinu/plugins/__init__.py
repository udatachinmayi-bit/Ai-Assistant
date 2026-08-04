"""Plugin system package for Chinu AI."""

from chinu.plugins.interfaces.plugin import (
    IPlugin,
    IPluginLoader,
    PluginMetadata,
    PluginResult,
)
from chinu.plugins.plugin_manager.loader import PluginLoader

__all__ = [
    "IPlugin",
    "IPluginLoader",
    "PluginMetadata",
    "PluginResult",
    "PluginLoader",
]

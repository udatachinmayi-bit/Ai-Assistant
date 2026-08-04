"""Plugin metadata, result models, and plugin interfaces for Chinu AI."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass
class PluginMetadata:
    """Metadata describing a plugin's identity, version, and capabilities.

    Attributes:
        name: Unique plugin identifier.
        version: Version string (semver).
        description: Short description of plugin functionality.
        author: Plugin author name/organization.
        dependencies: Dictionary of other plugin names to required semver ranges.
        required_chinu_version: Semver range for the required Chinu core version.
        capabilities: List of intent/capability strings this plugin handles.
        permissions: List of required permissions (e.g. 'filesystem', 'browser').
    """

    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    dependencies: dict[str, str] = field(default_factory=dict)
    required_chinu_version: str = "*"
    capabilities: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)


@dataclass
class PluginResult:
    """Result returned by a plugin execution.

    Attributes:
        success: Whether execution was successful.
        data: Execution output payload.
        error: Error message string if success is False.
    """

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class IPlugin(ABC):
    """Abstract base class defining contract for all Chinu plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata descriptor."""

    async def setup(self) -> None:
        """Lifecycle hook called when plugin is loaded/initialized.

        Can be overridden by subclasses for async resource acquisition.
        """
        return None

    async def teardown(self) -> None:
        """Lifecycle hook called when plugin is unloaded/shut down.

        Can be overridden by subclasses for cleanup.
        """
        return None

    @abstractmethod
    async def execute(self, intent: str, context: dict[str, Any]) -> PluginResult:
        """Execute a capability action handled by this plugin.

        Args:
            intent: Intent name or action identifier.
            context: Context dictionary passed from Automation Engine.

        Returns:
            PluginResult instance.
        """


@runtime_checkable
class IPluginLoader(Protocol):
    """Protocol for plugin loading and management interface."""

    def discover_plugins(self, plugins_dir: Path | str) -> list[PluginMetadata]:
        """Discover available plugins in the specified directory without instantiating.

        Args:
            plugins_dir: Directory path containing plugins.

        Returns:
            List of PluginMetadata objects for discovered plugins.
        """
        ...

    async def load_plugin(self, plugin_path: Path | str) -> IPlugin:
        """Load and instantiate a plugin from its directory or file path.

        Args:
            plugin_path: Path to plugin directory or module file.

        Returns:
            Instantiated and set up IPlugin instance.
        """
        ...

    async def unload_plugin(self, plugin_name: str) -> None:
        """Unload and teardown a plugin by name.

        Args:
            plugin_name: Unique plugin name.
        """
        ...

    def get_plugin(self, plugin_name: str) -> IPlugin | None:
        """Retrieve a loaded plugin instance by name.

        Args:
            plugin_name: Unique plugin name.

        Returns:
            IPlugin instance if loaded, None otherwise.
        """
        ...

    def list_plugins(self) -> list[IPlugin]:
        """List all currently loaded plugin instances.

        Returns:
            List of loaded IPlugin instances.
        """
        ...
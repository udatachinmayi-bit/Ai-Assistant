"""High-level plugin manager for Chinu AI."""

from pathlib import Path
from typing import Dict, List, Set

from semantic_version import SimpleSpec, Version

from chinu.core.interfaces.exceptions import PluginError
from chinu.logging_system.logger import get_logger
from chinu.plugins.interfaces.plugin import IPlugin, PluginMetadata
from chinu.plugins.plugin_manager.loader import PluginLoader

logger = get_logger("plugin_manager")


class PluginManager:
    """Manages plugin discovery, validation, and lifecycle."""

    def __init__(self, plugin_dir: str, chinu_version: str) -> None:
        """Initialize the PluginManager.

        Args:
            plugin_dir: The directory to scan for plugins.
            chinu_version: The current version of the Chinu application.
        """
        self.plugin_dir = Path(plugin_dir)
        self.chinu_version = Version(chinu_version)
        self.loader = PluginLoader()
        self.available_plugins: Dict[str, PluginMetadata] = {}
        self.enabled_plugins: Set[str] = set()

    def scan_plugins(self) -> None:
        """Scan the plugin directory to find all available plugins."""
        logger.info("Scanning for plugins...", directory=str(self.plugin_dir))
        discovered = self.loader.discover_plugins(self.plugin_dir)
        self.available_plugins = {p.name: p for p in discovered}
        logger.info(f"Found {len(self.available_plugins)} available plugins.")

    async def enable_plugin(self, plugin_name: str) -> None:
        """Enable and load a single plugin after validation."""
        if plugin_name not in self.available_plugins:
            raise PluginError(f"Plugin '{plugin_name}' not found.")

        if plugin_name in self.enabled_plugins:
            logger.warning(f"Plugin '{plugin_name}' is already enabled.")
            return

        metadata = self.available_plugins[plugin_name]
        self._validate_plugin(metadata)

        # Assuming discover_plugins gives enough info to find the plugin file/dir
        # This might need adjustment based on the loader's implementation details.
        plugin_path = self._find_plugin_path(metadata.name)
        if not plugin_path:
            raise PluginError(f"Could not find path for plugin '{metadata.name}'.")

        await self.loader.load_plugin(plugin_path)
        self.enabled_plugins.add(plugin_name)
        logger.info(f"Successfully enabled plugin '{plugin_name}'.")

    async def disable_plugin(self, plugin_name: str) -> None:
        """Disable and unload a single plugin."""
        if plugin_name not in self.enabled_plugins:
            logger.warning(f"Plugin '{plugin_name}' is not currently enabled.")
            return

        await self.loader.unload_plugin(plugin_name)
        self.enabled_plugins.remove(plugin_name)
        logger.info(f"Successfully disabled plugin '{plugin_name}'.")

    def _validate_plugin(self, metadata: PluginMetadata) -> None:
        """Validate a plugin's dependencies and version requirements."""
        logger.debug(f"Validating plugin '{metadata.name}'.")
        self._check_chinu_version(metadata)
        self._check_dependencies(metadata)

    def _check_chinu_version(self, metadata: PluginMetadata) -> None:
        """Check if the plugin is compatible with the current Chinu version."""
        spec = SimpleSpec(metadata.required_chinu_version)
        if self.chinu_version not in spec:
            raise PluginError(
                f"Plugin '{metadata.name}' requires Chinu version {spec}, but current is {self.chinu_version}."
            )

    def _check_dependencies(self, metadata: PluginMetadata) -> None:
        """Check if all of the plugin's dependencies are met."""
        for dep_name, dep_spec_str in metadata.dependencies.items():
            if dep_name not in self.available_plugins:
                raise PluginError(
                    f"Plugin '{metadata.name}' has an unmet dependency: '{dep_name}' is not available."
                )

            dep_metadata = self.available_plugins[dep_name]
            dep_version = Version(dep_metadata.version)
            dep_spec = SimpleSpec(dep_spec_str)

            if dep_version not in dep_spec:
                raise PluginError(
                    f"Plugin '{metadata.name}' requires '{dep_name}' version {dep_spec}, but found {dep_version}."
                )

    def _find_plugin_path(self, plugin_name: str) -> Path | None:
        """Find the file path for a given plugin name."""
        # This is a simplified search. A real implementation might need a more robust
        # mapping from plugin name to path, stored during discovery.
        for item in self.plugin_dir.iterdir():
            if item.name == plugin_name or item.stem == plugin_name:
                return item
        return None

    def get_loaded_plugins(self) -> List[IPlugin]:
        """Get a list of all currently loaded and enabled plugin instances."""
        return self.loader.list_plugins()
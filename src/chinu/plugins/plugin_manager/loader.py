"""Plugin loader implementation for discovering and loading Chinu plugins."""

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any

from chinu.core.interfaces.exceptions import PluginError, PluginLoadError
from chinu.logging_system.logger import get_logger
from chinu.plugins.interfaces.plugin import (
    IPlugin,
    IPluginLoader,
    PluginMetadata,
)

logger = get_logger("plugin_loader")


class PluginLoader(IPluginLoader):
    """Discovers, dynamic loads, and manages lifecycle of Chinu plugins."""

    def __init__(self) -> None:
        """Initialize empty plugin storage."""
        self._loaded_plugins: dict[str, IPlugin] = {}

    def _find_plugin_class(self, module: Any) -> type[IPlugin]:
        """Inspect a module to find a class inheriting from IPlugin.

        Args:
            module: Dynamically loaded Python module.

        Returns:
            Class type implementing IPlugin.

        Raises:
            PluginLoadError: If no IPlugin subclass is found in module.
        """
        for _name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, IPlugin) and obj is not IPlugin:
                return obj

        raise PluginLoadError(
            f"No subclass of IPlugin found in module '{module.__name__}'",
            details={"module": module.__name__},
        )

    def _load_module_from_path(self, file_path: Path) -> Any:
        """Dynamically load Python module from file path.

        Args:
            file_path: Path to .py file or plugin directory package.

        Returns:
            Loaded module object.
        """
        if file_path.is_dir():
            init_py = file_path / "__init__.py"
            plugin_py = file_path / "plugin.py"
            if plugin_py.exists():
                file_path = plugin_py
            elif init_py.exists():
                file_path = init_py
            else:
                raise PluginLoadError(
                    f"No plugin.py or __init__.py found in directory '{file_path}'"
                )

        module_name = f"chinu_plugin_{file_path.stem}_{hash(str(file_path)) & 0xffffffff:x}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Could not create spec for plugin at '{file_path}'")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        except Exception as exc:
            if isinstance(exc, PluginLoadError):
                raise
            raise PluginLoadError(f"Failed to load plugin module at '{file_path}': {exc}") from exc

    def discover_plugins(self, plugins_dir: Path | str) -> list[PluginMetadata]:
        """Discover available plugins in target directory without initializing them.

        Args:
            plugins_dir: Root path containing plugin subdirectories or modules.

        Returns:
            List of PluginMetadata objects for discovered plugins.
        """
        dir_path = Path(plugins_dir)
        if not dir_path.exists() or not dir_path.is_dir():
            logger.warning("Plugin discovery directory does not exist", path=str(dir_path))
            return []

        discovered: list[PluginMetadata] = []

        for item in dir_path.iterdir():
            if item.name.startswith((".", "_")):
                continue
            if item.is_dir() or (item.is_file() and item.suffix == ".py"):
                try:
                    module = self._load_module_from_path(item)
                    cls_type = self._find_plugin_class(module)
                    instance = cls_type()
                    discovered.append(instance.metadata)
                except Exception as exc:
                    logger.debug(
                        "Skipping candidate plugin during discovery",
                        path=str(item),
                        reason=str(exc),
                    )

        return discovered

    async def load_plugin(self, plugin_path: Path | str) -> IPlugin:
        """Load, instantiate, and setup a plugin from file or folder path.

        Args:
            plugin_path: Path to plugin file or directory.

        Returns:
            Configured and initialized IPlugin instance.
        """
        path = Path(plugin_path)
        logger.info("Loading plugin from path", path=str(path))

        module = self._load_module_from_path(path)
        plugin_cls = self._find_plugin_class(module)

        try:
            instance = plugin_cls()
            meta = instance.metadata

            if meta.name in self._loaded_plugins:
                logger.warning("Plugin with name already loaded, replacing", name=meta.name)
                await self.unload_plugin(meta.name)

            await instance.setup()
            self._loaded_plugins[meta.name] = instance
            logger.info("Successfully loaded plugin", name=meta.name, version=meta.version)
            return instance
        except Exception as exc:
            if isinstance(exc, PluginError):
                raise
            raise PluginLoadError(f"Error initializing plugin at '{path}': {exc}") from exc

    async def load_all_plugins(self, plugins_dir: Path | str) -> list[IPlugin]:
        """Load all plugins found in specified directory.

        Args:
            plugins_dir: Path to directory containing plugins.

        Returns:
            List of loaded IPlugin instances.
        """
        dir_path = Path(plugins_dir)
        if not dir_path.exists() or not dir_path.is_dir():
            logger.warning("Plugins directory not found", path=str(dir_path))
            return []

        loaded: list[IPlugin] = []
        for item in dir_path.iterdir():
            if item.name.startswith((".", "_")):
                continue
            if item.is_dir() or (item.is_file() and item.suffix == ".py"):
                try:
                    plugin = await self.load_plugin(item)
                    loaded.append(plugin)
                except Exception as exc:
                    logger.error("Failed to load plugin", path=str(item), error=str(exc))

        return loaded

    async def unload_plugin(self, plugin_name: str) -> None:
        """Unload and teardown a plugin by name.

        Args:
            plugin_name: Unique plugin name.
        """
        if plugin_name in self._loaded_plugins:
            plugin = self._loaded_plugins[plugin_name]
            try:
                await plugin.teardown()
            except Exception as exc:
                logger.error("Error tearing down plugin", name=plugin_name, error=str(exc))
            finally:
                del self._loaded_plugins[plugin_name]
                logger.info("Unloaded plugin", name=plugin_name)

    async def unload_all_plugins(self) -> None:
        """Unload and teardown all loaded plugins."""
        for name in list(self._loaded_plugins.keys()):
            await self.unload_plugin(name)

    def get_plugin(self, plugin_name: str) -> IPlugin | None:
        """Retrieve a loaded plugin instance by name.

        Args:
            plugin_name: Unique plugin name.

        Returns:
            IPlugin instance if loaded, None otherwise.
        """
        return self._loaded_plugins.get(plugin_name)

    def list_plugins(self) -> list[IPlugin]:
        """List all currently loaded plugin instances.

        Returns:
            List of loaded IPlugin instances.
        """
        return list(self._loaded_plugins.values())

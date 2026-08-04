"""Unit tests for PluginLoader."""

from pathlib import Path
from typing import Any

import pytest

from chinu.plugins.interfaces.plugin import IPlugin, PluginMetadata, PluginResult
from chinu.plugins.plugin_manager.loader import PluginLoader


class SampleMockPlugin(IPlugin):
    """Mock plugin implementation for testing loader."""

    def __init__(self) -> None:
        self.setup_called = False
        self.teardown_called = False

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="mock_plugin",
            version="1.0.0",
            description="Mock plugin for testing",
            capabilities=["test_intent"],
        )

    async def setup(self) -> None:
        self.setup_called = True

    async def teardown(self) -> None:
        self.teardown_called = True

    async def execute(self, intent: str, context: dict[str, Any]) -> PluginResult:
        return PluginResult(success=True, data={"echo": intent})


@pytest.mark.asyncio
async def test_plugin_load_and_unload(tmp_path: Path) -> None:
    """Test loading and unloading plugin from directory package."""
    plugin_dir = tmp_path / "mock_plugin"
    plugin_dir.mkdir()

    plugin_code = """
from chinu.plugins.interfaces.plugin import IPlugin, PluginMetadata, PluginResult
from typing import Any

class MockPlugin(IPlugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(name="dir_mock_plugin", version="0.1.0")

    async def execute(self, intent: str, context: dict[str, Any]) -> PluginResult:
        return PluginResult(success=True, data={"status": "ok"})
"""
    (plugin_dir / "plugin.py").write_text(plugin_code, encoding="utf-8")

    loader = PluginLoader()
    plugin = await loader.load_plugin(plugin_dir)

    assert plugin is not None
    assert plugin.metadata.name == "dir_mock_plugin"
    assert loader.get_plugin("dir_mock_plugin") is plugin
    assert len(loader.list_plugins()) == 1

    await loader.unload_plugin("dir_mock_plugin")
    assert loader.get_plugin("dir_mock_plugin") is None
    assert len(loader.list_plugins()) == 0

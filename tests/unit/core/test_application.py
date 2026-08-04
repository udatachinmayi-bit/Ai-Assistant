"""Unit tests for Application Engine and ChinuEngine."""

import asyncio
from pathlib import Path

import pytest

from chinu.core.application import Application
from chinu.core.engine import ChinuEngine
from chinu.core.interfaces.events import Event
from chinu.core.interfaces.lifecycle import LifecycleStage


def test_application_bootstrap() -> None:
    """Test Application bootstrapping registers core services."""
    app = Application()
    app.bootstrap()

    assert app.config is not None
    assert app.container.has("config") or app.container.has(type(app.config))
    assert app.service_registry.has("config")
    assert app.service_registry.has("event_bus")


@pytest.mark.asyncio
async def test_application_start_and_stop() -> None:
    """Test Application start and stop lifecycle and events."""
    app = Application()
    events: list[str] = []

    def on_started(evt: Event) -> None:
        events.append("started")

    def on_stopping(evt: Event) -> None:
        events.append("stopping")

    app.event_bus.subscribe("app.started", on_started)
    app.event_bus.subscribe("app.stopping", on_stopping)

    await app.start()
    assert app.lifecycle.stage == LifecycleStage.RUNNING
    assert "started" in events

    await app.stop()
    assert app.lifecycle.stage == LifecycleStage.STOPPED
    assert "stopping" in events


def test_chinu_engine_alias() -> None:
    """Test ChinuEngine is identical to Application."""
    assert ChinuEngine is Application


def test_core_init_lazy_imports() -> None:
    """Test importing attributes lazily from chinu.core package."""
    import chinu.core as core

    assert core.Application is not None
    assert core.ChinuEngine is not None
    assert core.Container is not None
    assert core.EventBus is not None
    assert core.LifecycleManager is not None
    assert core.ServiceRegistry is not None

    with pytest.raises(AttributeError):
        _ = core.NonExistentAttr


@pytest.mark.asyncio
async def test_application_run_async(tmp_path: Path) -> None:
    """Test Application run_async method."""
    config_path = tmp_path / "settings.yaml"
    config_path.write_text("app:\n  name: AsyncTest\n", encoding="utf-8")

    app = Application(config_path=config_path)

    async def trigger_shutdown() -> None:
        await asyncio.sleep(0.01)
        await app.stop()

    asyncio.create_task(trigger_shutdown())
    await app.run_async()

    assert app.lifecycle.stage == LifecycleStage.STOPPED

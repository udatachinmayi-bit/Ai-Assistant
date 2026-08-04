"""Unit tests for LifecycleManager."""

import pytest

from chinu.core.interfaces.exceptions import LifecycleError
from chinu.core.interfaces.lifecycle import LifecycleStage
from chinu.core.lifecycle import LifecycleManager


@pytest.mark.asyncio
async def test_lifecycle_startup_and_shutdown() -> None:
    """Test priority ordered startup and shutdown hooks execution."""
    mgr = LifecycleManager()
    events: list[str] = []

    def startup_1() -> None:
        events.append("start_p1")

    async def startup_0() -> None:
        events.append("start_p0")

    def shutdown_1() -> None:
        events.append("stop_p1")

    async def shutdown_0() -> None:
        events.append("stop_p0")

    mgr.add_startup_hook(startup_1, priority=1)
    mgr.add_startup_hook(startup_0, priority=0)

    mgr.add_shutdown_hook(shutdown_1, priority=1)
    mgr.add_shutdown_hook(shutdown_0, priority=0)

    assert mgr.stage == LifecycleStage.UNINITIALIZED

    await mgr.startup()
    assert mgr.stage == LifecycleStage.RUNNING
    assert events == ["start_p0", "start_p1"]

    await mgr.shutdown()
    assert mgr.stage == LifecycleStage.STOPPED
    assert events == ["start_p0", "start_p1", "stop_p0", "stop_p1"]


@pytest.mark.asyncio
async def test_failing_startup_hook_sets_failed_stage() -> None:
    """Test failing startup hook transitions stage to FAILED and raises LifecycleError."""
    mgr = LifecycleManager()

    def bad_hook() -> None:
        raise ValueError("Startup crash")

    mgr.add_startup_hook(bad_hook)

    with pytest.raises(LifecycleError):
        await mgr.startup()

    assert mgr.stage == LifecycleStage.FAILED

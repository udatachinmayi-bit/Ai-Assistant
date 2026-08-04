"""Lifecycle state and interface definitions for application lifecycle management."""

from collections.abc import Awaitable, Callable
from enum import Enum, auto
from typing import Protocol, runtime_checkable

LifecycleHook = Callable[[], None | Awaitable[None]]


class LifecycleStage(Enum):
    """Stages of application lifecycle."""

    UNINITIALIZED = auto()
    BOOTSTRAPPING = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()


@runtime_checkable
class ILifecycleManager(Protocol):
    """Protocol for Lifecycle Manager."""

    @property
    def stage(self) -> LifecycleStage:
        """Get current lifecycle stage."""
        ...

    def add_startup_hook(
        self, hook: LifecycleHook, priority: int = 0, name: str | None = None
    ) -> None:
        """Register a hook to execute during startup.

        Args:
            hook: Sync or async callback function.
            priority: Priority order (lower numbers execute first).
            name: Optional human-readable name for logging.
        """
        ...

    def add_shutdown_hook(
        self, hook: LifecycleHook, priority: int = 0, name: str | None = None
    ) -> None:
        """Register a hook to execute during shutdown.

        Args:
            hook: Sync or async callback function.
            priority: Priority order (lower numbers execute first).
            name: Optional human-readable name for logging.
        """
        ...

    async def startup(self) -> None:
        """Execute all startup hooks in priority order and transition stage."""
        ...

    async def shutdown(self) -> None:
        """Execute all shutdown hooks in priority order and transition stage."""
        ...

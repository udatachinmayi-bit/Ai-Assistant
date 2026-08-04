"""Lifecycle Manager implementation for Chinu AI.

Manages application lifecycle state transitions, priority-ordered startup/shutdown
hooks, and signal registration for graceful shutdown.
"""

import asyncio
import inspect
import signal
from collections.abc import Callable
from dataclasses import dataclass

from chinu.core.interfaces.exceptions import LifecycleError
from chinu.core.interfaces.lifecycle import (
    ILifecycleManager,
    LifecycleHook,
    LifecycleStage,
)
from chinu.logging_system.logger import get_logger

logger = get_logger("lifecycle")


@dataclass
class RegisteredHook:
    """Registered lifecycle hook with priority and metadata."""

    hook: LifecycleHook
    priority: int = 0
    name: str = ""


class LifecycleManager(ILifecycleManager):
    """Manages application startup/shutdown hooks and state transitions."""

    def __init__(self) -> None:
        """Initialize LifecycleManager in UNINITIALIZED stage."""
        self._stage: LifecycleStage = LifecycleStage.UNINITIALIZED
        self._startup_hooks: list[RegisteredHook] = []
        self._shutdown_hooks: list[RegisteredHook] = []
        self._shutdown_event: asyncio.Event = asyncio.Event()

    @property
    def stage(self) -> LifecycleStage:
        """Get current lifecycle stage."""
        return self._stage

    @property
    def shutdown_event(self) -> asyncio.Event:
        """Get asyncio.Event triggered when shutdown is requested."""
        return self._shutdown_event

    def add_startup_hook(
        self, hook: LifecycleHook, priority: int = 0, name: str | None = None
    ) -> None:
        """Register a hook to execute during startup.

        Args:
            hook: Synchronous or asynchronous callback function.
            priority: Priority order (lower numbers execute first).
            name: Optional descriptive name.
        """
        hook_name = str(name or getattr(hook, "__name__", str(hook)))
        self._startup_hooks.append(RegisteredHook(hook=hook, priority=priority, name=hook_name))
        logger.debug("Registered startup hook", name=hook_name, priority=priority)

    def add_shutdown_hook(
        self, hook: LifecycleHook, priority: int = 0, name: str | None = None
    ) -> None:
        """Register a hook to execute during shutdown.

        Args:
            hook: Synchronous or asynchronous callback function.
            priority: Priority order (lower numbers execute first).
            name: Optional descriptive name.
        """
        hook_name = name or getattr(hook, "__name__", str(hook))
        self._shutdown_hooks.append(RegisteredHook(hook=hook, priority=priority, name=hook_name))
        logger.debug("Registered shutdown hook", name=hook_name, priority=priority)

    async def _execute_hook(self, registered: RegisteredHook) -> None:
        """Execute a single lifecycle hook.

        Args:
            registered: RegisteredHook container.
        """
        logger.debug("Executing lifecycle hook", name=registered.name)
        if inspect.iscoroutinefunction(registered.hook):
            await registered.hook()
        else:
            res = registered.hook()
            if inspect.isawaitable(res):
                await res

    async def startup(self) -> None:
        """Execute all startup hooks in priority order and transition stage to RUNNING.

        Raises:
            LifecycleError: If a startup hook fails.
        """
        if self._stage in (LifecycleStage.STARTING, LifecycleStage.RUNNING):
            logger.warning("Application is already starting or running")
            return

        self._stage = LifecycleStage.STARTING
        logger.info("Application lifecycle stage transitioning to STARTING")

        sorted_hooks = sorted(self._startup_hooks, key=lambda h: h.priority)
        for registered in sorted_hooks:
            try:
                await self._execute_hook(registered)
            except Exception as exc:
                self._stage = LifecycleStage.FAILED
                logger.critical(
                    "Startup hook execution failed",
                    hook_name=registered.name,
                    error=str(exc),
                    exc_info=True,
                )
                raise LifecycleError(
                    f"Startup hook '{registered.name}' failed: {exc}",
                    details={"hook_name": registered.name},
                ) from exc

        self._stage = LifecycleStage.RUNNING
        logger.info("Application lifecycle stage transitioning to RUNNING")

    async def shutdown(self) -> None:
        """Execute all shutdown hooks in priority order and transition stage to STOPPED."""
        if self._stage in (LifecycleStage.STOPPING, LifecycleStage.STOPPED):
            logger.warning("Application is already stopping or stopped")
            return

        self._stage = LifecycleStage.STOPPING
        logger.info("Application lifecycle stage transitioning to STOPPING")
        self._shutdown_event.set()

        sorted_hooks = sorted(self._shutdown_hooks, key=lambda h: h.priority)
        for registered in sorted_hooks:
            try:
                await self._execute_hook(registered)
            except Exception as exc:
                logger.error(
                    "Shutdown hook execution failed",
                    hook_name=registered.name,
                    error=str(exc),
                    exc_info=True,
                )

        self._stage = LifecycleStage.STOPPED
        logger.info("Application lifecycle stage transitioning to STOPPED")

    def setup_signal_handlers(
        self,
        loop: asyncio.AbstractEventLoop | None = None,
        shutdown_callback: Callable[[], None] | None = None,
    ) -> None:
        """Setup OS signal handlers (SIGINT, SIGTERM) for graceful shutdown.

        Args:
            loop: Optional asyncio event loop.
            shutdown_callback: Optional sync or async callback invoked on signal.
        """
        if loop is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

        def handle_signal(sig_name: str) -> None:
            logger.info("Received termination signal", signal=sig_name)
            self._shutdown_event.set()
            if shutdown_callback and callable(shutdown_callback):
                res = shutdown_callback()
                if inspect.isawaitable(res) and loop is not None and loop.is_running():
                    loop.create_task(res)

        def _make_signal_callback(sig_name: str) -> Callable[[], None]:
            return lambda: handle_signal(sig_name)

        def _make_handler_callback(sig_name: str) -> Callable[[int, Any], None]:
            return lambda s, f: handle_signal(sig_name)

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                sig_name = sig.name
                if loop is not None and hasattr(loop, "add_signal_handler"):
                    try:
                        loop.add_signal_handler(sig, _make_signal_callback(sig_name))
                    except (NotImplementedError, RuntimeError):
                        # Windows event loop may not support add_signal_handler
                        signal.signal(sig, _make_handler_callback(sig_name))
                else:
                    signal.signal(sig, _make_handler_callback(sig_name))
            except Exception as exc:
                logger.debug("Could not attach signal handler", signal=sig.name, reason=str(exc))

"""Main assistant runtime service for Chinu AI."""

import asyncio

from chinu.core.interfaces.lifecycle import ILifecycleManager
from chinu.logging_system.logger import get_logger
from chinu.runtime.interfaces import IAssistantRuntime
from chinu.voice.interfaces import IVoiceManager
from chinu.brain.interfaces import IBrainService
from chinu.memory.interfaces import IMemoryService
from chinu.tts.interfaces import ITextToSpeechService

logger = get_logger("assistant_runtime")

class AssistantRuntime(IAssistantRuntime):
    """Orchestrates the main assistant services and keeps the application alive."""

    def __init__(
        self,
        lifecycle_manager: ILifecycleManager,
        voice_manager: IVoiceManager,
        brain_service: IBrainService,
        memory_service: IMemoryService,
        tts_service: ITextToSpeechService,
    ) -> None:
        """Initialize the AssistantRuntime.

        Args:
            lifecycle_manager: The application's lifecycle manager.
        """
        self._lifecycle = lifecycle_manager
        self._voice_manager = voice_manager
        self._brain_service = brain_service
        self._memory_service = memory_service
        self._tts_service = tts_service
        self._task: asyncio.Task | None = None

        # Register hooks to be called by the Application lifecycle
        self._lifecycle.add_startup_hook(self.start, priority=10)
        self._lifecycle.add_shutdown_hook(self.stop, priority=10)

    async def start(self) -> None:
        """Start the assistant runtime and keep it running."""
        if self._task is not None and not self._task.done():
            logger.warning("AssistantRuntime is already running.")
            return

        logger.info("AssistantRuntime is starting...")
        await self._voice_manager.start()
        await self._brain_service.start()
        await self._memory_service.start()
        await self._tts_service.start()
        self._task = asyncio.create_task(self._run())
        logger.info("AssistantRuntime has started.")

    async def stop(self) -> None:
        """Stop the assistant runtime."""
        if self._task is None or self._task.done():
            logger.warning("AssistantRuntime is not running or already stopped.")
            return

        logger.info("AssistantRuntime is stopping...")
        await self._tts_service.stop()
        await self._memory_service.stop()
        await self._brain_service.stop()
        await self._voice_manager.stop()
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass  # Expected on cancellation
        finally:
            self._task = None
            logger.info("AssistantRuntime has stopped.")

    async def _run(self) -> None:
        """Main loop to keep the assistant alive and coordinate services."""
        logger.info("Assistant is running and waiting for shutdown signal.")
        try:
            while True:
                # This loop will keep the service alive. In the future, it will
                # be used to coordinate the different assistant services.
                await asyncio.sleep(3600)  # Sleep for a long time
        except asyncio.CancelledError:
            logger.debug("AssistantRuntime run loop was cancelled.")
        finally:
            logger.info("Assistant shutdown complete.")
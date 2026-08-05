"""Unit tests for the AssistantRuntime service."""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from chinu.core.lifecycle import LifecycleManager
from chinu.runtime.assistant_runtime import AssistantRuntime


class TestAssistantRuntime(unittest.TestCase):
    """Test suite for the AssistantRuntime service."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.lifecycle_manager = MagicMock(spec=LifecycleManager)
        self.runtime = AssistantRuntime(lifecycle_manager=self.lifecycle_manager)

    def test_initialization_hooks(self) -> None:
        """Test that startup and shutdown hooks are registered on initialization."""
        self.lifecycle_manager.add_startup_hook.assert_called_once_with(
            self.runtime.start, priority=10
        )
        self.lifecycle_manager.add_shutdown_hook.assert_called_once_with(
            self.runtime.stop, priority=10
        )

    @patch("asyncio.create_task")
    def test_start_creates_task(self, mock_create_task: MagicMock) -> None:
        """Test that start() creates and starts the main asyncio task."""
        async def run_test() -> None:
            await self.runtime.start()
            mock_create_task.assert_called_once()
            self.assertIsNotNone(self.runtime._task)

        asyncio.run(run_test())

    def test_stop_cancels_task(self) -> None:
        """Test that stop() cancels the main asyncio task."""
        async def run_test() -> None:
            # Create a mock task and assign it
            self.runtime._task = AsyncMock()
            self.runtime._task.done.return_value = False

            await self.runtime.stop()

            # Check that the task was cancelled
            self.runtime._task.cancel.assert_called_once()

        asyncio.run(run_test())

    def test_run_main_loop(self) -> None:
        """Test the main _run loop to ensure it can be cancelled gracefully."""
        async def run_test() -> None:
            # Start the runtime in a cancellable way
            task = asyncio.create_task(self.runtime._run())
            await asyncio.sleep(0.01)  # Allow the loop to start
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass  # Expected

            # If it completes without hanging, the test passes
            self.assertTrue(task.done())

if __name__ == "__main__":
    unittest.main()
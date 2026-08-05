"""Core Application Engine class for Chinu AI.

Central orchestrator linking configuration, dependency injection, event bus,
service registry, plugin management, and lifecycle hooks.
"""

import asyncio
from pathlib import Path

from chinu.config.config_loader import ConfigLoader, SettingsConfig, get_config
from chinu.core.container import Container
from chinu.core.event_bus import EventBus
from chinu.core.interfaces.events import IEventBus
from chinu.core.interfaces.lifecycle import ILifecycleManager, LifecycleStage
from chinu.core.interfaces.services import IContainer, IServiceRegistry
from chinu.core.lifecycle import LifecycleManager
from chinu.core.service_registry import ServiceRegistry
from chinu.logging_system.logger import configure_logging, get_logger
from chinu.plugins.interfaces.plugin import IPluginLoader
from chinu.plugins.plugin_manager.loader import PluginLoader
from chinu.runtime.interfaces import IAssistantRuntime
from chinu.voice.interfaces import IVoiceService
from chinu.voice.voice_service import VoiceService

logger = get_logger("application")


class Application:
    """Core application engine for Chinu AI."""

    def __init__(self, config_path: Path | str | None = None) -> None:
        """Initialize Application engine container and subsystem instances.

        Args:
            config_path: Optional path to YAML configuration file.
        """
        self._config_path = config_path
        self._config: SettingsConfig | None = None
        self._container = Container()
        self._service_registry = ServiceRegistry()
        self._event_bus = EventBus()
        self._lifecycle = LifecycleManager()
        self._plugin_loader = PluginLoader()

    @property
    def config(self) -> SettingsConfig:
        """Get application configuration model."""
        if self._config is None:
            self._config = get_config(self._config_path)
        return self._config

    @property
    def container(self) -> Container:
        """Get dependency injection container."""
        return self._container

    @property
    def service_registry(self) -> ServiceRegistry:
        """Get service registry."""
        return self._service_registry

    @property
    def event_bus(self) -> EventBus:
        """Get event bus."""
        return self._event_bus

    @property
    def lifecycle(self) -> LifecycleManager:
        """Get lifecycle manager."""
        return self._lifecycle

    @property
    def plugin_loader(self) -> PluginLoader:
        """Get plugin loader."""
        return self._plugin_loader

    def bootstrap(self, config_path: Path | str | None = None) -> None:
        """Bootstrap system dependencies, logging, and dependency registrations.

        Args:
            config_path: Optional override path for settings YAML.
        """
        target_path = config_path or self._config_path
        self._config = ConfigLoader(target_path).load_config()

        configure_logging(
            level=self._config.logging.level,
            log_file=self._config.logging.file_path,
            log_to_console=self._config.logging.log_to_console,
        )

        logger.info(
            "Bootstrapping Chinu AI Engine",
            app_name=self._config.app.name,
            environment=self._config.app.environment,
        )

        # Register core instances in DI Container
        self._container.register_singleton(SettingsConfig, self._config)
        self._container.register_singleton(IContainer, self._container)
        self._container.register_singleton(IServiceRegistry, self._service_registry)
        self._container.register_singleton(IEventBus, self._event_bus)
        self._container.register_singleton(ILifecycleManager, self._lifecycle)
        self._container.register_singleton(IPluginLoader, self._plugin_loader)

        # Register runtime services
        # FIXED: VoiceService only takes config parameter
        self._container.register_singleton(
            IVoiceService,
            lambda: VoiceService(self._config)
        )

        # Register core instances in Service Registry
        self._service_registry.register("config", self._config, SettingsConfig)
        self._service_registry.register("container", self._container, IContainer)
        self._service_registry.register(
            "service_registry", self._service_registry, IServiceRegistry
        )
        self._service_registry.register("event_bus", self._event_bus, IEventBus)
        self._service_registry.register("lifecycle", self._lifecycle, ILifecycleManager)
        self._service_registry.register("plugin_loader", self._plugin_loader, IPluginLoader)

        self._event_bus.publish("app.bootstrapped", {"environment": self._config.app.environment})

    async def start(self) -> None:
        """Execute lifecycle startup sequence."""
        if self._lifecycle.stage == LifecycleStage.UNINITIALIZED:
            self.bootstrap()

        logger.info("Starting Chinu AI Engine")
        await self._lifecycle.startup()

        try:
            logger.info("Initializing Voice Service...")
            voice_service = self._container.resolve(IVoiceService)
            await voice_service.start()
            logger.info("Voice Service Started.")
        except Exception as e:
            logger.error(f"Failed to start Voice Service: {e}")
            await self.stop()
            return

        # Load installed plugins if plugins directory exists
        installed_plugins_dir = Path(__file__).parent.parent / "plugins" / "installed"
        if installed_plugins_dir.exists():
            await self._plugin_loader.load_all_plugins(installed_plugins_dir)

        await self._event_bus.publish_async("app.started")

    async def stop(self) -> None:
        """Execute graceful shutdown sequence."""
        logger.info("Stopping Chinu AI Engine")
        await self._event_bus.publish_async("app.stopping")

        try:
            voice_service = self._container.resolve(IVoiceService)
            await voice_service.stop()
        except Exception as e:
            logger.error(f"Failed to stop Voice Service gracefully: {e}")

        await self._plugin_loader.unload_all_plugins()
        await self._lifecycle.shutdown()

        await self._event_bus.publish_async("app.stopped")

    async def run_async(self) -> None:
        """Asynchronous execution entry point. Bootstraps, starts, waits for signal, and stops."""
        if self._lifecycle.stage == LifecycleStage.UNINITIALIZED:
            self.bootstrap()

        loop = asyncio.get_running_loop()
        self._lifecycle.setup_signal_handlers(
            loop=loop,
            shutdown_callback=lambda: asyncio.create_task(self.stop()),
        )

        await self.start()

        try:
            await self._lifecycle.shutdown_event.wait()
        finally:
            if self._lifecycle.stage not in (LifecycleStage.STOPPING, LifecycleStage.STOPPED):
                await self.stop()

    def run(self) -> None:
        """Synchronous entry point running the application inside asyncio event loop."""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
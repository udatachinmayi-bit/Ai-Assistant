"""Service Registry implementation for Chinu AI.

Provides a centralized service lookup registry.
"""

from typing import Any

from chinu.core.interfaces.exceptions import ServiceNotFoundError
from chinu.core.interfaces.services import IServiceRegistry
from chinu.logging_system.logger import get_logger

logger = get_logger("service_registry")


class ServiceRegistry(IServiceRegistry):
    """Centralized service registry for managing named application services."""

    def __init__(self) -> None:
        """Initialize empty service dictionary."""
        self._services: dict[str, Any] = {}
        self._interfaces: dict[str, type[Any]] = {}

    def register(self, name: str, service: Any, interface: type[Any] | None = None) -> None:
        """Register a service by name and optional interface.

        Args:
            name: Service registration name.
            service: Service instance.
            interface: Optional interface type for verification.
        """
        if interface is not None and not isinstance(service, interface):
            logger.warning(
                "Registered service does not explicitly inherit from specified interface",
                service_name=name,
                interface=interface.__name__,
            )

        self._services[name] = service
        if interface is not None:
            self._interfaces[name] = interface

        logger.debug("Registered service in registry", name=name)

    def get(self, name: str) -> Any:
        """Retrieve a service by name.

        Args:
            name: Service registration name.

        Returns:
            Service instance.

        Raises:
            ServiceNotFoundError: If name is not registered.
        """
        if name not in self._services:
            raise ServiceNotFoundError(
                f"Service '{name}' not found in registry.",
                details={"service_name": name},
            )
        return self._services[name]

    def has(self, name: str) -> bool:
        """Check if a service is registered.

        Args:
            name: Service registration name.

        Returns:
            True if registered, False otherwise.
        """
        return name in self._services

    def unregister(self, name: str) -> None:
        """Unregister a service by name.

        Args:
            name: Service registration name.
        """
        if name in self._services:
            del self._services[name]
            if name in self._interfaces:
                del self._interfaces[name]
            logger.debug("Unregistered service from registry", name=name)

    def clear(self) -> None:
        """Clear all service registrations."""
        self._services.clear()
        self._interfaces.clear()
        logger.debug("Cleared Service Registry")

"""Dependency Injection Container implementation for Chinu AI.

Supports registering singletons, factories, and transient components, with resolution
by type or string keys.
"""

from collections.abc import Callable
from typing import Any, TypeVar

from chinu.core.interfaces.exceptions import ServiceNotFoundError
from chinu.core.interfaces.services import IContainer
from chinu.logging_system.logger import get_logger

logger = get_logger("container")

T = TypeVar("T")


class Container(IContainer):
    """In-version Dependency Injection Container."""

    def __init__(self) -> None:
        """Initialize empty container dictionaries."""
        self._singletons: dict[Any, Any] = {}
        self._singleton_factories: dict[Any, Callable[[], Any]] = {}
        self._factories: dict[Any, Callable[..., Any]] = {}

    def _key_to_str(self, key: Any) -> str:
        """Convert a type or string key to string representation for logging/lookup."""
        if isinstance(key, type):
            return f"{key.__module__}.{key.__qualname__}"
        return str(key)

    def register_singleton(
        self, service_type: type[T] | str, instance_or_factory: T | Callable[[], T]
    ) -> None:
        """Register a singleton instance or factory.

        Args:
            service_type: Service interface/type or string identifier.
            instance_or_factory: Instance or factory returning the instance.
        """
        if callable(instance_or_factory) and not isinstance(instance_or_factory, type):
            self._singleton_factories[service_type] = instance_or_factory
            if service_type in self._singletons:
                del self._singletons[service_type]
        else:
            self._singletons[service_type] = instance_or_factory
            if service_type in self._singleton_factories:
                del self._singleton_factories[service_type]

        logger.debug("Registered singleton service", key=self._key_to_str(service_type))

    def register_factory(self, service_type: type[T] | str, factory: Callable[..., T]) -> None:
        """Register a factory function that creates a new instance on every resolution.

        Args:
            service_type: Service interface/type or string identifier.
            factory: Callable producing new instances.
        """
        self._factories[service_type] = factory
        logger.debug("Registered factory service", key=self._key_to_str(service_type))

    def resolve(self, service_type: type[T] | str) -> Any:
        """Resolve a service instance by type or key.

        Args:
            service_type: Service type or key.

        Returns:
            Resolved instance.

        Raises:
            ServiceNotFoundError: If key is not registered.
        """
        if service_type in self._singletons:
            return self._singletons[service_type]

        if service_type in self._singleton_factories:
            factory = self._singleton_factories[service_type]
            instance = factory()
            self._singletons[service_type] = instance
            del self._singleton_factories[service_type]
            return instance

        if service_type in self._factories:
            return self._factories[service_type]()

        key_name = self._key_to_str(service_type)
        raise ServiceNotFoundError(
            f"Service '{key_name}' is not registered in the container.",
            details={"service_key": key_name},
        )

    def has(self, service_type: type[T] | str) -> bool:
        """Check if a service is registered in the container.

        Args:
            service_type: Service type or string key.

        Returns:
            True if registered, False otherwise.
        """
        return (
            service_type in self._singletons
            or service_type in self._singleton_factories
            or service_type in self._factories
        )

    def clear(self) -> None:
        """Clear all registered services."""
        self._singletons.clear()
        self._singleton_factories.clear()
        self._factories.clear()
        logger.debug("Cleared DI Container registrations")

"""Interfaces for Dependency Injection Container and Service Registry."""

from collections.abc import Callable
from typing import Any, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class IContainer(Protocol):
    """Protocol for Dependency Injection container."""

    def register_singleton(
        self, service_type: type[T] | str, instance_or_factory: T | Callable[[], T]
    ) -> None:
        """Register a singleton service instance or factory.

        Args:
            service_type: Type/Interface or string identifier.
            instance_or_factory: Concrete instance or factory returning instance.
        """
        ...

    def register_factory(self, service_type: type[T] | str, factory: Callable[..., T]) -> None:
        """Register a factory producing new service instances.

        Args:
            service_type: Type/Interface or string identifier.
            factory: Function that constructs and returns the service.
        """
        ...

    def resolve(self, service_type: type[T] | str) -> Any:
        """Resolve a service instance by type or key.

        Args:
            service_type: Type/Interface or string identifier.

        Returns:
            The resolved service instance.
        """
        ...

    def has(self, service_type: type[T] | str) -> bool:
        """Check if a service is registered.

        Args:
            service_type: Type/Interface or string identifier.

        Returns:
            True if registered, False otherwise.
        """
        ...


@runtime_checkable
class IServiceRegistry(Protocol):
    """Protocol for dynamic service registry."""

    def register(self, name: str, service: Any, interface: type[Any] | None = None) -> None:
        """Register a service by name and optional interface.

        Args:
            name: Unique service identifier.
            service: Service instance.
            interface: Optional interface type.
        """
        ...

    def get(self, name: str) -> Any:
        """Get a registered service by name.

        Args:
            name: Unique service identifier.

        Returns:
            Registered service instance.
        """
        ...

    def has(self, name: str) -> bool:
        """Check if a service exists in the registry.

        Args:
            name: Unique service identifier.

        Returns:
            True if found, False otherwise.
        """
        ...

    def unregister(self, name: str) -> None:
        """Remove a service from registry.

        Args:
            name: Unique service identifier.
        """
        ...

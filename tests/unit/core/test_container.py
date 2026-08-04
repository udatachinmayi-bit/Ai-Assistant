"""Unit tests for Dependency Injection Container."""

import pytest

from chinu.core.container import Container
from chinu.core.interfaces.exceptions import ServiceNotFoundError


class SampleService:
    """Sample dummy service for testing DI container."""

    def __init__(self, value: str = "default") -> None:
        self.value = value


def test_register_and_resolve_singleton_instance() -> None:
    """Test registering singleton instance."""
    container = Container()
    instance = SampleService("custom")

    container.register_singleton(SampleService, instance)
    resolved = container.resolve(SampleService)

    assert resolved is instance
    assert resolved.value == "custom"


def test_register_and_resolve_singleton_factory() -> None:
    """Test registering singleton factory."""
    container = Container()
    calls = 0

    def factory() -> SampleService:
        nonlocal calls
        calls += 1
        return SampleService("from_factory")

    container.register_singleton("sample", factory)
    first = container.resolve("sample")
    second = container.resolve("sample")

    assert first is second
    assert calls == 1
    assert first.value == "from_factory"


def test_register_and_resolve_factory() -> None:
    """Test registering transient factory creating new instance on each resolve."""
    container = Container()

    container.register_factory(SampleService, lambda: SampleService("transient"))
    first = container.resolve(SampleService)
    second = container.resolve(SampleService)

    assert first is not second
    assert first.value == "transient"
    assert second.value == "transient"


def test_resolve_unregistered_raises_service_not_found() -> None:
    """Test resolving unregistered service key raises ServiceNotFoundError."""
    container = Container()
    with pytest.raises(ServiceNotFoundError):
        container.resolve("non_existent_key")

"""Unit tests for Service Registry."""

import pytest

from chinu.core.interfaces.exceptions import ServiceNotFoundError
from chinu.core.service_registry import ServiceRegistry


class DummyService:
    """Dummy service class."""


def test_register_get_has_unregister() -> None:
    """Test full CRUD operations on Service Registry."""
    registry = ServiceRegistry()
    service = DummyService()

    assert not registry.has("dummy")
    registry.register("dummy", service)
    assert registry.has("dummy")

    retrieved = registry.get("dummy")
    assert retrieved is service

    registry.unregister("dummy")
    assert not registry.has("dummy")


def test_get_missing_service_raises_error() -> None:
    """Test retrieving missing service raises ServiceNotFoundError."""
    registry = ServiceRegistry()
    with pytest.raises(ServiceNotFoundError):
        registry.get("missing")

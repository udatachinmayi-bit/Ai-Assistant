"""Unit tests for EventBus."""

import pytest

from chinu.core.event_bus import EventBus
from chinu.core.interfaces.events import Event
from chinu.core.interfaces.exceptions import EventBusError


def test_subscribe_and_publish_sync() -> None:
    """Test sync event subscription and publication."""
    bus = EventBus()
    received: list[Event] = []

    def handler(evt: Event) -> None:
        received.append(evt)

    bus.subscribe("wake_word.detected", handler)
    bus.publish("wake_word.detected", {"confidence": 0.95})

    assert len(received) == 1
    assert received[0].name == "wake_word.detected"
    assert received[0].payload["confidence"] == 0.95


def test_wildcard_subscription() -> None:
    """Test wildcard topic subscription matching."""
    bus = EventBus()
    received: list[Event] = []

    def handler(evt: Event) -> None:
        received.append(evt)

    bus.subscribe("wake_word.*", handler)
    bus.publish("wake_word.detected", {"word": "chinu"})
    bus.publish("wake_word.lost", {})
    bus.publish("stt.transcript", {})

    assert len(received) == 2


@pytest.mark.asyncio
async def test_publish_async() -> None:
    """Test async event publication."""
    bus = EventBus()
    received: list[Event] = []

    async def async_handler(evt: Event) -> None:
        received.append(evt)

    bus.subscribe("app.started", async_handler)
    await bus.publish_async("app.started", {"status": "ok"})

    assert len(received) == 1
    assert received[0].name == "app.started"


def test_unsubscribe() -> None:
    """Test unsubscribing handler from topic."""
    bus = EventBus()
    received: list[Event] = []

    def handler(evt: Event) -> None:
        received.append(evt)

    bus.subscribe("test.event", handler)
    bus.publish("test.event")
    assert len(received) == 1

    bus.unsubscribe("test.event", handler)
    bus.publish("test.event")
    assert len(received) == 1


def test_invalid_handler_raises_error() -> None:
    """Test subscribing non-callable raises EventBusError."""
    bus = EventBus()
    with pytest.raises(EventBusError):
        bus.subscribe("test.event", "not_callable")  # type: ignore[arg-type]

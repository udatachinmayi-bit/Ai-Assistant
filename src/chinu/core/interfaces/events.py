"""Event definitions and EventBus interface contract for Chinu AI."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class Event:
    """Represents an event published on the EventBus.

    Attributes:
        name: Dot-notated event name (e.g., 'wake_word.detected', 'app.started').
        payload: Event data dictionary.
        timestamp: UTC timestamp when the event was created.
        source: Optional name of the module or component emitting the event.
    """

    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    source: str | None = None


# Handler can be sync or async
EventHandler = Callable[[Event], None | Awaitable[None]]


@runtime_checkable
class IEventBus(Protocol):
    """Protocol defining the contract for the Event Bus component."""

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Subscribe a handler to an event topic.

        Args:
            event_name: Dot-notated event pattern (e.g. 'wake_word.detected' or '*').
            handler: Synchronous or asynchronous callback function.
        """
        ...

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """Unsubscribe a handler from an event topic.

        Args:
            event_name: Dot-notated event pattern.
            handler: Callback function to remove.
        """
        ...

    def publish(
        self, event: Event | str, payload: dict[str, Any] | None = None, source: str | None = None
    ) -> None:
        """Publish an event synchronously to subscribers.

        Args:
            event: Event object or event name string.
            payload: Optional payload if event name string is provided.
            source: Optional source module name if event name string is provided.
        """
        ...

    async def publish_async(
        self, event: Event | str, payload: dict[str, Any] | None = None, source: str | None = None
    ) -> None:
        """Publish an event asynchronously to subscribers.

        Args:
            event: Event object or event name string.
            payload: Optional payload if event name string is provided.
            source: Optional source module name if event name string is provided.
        """
        ...

    def clear(self) -> None:
        """Remove all subscriptions."""
        ...

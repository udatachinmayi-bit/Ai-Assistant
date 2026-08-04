"""Event Bus implementation for Chinu AI.

Provides publish/subscribe mechanism supporting both synchronous and asynchronous
event dispatching with exact and wildcard topic matching.
"""

import asyncio
import inspect
from typing import Any

from chinu.core.interfaces.events import Event, EventHandler, IEventBus
from chinu.core.interfaces.exceptions import EventBusError
from chinu.logging_system.logger import get_logger

logger = get_logger("event_bus")


def _match_pattern(pattern: str, topic: str) -> bool:
    """Check if an event topic matches a subscription pattern.

    Args:
        pattern: Pattern string (e.g. '*', 'wake_word.*', 'wake_word.detected').
        topic: Actual event topic name.

    Returns:
        True if matched, False otherwise.
    """
    if pattern == "*" or pattern == topic:
        return True
    if pattern.endswith(".*"):
        prefix = pattern[:-2]
        return topic.startswith(prefix + ".") or topic == prefix
    return False


class EventBus(IEventBus):
    """Central event bus for decoupled inter-module communication."""

    def __init__(self) -> None:
        """Initialize EventBus with empty subscriber map."""
        self._subscribers: dict[str, list[EventHandler]] = {}

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Subscribe a callback handler to an event topic pattern.

        Args:
            event_name: Event topic or pattern (e.g., 'wake_word.detected', '*').
            handler: Synchronous or asynchronous handler callable.
        """
        if not callable(handler):
            raise EventBusError(f"Handler '{handler}' is not callable.")

        if event_name not in self._subscribers:
            self._subscribers[event_name] = []

        if handler not in self._subscribers[event_name]:
            self._subscribers[event_name].append(handler)
            logger.debug(
                "Subscribed handler to event pattern",
                topic=event_name,
                handler=getattr(handler, "__name__", str(handler)),
            )

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """Unsubscribe a callback handler from an event topic pattern.

        Args:
            event_name: Event topic or pattern.
            handler: Handler callable to remove.
        """
        if event_name in self._subscribers:
            if handler in self._subscribers[event_name]:
                self._subscribers[event_name].remove(handler)
                logger.debug("Unsubscribed handler from event pattern", topic=event_name)
            if not self._subscribers[event_name]:
                del self._subscribers[event_name]

    def _get_matching_handlers(self, topic: str) -> list[EventHandler]:
        """Get list of handlers matching topic.

        Args:
            topic: Actual event topic name.

        Returns:
            List of matching handler callables.
        """
        matching: list[EventHandler] = []
        for pattern, handlers in list(self._subscribers.items()):
            if _match_pattern(pattern, topic):
                matching.extend(handlers)
        return matching

    def _prepare_event(
        self, event: Event | str, payload: dict[str, Any] | None = None, source: str | None = None
    ) -> Event:
        """Helper to coerce input into an Event object.

        Args:
            event: Event instance or event name string.
            payload: Optional payload dict if event is string.
            source: Optional source name if event is string.

        Returns:
            Event instance.
        """
        if isinstance(event, str):
            return Event(name=event, payload=payload or {}, source=source)
        return event

    def publish(
        self, event: Event | str, payload: dict[str, Any] | None = None, source: str | None = None
    ) -> None:
        """Publish an event synchronously to subscribers.

        Args:
            event: Event object or event name string.
            payload: Event payload if event name string is provided.
            source: Optional source identifier.
        """
        evt = self._prepare_event(event, payload, source)
        handlers = self._get_matching_handlers(evt.name)

        logger.debug("Publishing event synchronously", topic=evt.name, handler_count=len(handlers))

        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(handler(evt))
                    except RuntimeError:
                        asyncio.run(handler(evt))
                else:
                    res = handler(evt)
                    if inspect.isawaitable(res):
                        async def _run_awaitable(aw: Any) -> None:
                            await aw

                        try:
                            loop = asyncio.get_running_loop()
                            loop.create_task(_run_awaitable(res))
                        except RuntimeError:
                            asyncio.run(_run_awaitable(res))
            except Exception as exc:
                logger.error(
                    "Error executing event handler",
                    topic=evt.name,
                    handler=getattr(handler, "__name__", str(handler)),
                    error=str(exc),
                    exc_info=True,
                )

    async def publish_async(
        self, event: Event | str, payload: dict[str, Any] | None = None, source: str | None = None
    ) -> None:
        """Publish an event asynchronously to subscribers.

        Args:
            event: Event object or event name string.
            payload: Event payload if event name string is provided.
            source: Optional source identifier.
        """
        evt = self._prepare_event(event, payload, source)
        handlers = self._get_matching_handlers(evt.name)

        logger.debug("Publishing event asynchronously", topic=evt.name, handler_count=len(handlers))

        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    await handler(evt)
                else:
                    res = handler(evt)
                    if inspect.isawaitable(res):
                        await res
            except Exception as exc:
                logger.error(
                    "Error executing async event handler",
                    topic=evt.name,
                    handler=getattr(handler, "__name__", str(handler)),
                    error=str(exc),
                    exc_info=True,
                )

    def clear(self) -> None:
        """Remove all event subscriptions."""
        self._subscribers.clear()
        logger.debug("Cleared all event bus subscriptions")

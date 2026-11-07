"""A subscriber that keeps every event it receives, for a test to assert on."""

from patchbay.events import Event


class RecordingSubscriber:
    """Records each event delivered to it, in the order delivered.

    Subscribe it to everything (`bus.subscribe(None, recorder)`) or to one type; it is a
    `Subscriber[Event]`, so it takes any event.
    """

    def __init__(self) -> None:
        """Start with nothing recorded."""
        self._events: list[Event] = []

    def __call__(self, event: Event, /) -> None:
        """Record one event."""
        self._events.append(event)

    @property
    def events(self) -> tuple[Event, ...]:
        """Every event recorded so far, oldest first."""
        return tuple(self._events)

    def of_type[E: Event](self, event_type: type[E]) -> tuple[E, ...]:
        """Return the recorded events that are an `event_type`, oldest first."""
        return tuple(event for event in self._events if isinstance(event, event_type))

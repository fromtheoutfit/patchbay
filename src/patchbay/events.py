"""What happened, said after it happened: frozen events, and the in-process bus that delivers them.

An event is a frozen model. Its name is past tense and dotted (`parameter.changed`), its payload
is typed fields on its own class, never a dict, and its `at` is the UTC time it was built. A time
given for `at` is in UTC itself, a zone whose offset is zero at every instant, and is held as
`datetime.UTC`; a naive time, or a zone such as Europe/London that is at UTC only in winter, is
refused.

The bus is synchronous and in-process: `publish` calls every subscriber whose type the event is,
in the order they subscribed, and returns once all have run. The bus never alters an event; the
object published is the object each subscriber receives. `subscribe` returns the `Subscription`,
which `cancel()` ends, and refuses with `SubscriptionRejectedError` a type that is not an event or
a subscriber that cannot be called, so a bad subscription fails where it is made and not at every
publish after it. Subscribing or cancelling during a publish takes effect from the next event.

A subscriber that raises does not stop the others. Every one runs, and then the bus raises
`SubscriberFailedError` carrying each exception, so one bad listener cannot hide an event from
the rest. Only an `Exception` is caught; a `KeyboardInterrupt` or `SystemExit` stops delivery
where it is raised.

`Subscriber` lives here, beside the bus that takes it, and `patchbay.contracts` re-exports it.
"""

import re
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from types import TracebackType
from typing import Any, Literal, Protocol, Self, overload, runtime_checkable

from pydantic import Field, field_validator

from patchbay.errors import SubscriberFailedError, SubscriptionRejectedError
from patchbay.models import ParameterId, PatchbayModel, Quantity

_NAME = re.compile(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+")


def _now() -> datetime:
    return datetime.now(UTC)


class Event(PatchbayModel, frozen=True):
    """Something that happened, built at `at`, by `source`, as part of `correlation_id`'s work.

    `correlation_id` ties together the events of one call; `version` is the payload's shape, so
    a subscriber can tell a later shape from this one.
    """

    name: str
    version: int = Field(default=1, ge=1)
    at: datetime = Field(default_factory=_now)
    source: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)

    @field_validator("name", mode="after")
    @classmethod
    def _past_tense_and_dotted(cls, name: str) -> str:
        if not _NAME.fullmatch(name):
            msg = f"an event's name is dotted lowercase words, given {name!r}"
            raise ValueError(msg)
        return name

    @field_validator("at", mode="after")
    @classmethod
    def _in_utc(cls, at: datetime) -> datetime:
        # The zone is judged, not the instant: utcoffset(None) is a fixed zone's one offset, and
        # None for a zone whose offset moves (the PR 11 revision's verification/probes.txt,
        # footing.py C).
        zone = at.tzinfo
        if zone is None:
            msg = f"an event's time is in UTC, given a naive time {at.isoformat()}"
            raise ValueError(msg)
        if zone.utcoffset(None) != timedelta(0):
            msg = (
                f"an event's time is in UTC, offset zero all year, given {at.isoformat()} ({zone})"
            )
            raise ValueError(msg)
        return at.astimezone(UTC)


class ParameterChanged(Event, frozen=True):
    """A parameter was set: its id, the value it had and the value it has now."""

    name: Literal["parameter.changed"] = "parameter.changed"
    id: ParameterId = Field(min_length=1)
    old: Quantity
    new: Quantity


class PatchLoaded(Event, frozen=True):
    """An instrument loaded a patch holding `parameter_count` values."""

    name: Literal["patch.loaded"] = "patch.loaded"
    instrument: str = Field(min_length=1)
    parameter_count: int = Field(ge=0)


class RenderCompleted(Event, frozen=True):
    """An instrument rendered a pattern.

    `elapsed_seconds` is how long the render took on the wall clock, `audio_seconds` how long
    the audio is, and `warnings` what degraded it, if anything did.
    """

    name: Literal["render.completed"] = "render.completed"
    instrument: str = Field(min_length=1)
    elapsed_seconds: float = Field(ge=0)
    audio_seconds: float = Field(ge=0)
    warnings: tuple[str, ...] = ()


@runtime_checkable
class Subscriber[E: Event](Protocol):
    """Anything called with an event and returning nothing: a function will do.

    The event is positional-only, so a subscriber names its parameter as it likes. A subscriber
    for one type takes that type: `Subscriber[ParameterChanged]`.
    """

    def __call__(self, event: E, /) -> None:
        """Receive one event."""


class Subscription:
    """One subscriber's subscription to one type of event on one bus, until it is cancelled.

    The bus makes it, in `EventBus.subscribe`. `cancel()` ends it from the next event published:
    a publish already under way delivers to every subscription it began with. A second `cancel()`
    does nothing. As a context manager it cancels on leaving the block, however the block ends:
    `with bus.subscribe(ParameterChanged, handler): ...`. Each `subscribe` is a subscription of
    its own, so one subscriber subscribed twice is cancelled one subscription at a time.
    """

    def __init__(
        self,
        event_type: type[Event],
        subscriber: Subscriber[Any],
        on_cancel: Callable[["Subscription"], None],
    ) -> None:
        """Hold what is subscribed to and by whom, and what cancelling tells the bus."""
        self._event_type = event_type
        self._subscriber = subscriber
        self._on_cancel = on_cancel
        self._active = True

    @property
    def event_type(self) -> type[Event]:
        """The type an event is for this subscription to deliver it; Event for every event."""
        return self._event_type

    @property
    def subscriber(self) -> Subscriber[Any]:
        """The subscriber this subscription delivers to."""
        return self._subscriber

    @property
    def active(self) -> bool:
        """True until `cancel()` is called."""
        return self._active

    def cancel(self) -> None:
        """End the subscription from the next event; nothing, if it has ended already."""
        if self._active:
            self._active = False
            self._on_cancel(self)

    def __enter__(self) -> Self:
        """Return the subscription itself, for the block to hold."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Cancel, whether the block returned or raised; what it raised goes on."""
        self.cancel()


class EventBus:
    """Synchronous, in-process delivery of events to the subscribers that want them."""

    def __init__(self) -> None:
        """Start with no subscriptions."""
        self._subscriptions: list[Subscription] = []

    @overload
    def subscribe[E: Event](
        self, event_type: type[E], subscriber: Subscriber[E], /
    ) -> Subscription: ...

    @overload
    def subscribe(self, event_type: None, subscriber: Subscriber[Event], /) -> Subscription: ...

    def subscribe(self, event_type: object, subscriber: object, /) -> Subscription:
        """Deliver to `subscriber` every event that is an `event_type`, or every event for None.

        Returns the subscription, which `cancel()` ends. Subscribing during a publish takes
        effect from the next event. SubscriptionRejectedError, and nothing subscribed, when
        `event_type` is neither None nor a subclass of Event, or `subscriber` is not callable:
        the types say so already, and this says so to a caller the type checker never saw.
        """
        if event_type is None:
            wanted: type[Event] = Event
        elif isinstance(event_type, type) and issubclass(event_type, Event):
            wanted = event_type
        else:
            msg = f"{event_type!r} is not an Event type, nor None for every event"
            raise SubscriptionRejectedError(msg)
        if not isinstance(subscriber, Subscriber):
            msg = f"{subscriber!r} is not callable, so it cannot receive an event"
            raise SubscriptionRejectedError(msg)
        subscription = Subscription(wanted, subscriber, self._remove)
        self._subscriptions.append(subscription)
        return subscription

    def publish(self, event: Event, /) -> None:
        """Call every subscriber that wants `event`, in the order they subscribed, then return.

        Delivers to the subscriptions held when the publish began. Raises SubscriberFailedError
        after every subscriber has run when one or more raised, carrying their exceptions in
        order and chained from the first.
        """
        errors: list[Exception] = []
        for subscription in tuple(self._subscriptions):
            if isinstance(event, subscription.event_type):
                error = _deliver(subscription.subscriber, event)
                if error is not None:
                    errors.append(error)
        if errors:
            raise SubscriberFailedError(event.name, tuple(errors)) from errors[0]

    def _remove(self, subscription: Subscription) -> None:
        """Drop a cancelled subscription, so the bus holds its subscriber no longer."""
        self._subscriptions = [held for held in self._subscriptions if held is not subscription]


def _deliver(subscriber: Subscriber[Any], event: Event) -> Exception | None:
    """Call one subscriber; return what it raised, so the next one still runs."""
    try:
        subscriber(event)
    except Exception as error:  # noqa: BLE001  # the issue: one listener hides no event from another
        return error
    return None

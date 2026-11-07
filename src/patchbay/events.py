"""What happened, said after it happened: frozen events, and the in-process bus that delivers them.

An event is a frozen model. Its name is past tense and dotted (`parameter.changed`), its payload
is typed fields on its own class, never a dict, and its `at` is the UTC time it was built. The bus
is synchronous and in-process: `publish` calls every subscriber whose type the event is, in the
order they subscribed, and returns once all have run. The bus never alters an event; the object
published is the object each subscriber receives.

A subscriber that raises does not stop the others. Every one runs, and then the bus raises
`SubscriberFailedError` carrying each exception, so one bad listener cannot hide an event from
the rest. Only an `Exception` is caught; a `KeyboardInterrupt` or `SystemExit` stops delivery
where it is raised.

`Subscriber` lives here, beside the bus that takes it, and `patchbay.contracts` re-exports it.
"""

import re
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, Protocol, overload, runtime_checkable

from pydantic import Field, field_validator

from patchbay.errors import SubscriberFailedError
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
        if at.utcoffset() != timedelta(0):
            msg = f"an event's time is in UTC, given {at.isoformat()}"
            raise ValueError(msg)
        return at


class ParameterChanged(Event, frozen=True):
    """A parameter was set: its id, the value it had and the value it has now."""

    name: Literal["parameter.changed"] = "parameter.changed"
    id: ParameterId
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


class EventBus:
    """Synchronous, in-process delivery of events to the subscribers that want them."""

    def __init__(self) -> None:
        """Start with no subscribers."""
        self._subscriptions: list[tuple[type[Event], Subscriber[Any]]] = []

    @overload
    def subscribe[E: Event](self, event_type: type[E], subscriber: Subscriber[E], /) -> None: ...

    @overload
    def subscribe(self, event_type: None, subscriber: Subscriber[Event], /) -> None: ...

    def subscribe[E: Event](self, event_type: type[E] | None, subscriber: Subscriber[E], /) -> None:
        """Deliver to `subscriber` every event that is an `event_type`, or every event for None.

        Subscribing during a publish takes effect from the next event.
        """
        self._subscriptions.append((Event if event_type is None else event_type, subscriber))

    def publish(self, event: Event, /) -> None:
        """Call every subscriber that wants `event`, in the order they subscribed, then return.

        Raises SubscriberFailedError after every subscriber has run when one or more raised,
        carrying their exceptions in order and chained from the first.
        """
        errors: list[Exception] = []
        for event_type, subscriber in tuple(self._subscriptions):
            if isinstance(event, event_type):
                error = _deliver(subscriber, event)
                if error is not None:
                    errors.append(error)
        if errors:
            raise SubscriberFailedError(event.name, tuple(errors)) from errors[0]


def _deliver(subscriber: Subscriber[Any], event: Event) -> Exception | None:
    """Call one subscriber; return what it raised, so the next one still runs."""
    try:
        subscriber(event)
    except Exception as error:  # noqa: BLE001  # the issue: one listener hides no event from another
        return error
    return None

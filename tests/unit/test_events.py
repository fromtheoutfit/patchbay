"""Events are frozen, named and stamped in UTC; the bus delivers each to every subscriber."""

import gc
import json
import weakref
from collections.abc import Callable
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from typing import cast, override
from zoneinfo import ZoneInfo

import pytest

from patchbay.errors import (
    PatchbayValidationError,
    SubscriberFailedError,
    SubscriptionRejectedError,
)
from patchbay.events import (
    Event,
    EventBus,
    ParameterChanged,
    PatchLoaded,
    RenderCompleted,
    Subscriber,
    Subscription,
)
from patchbay.models import ParameterId, Quantity, Unit

_OLD = Quantity(value=0.25, unit=Unit.ratio)
_NEW = Quantity(value=0.75, unit=Unit.ratio)


def _changed(correlation_id: str = "c1") -> ParameterChanged:
    return ParameterChanged(
        source="fake", correlation_id=correlation_id, id=ParameterId("level"), old=_OLD, new=_NEW
    )


def _loaded() -> PatchLoaded:
    return PatchLoaded(source="fake", correlation_id="c2", instrument="fake", parameter_count=8)


# --- Event --------------------------------------------------------------------------------------


def test_each_event_names_itself_in_past_tense_dotted_form() -> None:
    """The three core events carry their fixed names and payload version 1."""
    rendered = RenderCompleted(
        source="fake",
        correlation_id="c3",
        instrument="fake",
        elapsed_seconds=0.01,
        audio_seconds=2.0,
    )
    names = [event.name for event in (_changed(), _loaded(), rendered)]
    assert names == ["parameter.changed", "patch.loaded", "render.completed"]
    assert {event.version for event in (_changed(), _loaded(), rendered)} == {1}
    assert rendered.warnings == ()


def test_an_event_s_name_is_fixed_by_its_class() -> None:
    """A ParameterChanged cannot be built under another name."""
    with pytest.raises(PatchbayValidationError, match="name"):
        ParameterChanged.model_validate({**dict(_changed()), "name": "patch.loaded"})


@pytest.mark.parametrize(
    "name", ["parameter", "Parameter.Changed", "parameter changed", ".changed", "parameter.", ""]
)
def test_an_event_s_name_is_dotted_lowercase_words(name: str) -> None:
    """One word, a capital, a space or an empty part is not an event's name."""
    with pytest.raises(PatchbayValidationError, match="dotted lowercase words"):
        Event(name=name, source="fake", correlation_id="c1")


def test_a_name_with_digits_and_underscores_is_an_event_s_name() -> None:
    """Words may hold digits and underscores after their first letter."""
    assert Event(name="osc_2.wave_table.loaded", source="fake", correlation_id="c1").name


def test_an_event_is_stamped_in_utc_when_built() -> None:
    """Left out, `at` is the UTC time the event was built."""
    before = datetime.now(UTC)
    event = _changed()
    after = datetime.now(UTC)
    assert before <= event.at <= after
    assert event.at.tzinfo is UTC


_LONDON = ZoneInfo("Europe/London")


class _Answers(tzinfo):
    """A zone whose offset is whatever the test hands it."""

    def __init__(self, offset: Callable[[datetime | None], timedelta | None]) -> None:
        self._offset = offset

    @override
    def utcoffset(self, dt: datetime | None) -> timedelta | None:
        return self._offset(dt)

    @override
    def dst(self, dt: datetime | None) -> None:
        return None

    @override
    def tzname(self, dt: datetime | None) -> str:
        return "answers"


def _zero_for_none_then(at_an_instant: timedelta | None) -> _Answers:
    return _Answers(lambda dt: timedelta(0) if dt is None else at_an_instant)


def _raises_at_an_instant(dt: datetime | None) -> timedelta:
    if dt is None:
        return timedelta(0)
    msg = "no offset at this instant"
    raise RuntimeError(msg)


@pytest.mark.parametrize(
    "at",
    [
        datetime.fromisoformat("2026-11-07T08:00:00"),
        datetime(2026, 11, 7, 8, 0, tzinfo=timezone(timedelta(hours=1))),
        datetime(2026, 1, 15, 12, 0, tzinfo=_LONDON),
        datetime(2026, 7, 15, 12, 0, tzinfo=_LONDON),
        datetime(2026, 7, 15, 12, 0, tzinfo=_zero_for_none_then(timedelta(hours=1))),
        datetime(2026, 7, 15, 12, 0, tzinfo=_zero_for_none_then(None)),
        # type() so mypy does not refuse an abstract class: a bare tzinfo is the case under test.
        datetime(2026, 7, 15, 12, 0, tzinfo=type("_Bare", (tzinfo,), {})()),
        datetime(2026, 7, 15, 12, 0, tzinfo=_Answers(_raises_at_an_instant)),
        datetime(2026, 7, 15, 12, 0, tzinfo=_Answers(lambda _: cast("timedelta", 0))),
    ],
    ids=[
        "naive",
        "an hour east of UTC",
        "London in January",
        "London in July",
        "zero for no instant, an hour east at this one",
        "zero for no instant, None at this one",
        "a bare tzinfo",
        "a zone raising at this instant",
        "a zone answering an int",
    ],
)
def test_an_event_s_time_is_refused_unless_utc(at: datetime) -> None:
    """A naive time, or a zone other than UTC, is refused rather than guessed at or converted.

    The zone's answer for no instant and its offset at this one must both be zero, and a zone that
    cannot say is refused as well. London answers None for no instant, so it is refused in January,
    at offset zero, as in July: a zone whose offset moves never passes, in any season.
    """
    with pytest.raises(PatchbayValidationError, match="in UTC"):
        Event(name="thing.happened", at=at, source="fake", correlation_id="c1")


def test_a_zone_claiming_zero_is_taken_at_its_word_for_the_time_given() -> None:
    """A tzinfo answering zero for no instant is judged only at the time given: no more can be."""
    zone = _Answers(lambda dt: timedelta(0) if dt is None or dt.month == 1 else timedelta(hours=1))
    january = Event(
        name="thing.happened",
        at=datetime(2026, 1, 15, 12, 0, tzinfo=zone),
        source="fake",
        correlation_id="c1",
    )
    assert january.at.tzinfo is UTC
    with pytest.raises(PatchbayValidationError, match="in UTC"):
        Event(
            name="thing.happened",
            at=datetime(2026, 7, 15, 12, 0, tzinfo=zone),
            source="fake",
            correlation_id="c1",
        )


@pytest.mark.parametrize(
    "zone",
    [UTC, timezone(timedelta(0), "Z"), ZoneInfo("UTC")],
    ids=["datetime.UTC", "a zero offset named Z", "ZoneInfo UTC"],
)
def test_a_time_in_utc_is_held_as_datetime_utc(zone: timezone | ZoneInfo) -> None:
    """A zone answering zero for no instant and at this time is UTC, and is held as UTC itself."""
    at = datetime(2026, 7, 15, 12, 0, tzinfo=zone)
    event = Event(name="thing.happened", at=at, source="fake", correlation_id="c1")
    assert event.at == at
    assert event.at.tzinfo is UTC


def test_an_event_round_trips_through_json() -> None:
    """An event comes back equal from its JSON, its time and its typed payload included."""
    event = _changed()
    restored = ParameterChanged.model_validate_json(event.model_dump_json())
    assert restored == event
    assert restored.at.tzinfo is UTC


def test_an_event_comes_back_from_its_json_data() -> None:
    """json.loads of an event's JSON holds its time as an ISO string; from_json_data reads it."""
    event = _changed()
    assert ParameterChanged.from_json_data(json.loads(event.model_dump_json())) == event


def test_a_changed_parameter_is_named() -> None:
    """An empty id is refused, as Parameter refuses one."""
    with pytest.raises(PatchbayValidationError, match="id"):
        ParameterChanged(source="fake", correlation_id="c1", id=ParameterId(""), old=_OLD, new=_NEW)


@pytest.mark.parametrize("field", ["source", "correlation_id"])
def test_an_event_says_where_it_came_from(field: str) -> None:
    """An empty source or correlation id is refused."""
    with pytest.raises(PatchbayValidationError, match=field):
        PatchLoaded.model_validate({**dict(_loaded()), field: ""})


def test_an_event_is_frozen() -> None:
    """An event's fields cannot be reassigned."""
    event = _changed()
    with pytest.raises(PatchbayValidationError, match="frozen"):
        event.correlation_id = "c9"  # type: ignore[misc]


# --- Subscriber ---------------------------------------------------------------------------------


def test_a_function_is_a_subscriber() -> None:
    """Any callable passes the runtime check; its parameter's type is mypy's to hold."""

    def on_changed(changed: ParameterChanged, /) -> None:
        del changed

    assert isinstance(on_changed, Subscriber)
    subscriber: Subscriber[ParameterChanged] = on_changed
    assert subscriber is on_changed


# --- EventBus -----------------------------------------------------------------------------------


def test_publish_delivers_to_every_subscriber_once_in_subscription_order() -> None:
    """Each subscriber is called once with the very object published, first subscribed first."""
    bus = EventBus()
    calls: list[tuple[str, Event]] = []
    bus.subscribe(None, lambda event: calls.append(("first", event)))
    bus.subscribe(None, lambda event: calls.append(("second", event)))
    event = _changed()
    bus.publish(event)
    assert [who for who, _ in calls] == ["first", "second"]
    assert all(received is event for _, received in calls)


def test_subscribe_by_type_receives_only_that_type() -> None:
    """A subscriber for ParameterChanged sees no PatchLoaded; one for every event sees both."""
    bus = EventBus()
    changes: list[ParameterChanged] = []
    everything: list[Event] = []
    bus.subscribe(ParameterChanged, changes.append)
    bus.subscribe(None, everything.append)
    changed, loaded = _changed(), _loaded()
    bus.publish(changed)
    bus.publish(loaded)
    assert changes == [changed]
    assert everything == [changed, loaded]


def test_subscribe_to_the_base_event_is_every_event() -> None:
    """Event is the type of every event, so subscribing to it is subscribing to all."""
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(Event, received.append)
    bus.publish(_loaded())
    assert [event.name for event in received] == ["patch.loaded"]


def test_publish_with_no_subscribers_does_nothing() -> None:
    """An event nobody wants is published without complaint."""
    EventBus().publish(_changed())


def test_a_subscriber_added_during_a_publish_starts_with_the_next_event() -> None:
    """Delivery runs over the subscribers as they were when publish was called."""
    bus = EventBus()
    late: list[Event] = []

    def subscribe_another(event: Event) -> None:
        del event
        bus.subscribe(None, late.append)

    bus.subscribe(None, subscribe_another)
    first, second = _changed("c1"), _changed("c2")
    bus.publish(first)
    assert late == []
    bus.publish(second)
    assert late == [second]


def _subscribe_unchecked(bus: EventBus, event_type: object, subscriber: object) -> None:
    """Subscribe as a caller mypy never saw would: the ignore holds mypy's refusal of the types."""
    bus.subscribe(event_type, subscriber)  # type: ignore[call-overload]


@pytest.mark.parametrize(
    ("event_type", "subscriber"),
    [
        ("parameter.changed", print),
        (int, print),
        (Quantity, print),
        (_changed(), print),
        (ParameterChanged, 3),
        (None, "parameter.changed"),
    ],
    ids=[
        "an event's name",
        "a type not an event",
        "a model not an event",
        "an event, not its type",
        "a number",
        "a str",
    ],
)
def test_a_bad_subscription_is_refused_where_it_is_made(
    event_type: object, subscriber: object
) -> None:
    """Refused at subscribe, and nothing subscribed: every publish after it still delivers."""
    bus = EventBus()
    received: list[Event] = []
    bus.subscribe(None, received.append)
    with pytest.raises(SubscriptionRejectedError):
        _subscribe_unchecked(bus, event_type, subscriber)
    event = _changed()
    bus.publish(event)
    assert received == [event]


def test_a_subscription_says_what_it_delivers_and_to_whom() -> None:
    """The type it delivers, Event for every event, and the subscriber it delivers to."""
    bus = EventBus()
    received: list[Event] = []
    every = bus.subscribe(None, received.append)
    changes = bus.subscribe(ParameterChanged, received.append)
    assert (every.event_type, changes.event_type) == (Event, ParameterChanged)
    assert every.subscriber == received.append
    assert every.active


def test_cancel_ends_delivery_and_a_second_cancel_does_nothing() -> None:
    """After cancel the subscriber receives nothing more; cancelling again is harmless."""
    bus = EventBus()
    received: list[Event] = []
    subscription = bus.subscribe(None, received.append)
    first = _changed("c1")
    bus.publish(first)
    subscription.cancel()
    subscription.cancel()
    bus.publish(_changed("c2"))
    assert received == [first]
    assert not subscription.active


def test_a_subscription_is_a_context_manager_that_cancels_on_exit() -> None:
    """Leaving the block cancels, whether it returned or raised, and what it raised goes on."""
    bus = EventBus()
    received: list[Event] = []
    with bus.subscribe(None, received.append) as subscription:
        inside = _changed("c1")
        bus.publish(inside)
    bus.publish(_changed("c2"))
    assert received == [inside]
    assert not subscription.active
    with pytest.raises(KeyError), bus.subscribe(None, received.append) as raising:
        raise KeyError
    assert not raising.active


def test_a_cancel_during_a_publish_takes_effect_from_the_next_event() -> None:
    """Delivery runs over the subscriptions held when publish began, as a subscribe does."""
    bus = EventBus()
    later: list[Event] = []
    subscriptions: list[Subscription] = []

    def cancel_the_later(event: Event) -> None:
        del event
        subscriptions[0].cancel()

    bus.subscribe(None, cancel_the_later)
    subscriptions.append(bus.subscribe(None, later.append))
    first, second = _changed("c1"), _changed("c2")
    bus.publish(first)
    bus.publish(second)
    assert later == [first]


def test_each_subscribe_is_its_own_subscription() -> None:
    """Subscribed twice, a subscriber receives twice, and once when one subscription ends."""
    bus = EventBus()
    received: list[Event] = []
    first = bus.subscribe(None, received.append)
    bus.subscribe(None, received.append)
    event = _changed()
    bus.publish(event)
    first.cancel()
    bus.publish(event)
    assert received == [event, event, event]


class _Holder:
    """A subscriber that holds something, to watch whether the bus keeps it alive."""

    def __call__(self, event: Event, /) -> None:
        del event


def test_a_cancelled_subscriber_is_no_longer_held_by_the_bus() -> None:
    """The bus drops a cancelled subscription, so what its subscriber holds can be collected."""
    bus = EventBus()
    holder = _Holder()
    held = weakref.ref(holder)
    subscription = bus.subscribe(None, holder)
    subscription.cancel()
    del holder, subscription
    gc.collect()
    assert held() is None


def test_a_failing_subscriber_hides_the_event_from_no_other() -> None:
    """Every subscriber runs; then SubscriberFailedError carries each error, from the first."""
    bus = EventBus()
    received: list[Event] = []
    first_error, second_error = RuntimeError("first"), KeyError("second")

    def fail_first(_event: Event) -> None:
        raise first_error

    def fail_second(_event: Event) -> None:
        raise second_error

    bus.subscribe(None, fail_first)
    bus.subscribe(None, received.append)
    bus.subscribe(None, fail_second)
    event = _changed()
    with pytest.raises(SubscriberFailedError) as caught:
        bus.publish(event)
    assert received == [event]
    assert caught.value.event_name == "parameter.changed"
    assert caught.value.exceptions == (first_error, second_error)
    assert caught.value.__cause__ is first_error


class _Stop(BaseException):
    """Not an Exception: the kind of signal the bus must not swallow."""


def test_a_base_exception_stops_delivery_where_it_is_raised() -> None:
    """KeyboardInterrupt and its kind are not a subscriber's failure; they propagate at once."""
    bus = EventBus()
    received: list[Event] = []

    def stop(_event: Event) -> None:
        raise _Stop

    bus.subscribe(None, stop)
    bus.subscribe(None, received.append)
    with pytest.raises(_Stop):
        bus.publish(_changed())
    assert received == []

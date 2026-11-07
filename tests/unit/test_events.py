"""Events are frozen, named and stamped in UTC; the bus delivers each to every subscriber."""

from datetime import UTC, datetime, timedelta, timezone

import pytest

from patchbay.errors import PatchbayValidationError, SubscriberFailedError
from patchbay.events import (
    Event,
    EventBus,
    ParameterChanged,
    PatchLoaded,
    RenderCompleted,
    Subscriber,
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
    assert event.at.utcoffset() == timedelta(0)


@pytest.mark.parametrize(
    "at",
    [
        datetime.fromisoformat("2026-11-07T08:00:00"),
        datetime(2026, 11, 7, 8, 0, tzinfo=timezone(timedelta(hours=1))),
    ],
    ids=["naive", "an hour east of UTC"],
)
def test_an_event_s_time_is_refused_unless_utc(at: datetime) -> None:
    """A naive time, or one at another offset, is refused rather than guessed at or converted."""
    with pytest.raises(PatchbayValidationError, match="in UTC"):
        Event(name="thing.happened", at=at, source="fake", correlation_id="c1")


def test_an_event_round_trips_through_json() -> None:
    """An event comes back equal from its JSON, its time and its typed payload included."""
    event = _changed()
    assert ParameterChanged.model_validate_json(event.model_dump_json()) == event


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
    assert caught.value.errors == (first_error, second_error)
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

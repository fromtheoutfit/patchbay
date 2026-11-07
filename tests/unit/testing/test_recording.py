"""RecordingSubscriber keeps every event it receives, in order, and filters them by type."""

from patchbay.events import Event, EventBus, ParameterChanged, PatchLoaded, Subscriber
from patchbay.models import ParameterId, Quantity, Unit
from patchbay.testing import RecordingSubscriber

_VALUE = Quantity(value=0.5, unit=Unit.ratio)


def _changed() -> ParameterChanged:
    return ParameterChanged(
        source="fake", correlation_id="c1", id=ParameterId("level"), old=_VALUE, new=_VALUE
    )


def _loaded() -> PatchLoaded:
    return PatchLoaded(source="fake", correlation_id="c2", instrument="fake", parameter_count=0)


def test_a_recorder_is_a_subscriber_to_every_event() -> None:
    """It takes any event, so it subscribes to all of them or to one type."""
    recorder = RecordingSubscriber()
    subscriber: Subscriber[Event] = recorder
    assert isinstance(subscriber, Subscriber)


def test_a_recorder_keeps_what_the_bus_delivers_in_order() -> None:
    """Each call records its event; nothing else is recorded, and nothing is published."""
    bus = EventBus()
    recorder = RecordingSubscriber()
    bus.subscribe(None, recorder)
    changed, loaded = _changed(), _loaded()
    bus.publish(changed)
    bus.publish(loaded)
    assert recorder.events == (changed, loaded)
    assert recorder.events[0] is changed


def test_a_recorder_filters_by_type() -> None:
    """of_type gives the recorded events of one type, typed as that type."""
    recorder = RecordingSubscriber()
    changed, loaded = _changed(), _loaded()
    recorder(changed)
    recorder(loaded)
    changes: tuple[ParameterChanged, ...] = recorder.of_type(ParameterChanged)
    assert changes == (changed,)
    assert recorder.of_type(Event) == (changed, loaded)


def test_events_is_a_snapshot() -> None:
    """The tuple returned does not grow when the recorder does."""
    recorder = RecordingSubscriber()
    before = recorder.events
    recorder(_changed())
    assert before == ()
    assert len(recorder.events) == 1

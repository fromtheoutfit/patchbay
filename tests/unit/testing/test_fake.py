"""FakeInstrument: eight parameters, a boring sine voice, and one event for each call that acts."""

import numpy as np
import pytest

from patchbay.contracts import Instrument
from patchbay.errors import (
    ParameterNotFoundError,
    PatchbayError,
    PatchRejectedError,
    SubscriberFailedError,
    UnitMismatchError,
    ValueOutOfRangeError,
)
from patchbay.events import Event, EventBus, ParameterChanged, PatchLoaded, RenderCompleted
from patchbay.models import (
    Note,
    ParameterId,
    Patch,
    Pattern,
    Quantity,
    RenderRequest,
    Unit,
)
from patchbay.testing import FakeInstrument, RecordingSubscriber
from patchbay.testing.fake import PARAMETERS

_LEVEL = ParameterId("level")
_DECAY = ParameterId("decay")
_WAVEFORM = ParameterId("waveform")
_HALF = Quantity(value=0.5, unit=Unit.ratio)
_RATE = 8000
_A4 = 69  # MIDI pitch of A above middle C, 440 Hz


def _recorded(bus: EventBus) -> RecordingSubscriber:
    recorder = RecordingSubscriber()
    bus.subscribe(None, recorder)
    return recorder


def _pattern(*notes: Note, bars: int = 1, tempo_bpm: float = 120.0) -> Pattern:
    return Pattern(tempo_bpm=tempo_bpm, bars=bars, beats_per_bar=4, notes=notes)


def _note(start_beats: float = 0.0, duration_beats: float = 4.0, velocity: int = 127) -> Note:
    return Note(
        pitch=_A4,
        velocity=velocity,
        start_beats=start_beats,
        duration_beats=duration_beats,
        channel=0,
    )


# --- the parameters -----------------------------------------------------------------------------


def test_the_fake_is_an_instrument() -> None:
    """FakeInstrument meets the protocol: mypy holds its signatures, and isinstance agrees."""
    instrument: Instrument = FakeInstrument(EventBus())
    assert isinstance(instrument, Instrument)
    assert instrument.name == "fake"


def test_eight_parameters_cover_every_kind_and_seven_units(instrument: Instrument) -> None:
    """Every kind is there, and every unit but bpm, each parameter once."""
    parameters = instrument.parameters()
    assert parameters == PARAMETERS
    assert len({parameter.id for parameter in parameters}) == len(parameters) == len(PARAMETERS)
    assert {parameter.kind for parameter in parameters} == {"continuous", "choice", "boolean"}
    assert {parameter.unit for parameter in parameters} == set(Unit) - {Unit.bpm}


def test_every_parameter_starts_at_its_default(instrument: Instrument) -> None:
    """A new instrument holds each parameter's default."""
    for parameter in instrument.parameters():
        assert instrument.get(parameter.id) == parameter.default


# --- set ----------------------------------------------------------------------------------------


def test_set_stores_the_value_then_publishes_parameter_changed_once(
    instrument: Instrument, bus: EventBus
) -> None:
    """The value is held, and one ParameterChanged says what it was and what it is."""
    recorder = _recorded(bus)
    old = instrument.get(_LEVEL)
    instrument.set(_LEVEL, _HALF)
    assert instrument.get(_LEVEL) == _HALF
    (changed,) = recorder.events
    assert isinstance(changed, ParameterChanged)
    assert (changed.id, changed.old, changed.new) == (_LEVEL, old, _HALF)
    assert changed.source == "fake"
    assert changed.correlation_id


def test_set_to_the_value_held_still_publishes(instrument: Instrument, bus: EventBus) -> None:
    """A set is a set: setting the default publishes a change from the default to itself."""
    recorder = _recorded(bus)
    default = instrument.get(_LEVEL)
    instrument.set(_LEVEL, default)
    (changed,) = recorder.of_type(ParameterChanged)
    assert changed.old == changed.new == default


@pytest.mark.parametrize(
    ("parameter_id", "value", "error"),
    [
        (ParameterId("tremolo"), _HALF, ParameterNotFoundError),
        (_LEVEL, Quantity(value=0.5, unit=Unit.percent), UnitMismatchError),
        (ParameterId("cutoff"), Quantity(value=25000.0, unit=Unit.hz), ValueOutOfRangeError),
        (_WAVEFORM, Quantity(value=1.5, unit=Unit.none), ValueOutOfRangeError),
    ],
    ids=["unknown id", "wrong unit", "above the maximum", "between two choices"],
)
def test_a_refused_set_changes_nothing_and_publishes_nothing(
    instrument: Instrument,
    bus: EventBus,
    parameter_id: ParameterId,
    value: Quantity,
    error: type[PatchbayError],
) -> None:
    """The refusal is the error its cause names; the state and the bus are as they were."""
    recorder = _recorded(bus)
    before = instrument.patch()
    with pytest.raises(error):
        instrument.set(parameter_id, value)
    assert instrument.patch() == before
    assert recorder.events == ()


def test_get_of_an_unknown_id_names_the_id_and_the_instrument(instrument: Instrument) -> None:
    """ParameterNotFoundError, not KeyError."""
    with pytest.raises(ParameterNotFoundError) as caught:
        instrument.get(ParameterId("tremolo"))
    assert (caught.value.parameter_id, caught.value.instrument) == ("tremolo", "fake")


def test_each_call_publishes_under_its_own_correlation_id(
    instrument: Instrument, bus: EventBus
) -> None:
    """Two sets are two calls, so their events carry two ids."""
    recorder = _recorded(bus)
    instrument.set(_LEVEL, _HALF)
    instrument.set(_LEVEL, _HALF)
    first, second = recorder.events
    assert first.correlation_id != second.correlation_id


def test_a_subscriber_s_failure_reaches_the_caller_after_the_change(
    instrument: Instrument, bus: EventBus
) -> None:
    """The value is set and every subscriber runs; then set raises SubscriberFailedError."""

    def fail(_event: Event) -> None:
        raise RuntimeError

    recorder = RecordingSubscriber()
    bus.subscribe(None, fail)
    bus.subscribe(None, recorder)
    with pytest.raises(SubscriberFailedError):
        instrument.set(_LEVEL, _HALF)
    assert instrument.get(_LEVEL) == _HALF
    assert len(recorder.events) == 1


# --- load_patch and patch -----------------------------------------------------------------------


def test_load_patch_loads_values_and_opaque_then_publishes_patch_loaded_once(
    instrument: Instrument, bus: EventBus
) -> None:
    """Values the patch holds are set, the rest go to default, opaque sections are kept."""
    instrument.set(_DECAY, Quantity(value=2.0, unit=Unit.seconds))
    recorder = _recorded(bus)
    patch = Patch(instrument="fake", values={_LEVEL: _HALF}, opaque={"wavetable": b"\x00\xff"})
    instrument.load_patch(patch)
    assert instrument.get(_LEVEL) == _HALF
    decay = next(parameter for parameter in PARAMETERS if parameter.id == _DECAY)
    assert instrument.get(_DECAY) == decay.default
    assert dict(instrument.patch().opaque) == {"wavetable": b"\x00\xff"}
    (loaded,) = recorder.events
    assert isinstance(loaded, PatchLoaded)
    assert (loaded.instrument, loaded.parameter_count) == ("fake", 1)


def test_patch_holds_every_parameter_and_round_trips(instrument: Instrument) -> None:
    """patch() names every parameter; loading it back and asking again gives the same patch."""
    instrument.set(_LEVEL, _HALF)
    patch = instrument.patch()
    assert set(patch.values) == {parameter.id for parameter in PARAMETERS}
    instrument.set(_LEVEL, Quantity(value=0.1, unit=Unit.ratio))
    instrument.load_patch(patch)
    assert instrument.patch() == patch


@pytest.mark.parametrize(
    ("patch", "reason"),
    [
        (Patch(instrument="vital", values={}), "for instrument 'vital'"),
        (Patch(instrument="fake", values={ParameterId("tremolo"): _HALF}), "no parameter"),
        (
            Patch(instrument="fake", values={_LEVEL: Quantity(value=0.5, unit=Unit.db)}),
            "takes unit 'ratio'",
        ),
        (
            Patch(instrument="fake", values={_WAVEFORM: Quantity(value=4.0, unit=Unit.none)}),
            "not a value of parameter 'waveform'",
        ),
    ],
    ids=["another instrument", "unknown id", "wrong unit", "out of range"],
)
def test_a_rejected_patch_changes_nothing_and_publishes_nothing(
    instrument: Instrument, bus: EventBus, patch: Patch, reason: str
) -> None:
    """PatchRejectedError says why; the instrument and the bus are as they were."""
    instrument.set(_LEVEL, _HALF)
    recorder = _recorded(bus)
    before = instrument.patch()
    with pytest.raises(PatchRejectedError, match=reason):
        instrument.load_patch(patch)
    assert instrument.patch() == before
    assert recorder.events == ()


# --- render -------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("tempo_bpm", "bars", "tail_seconds", "sample_rate"),
    [(120.0, 1, 0.0, 8000), (120.0, 2, 0.5, 44100), (93.0, 3, 0.25, 48000), (500.0, 1, 0.0, 1)],
)
def test_render_gives_one_float32_channel_of_the_pattern_and_its_tail(
    instrument: Instrument, tempo_bpm: float, bars: int, tail_seconds: float, sample_rate: int
) -> None:
    """round((bars * beats_per_bar * 60 / tempo + tail) * sample_rate) samples, at that rate."""
    pattern = _pattern(bars=bars, tempo_bpm=tempo_bpm)
    request = RenderRequest(sample_rate=sample_rate, tail_seconds=tail_seconds)
    result = instrument.render(pattern, request)
    seconds = bars * pattern.beats_per_bar * 60.0 / tempo_bpm + tail_seconds
    assert result.audio.shape == (1, round(seconds * sample_rate))
    assert result.audio.dtype == np.float32
    assert result.sample_rate == sample_rate
    assert result.elapsed_seconds >= 0.0


def test_render_publishes_render_completed_once_with_the_result_s_times(
    instrument: Instrument, bus: EventBus
) -> None:
    """The event carries the result's elapsed and audio seconds, since a subscriber has no array."""
    recorder = _recorded(bus)
    result = instrument.render(_pattern(_note()), RenderRequest(sample_rate=_RATE, tail_seconds=0))
    (completed,) = recorder.events
    assert isinstance(completed, RenderCompleted)
    assert completed.elapsed_seconds == result.elapsed_seconds
    assert completed.audio_seconds == result.audio_seconds
    assert completed.warnings == result.warnings == ()


def test_a_note_sounds_at_its_pitch_and_decays_to_silence(instrument: Instrument) -> None:
    """MIDI 69 is 440 Hz; after the decay parameter's seconds the note is silent."""
    instrument.set(_DECAY, Quantity(value=0.5, unit=Unit.seconds))
    result = instrument.render(_pattern(_note()), RenderRequest(sample_rate=_RATE, tail_seconds=0))
    first_half_second = result.audio[0, : _RATE // 2]
    spectrum = np.abs(np.fft.rfft(first_half_second))
    hertz_per_bin = _RATE / first_half_second.size
    assert int(np.argmax(spectrum)) * hertz_per_bin == pytest.approx(440.0)
    assert np.max(np.abs(result.audio[0, _RATE // 2 :])) == 0.0


def test_velocity_and_level_scale_the_note(instrument: Instrument) -> None:
    """Half the velocity's share of full scale and half the level give a quarter of the peak."""
    request = RenderRequest(sample_rate=_RATE, tail_seconds=0)
    instrument.set(_LEVEL, Quantity(value=1.0, unit=Unit.ratio))
    loud = float(np.max(np.abs(instrument.render(_pattern(_note()), request).audio)))
    instrument.set(_LEVEL, _HALF)
    quiet_note = _note(velocity=round(127 / 2))
    quiet = float(np.max(np.abs(instrument.render(_pattern(quiet_note), request).audio)))
    assert quiet == pytest.approx(loud * 0.5 * round(127 / 2) / 127, rel=1e-3)


def test_an_empty_pattern_renders_silence(instrument: Instrument) -> None:
    """No notes, no sound, and no warning."""
    result = instrument.render(_pattern(), RenderRequest(sample_rate=_RATE, tail_seconds=1.0))
    assert not result.audio.any()
    assert result.warnings == ()


def test_notes_past_full_scale_are_clipped_and_the_result_says_so(
    instrument: Instrument, bus: EventBus
) -> None:
    """A degraded render is a result with a warning, and RenderCompleted carries it."""
    recorder = _recorded(bus)
    instrument.set(_LEVEL, Quantity(value=1.0, unit=Unit.ratio))
    chord = _pattern(*(_note() for _ in range(4)))
    result = instrument.render(chord, RenderRequest(sample_rate=_RATE, tail_seconds=0))
    assert float(np.max(np.abs(result.audio))) == 1.0
    (warning,) = result.warnings
    assert warning.startswith("clipped")
    assert recorder.of_type(RenderCompleted)[0].warnings == result.warnings

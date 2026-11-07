"""The models validate on the model, refuse as patchbay, stay frozen inside, and round-trip."""

import inspect
import json
import math
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from fractions import Fraction
from types import MappingProxyType

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import BaseModel, TypeAdapter, ValidationError

from patchbay.errors import PatchbayValidationError, UnitMismatchError, ValueOutOfRangeError
from patchbay.models import (
    Note,
    Parameter,
    ParameterId,
    Patch,
    PatchbayModel,
    Pattern,
    PresetKey,
    Quantity,
    RenderRequest,
    RenderResult,
    Unit,
)

_UNITS = ("none", "ratio", "percent", "hz", "semitones", "seconds", "db", "bpm")
_MIDI_TOP = 127  # the highest pitch and velocity
_CHANNEL_TOP = 15  # the highest MIDI channel
_CUTOFF: dict[str, object] = {
    "id": "cutoff",
    "label": "Cutoff",
    "kind": "continuous",
    "unit": Unit.hz,
    "minimum": 20.0,
    "maximum": 20000.0,
    "default": Quantity(value=1000.0, unit=Unit.hz),
}
_WAVEFORM: dict[str, object] = {
    "id": "waveform",
    "label": "Waveform",
    "kind": "choice",
    "unit": Unit.none,
    "minimum": 0.0,
    "maximum": 2.0,
    "default": Quantity(value=0.0, unit=Unit.none),
    "choices": ("sine", "saw", "square"),
}
_MONO: dict[str, object] = {
    "id": "mono",
    "label": "Mono",
    "kind": "boolean",
    "unit": Unit.none,
    "minimum": 0.0,
    "maximum": 1.0,
    "default": Quantity(value=0.0, unit=Unit.none),
}
_FINITE = st.floats(allow_nan=False, allow_infinity=False)
_NOTE: dict[str, object] = {
    "pitch": 60,
    "velocity": 100,
    "start_beats": 0.0,
    "duration_beats": 1.0,
    "channel": 0,
}
_A_NOTE = Note.model_validate(_NOTE)
_PATTERN: dict[str, object] = {"tempo_bpm": 120.0, "bars": 1, "beats_per_bar": 4, "notes": ()}


def _takes_parameter_id(parameter_id: ParameterId) -> ParameterId:
    return parameter_id


def test_a_preset_key_is_not_a_parameter_id() -> None:
    """A PresetKey is refused where a ParameterId is expected, though both are a str.

    The refusal is held by mypy, not pytest: the ignore below names it, and strict's
    warn_unused_ignores fails the gate the day the refusal stops and the ignore suppresses nothing.
    """
    key = PresetKey("osc_1_level")
    assert _takes_parameter_id(key) == "osc_1_level"  # type: ignore[arg-type]


def test_units_are_the_eight_the_contract_names() -> None:
    """Unit is a StrEnum of exactly the eight units, each its own value."""
    assert tuple(unit.value for unit in Unit) == _UNITS
    assert all(Unit(value) == value for value in _UNITS)


# --- PatchbayModel: every way in refuses as patchbay -------------------------------------------

_QUANTITY = Quantity(value=0.5, unit=Unit.ratio)
_ENTRY_POINTS: tuple[tuple[str, Callable[[], object]], ...] = (
    ("constructor", lambda: Quantity(value=1.5, unit=Unit.ratio)),
    ("model_validate", lambda: Quantity.model_validate({"value": 1.5, "unit": Unit.ratio})),
    (
        "model_validate_json",
        lambda: Quantity.model_validate_json('{"value": 1.5, "unit": "ratio"}'),
    ),
    ("model_validate_json, bad JSON", lambda: Quantity.model_validate_json("{")),
    ("model_validate_strings", lambda: Quantity.model_validate_strings({"value": "x"})),
    ("from_json_data", lambda: Quantity.from_json_data({"value": 1.5, "unit": "ratio"})),
    ("assignment", lambda: setattr(_QUANTITY, "value", 0.25)),
    ("deletion", lambda: delattr(_QUANTITY, "value")),
    (
        "a field not declared",
        lambda: Quantity.model_validate({"value": 0.5, "unit": Unit.ratio, "x": 1}),
    ),
    ("NaN", lambda: Quantity(value=math.nan, unit=Unit.hz)),
    ("infinity", lambda: Quantity(value=math.inf, unit=Unit.hz)),
)


@pytest.mark.parametrize(
    "refuse", [fn for _, fn in _ENTRY_POINTS], ids=[n for n, _ in _ENTRY_POINTS]
)
def test_every_entry_point_refuses_with_patchbay_validation_error(
    refuse: Callable[[], object],
) -> None:
    """Construction, the three validators, assignment and deletion refuse as the package does.

    pydantic's ValidationError is the cause, never what escapes.
    """
    with pytest.raises(PatchbayValidationError) as caught:
        refuse()
    assert type(caught.value) is PatchbayValidationError
    assert isinstance(caught.value.__cause__, ValidationError)
    assert caught.value.details


def test_a_frozen_model_is_unchanged_by_a_refused_assignment() -> None:
    """The refusal leaves the model as it was."""
    with pytest.raises(PatchbayValidationError, match="frozen"):
        _QUANTITY.value = 0.25  # type: ignore[misc]
    assert Quantity(value=0.5, unit=Unit.ratio) == _QUANTITY


_STRICT_REFUSALS: tuple[tuple[str, Callable[[], object]], ...] = (
    ("a str for a float", lambda: Quantity.model_validate({"value": "0.5", "unit": Unit.ratio})),
    ("a str for a Unit", lambda: Quantity.model_validate({"value": 0.5, "unit": "ratio"})),
    ("a bool for an int", lambda: Note.model_validate({**_NOTE, "pitch": True})),
    ("a float for an int", lambda: Note.model_validate({**_NOTE, "pitch": 60.0})),
    ("a list for a tuple", lambda: Pattern.model_validate({**_PATTERN, "notes": [_A_NOTE]})),
    (
        "a str for a float, nested",
        lambda: Parameter.model_validate(
            {**_CUTOFF, "default": {"value": "1000", "unit": Unit.hz}}
        ),
    ),
    (
        "a JSON str for a float",
        lambda: Quantity.model_validate_json('{"value": "0.5", "unit": "ratio"}'),
    ),
)


@pytest.mark.parametrize(
    "refuse", [fn for _, fn in _STRICT_REFUSALS], ids=[n for n, _ in _STRICT_REFUSALS]
)
def test_strict_refuses_a_conversion(refuse: Callable[[], object]) -> None:
    """The type is the contract: no value is converted from another type, at any depth."""
    with pytest.raises(PatchbayValidationError):
        refuse()


def test_strict_admits_an_int_for_a_float_and_json_forms() -> None:
    """An int is a float; JSON's own forms (an enum's value, an array, an object) are admitted."""
    assert Quantity(value=1, unit=Unit.hz).value == 1.0
    assert Quantity.model_validate_json('{"value": 1, "unit": "hz"}') == Quantity(
        value=1.0, unit=Unit.hz
    )
    pattern = Pattern.model_validate_json(
        '{"tempo_bpm": 120, "bars": 1, "beats_per_bar": 4, "notes": [{"pitch": 60,'
        ' "velocity": 100, "start_beats": 0, "duration_beats": 1, "channel": 0}]}'
    )
    assert pattern.notes == (_A_NOTE,)


@pytest.mark.parametrize(
    "name", ["model_validate", "model_validate_json", "model_validate_strings"]
)
def test_the_validating_classmethods_keep_pydantic_s_signatures(name: str) -> None:
    """Each is pydantic's own, wrapped rather than restated, so every keyword it takes passes.

    A keyword a later pydantic adds reaches pydantic too: nothing here lists them.
    """
    assert inspect.signature(getattr(Quantity, name)) == inspect.signature(getattr(BaseModel, name))


def test_a_keyword_reaches_pydantic_through_the_wrapper() -> None:
    """strict=False is pydantic's to read: through the wrapper, "0.5" is then a float."""
    lax = Quantity.model_validate({"value": "0.5", "unit": Unit.hz}, strict=False)
    assert lax == Quantity(value=0.5, unit=Unit.hz)


class _PlainHolder(BaseModel):
    quantity: Quantity


class _PatchbayHolder(PatchbayModel, frozen=True):
    quantity: Quantity


_A_BAD_QUANTITY: dict[str, object] = {"value": "x", "unit": Unit.hz}


@pytest.mark.parametrize(
    "refuse",
    [
        lambda: TypeAdapter(list[Quantity]).validate_python([_A_BAD_QUANTITY]),
        lambda: _PlainHolder.model_validate({"quantity": _A_BAD_QUANTITY}),
    ],
    ids=["a TypeAdapter", "a plain BaseModel holding a Quantity"],
)
def test_validation_run_for_something_else_raises_pydantic_s_error(
    refuse: Callable[[], object],
) -> None:
    """The promise is a patchbay model's own entry points; pydantic validating for another is not.

    pydantic validates a nested model inside the outer validator, so the outer's error is
    pydantic's, as pydantic documents. This test holds the boundary models.py states.
    """
    with pytest.raises(ValidationError):
        refuse()


def test_a_model_on_patchbay_model_refuses_as_patchbay_at_any_depth() -> None:
    """An adapter's own model, derived from PatchbayModel, has the promise for its fields too."""
    with pytest.raises(PatchbayValidationError, match=r"quantity\.value"):
        _PatchbayHolder.model_validate({"quantity": _A_BAD_QUANTITY})


# --- from_json_data: JSON's forms, from Python data -----------------------------------------------


def test_from_json_data_takes_json_s_own_forms() -> None:
    """An enum by its value, an array for a tuple, an int for a float, all as json.loads gives."""
    data = json.loads(
        '{"tempo_bpm": 120, "bars": 1, "beats_per_bar": 4, "notes": [{"pitch": 60,'
        ' "velocity": 100, "start_beats": 0, "duration_beats": 1, "channel": 0}]}'
    )
    assert Pattern.from_json_data(data).notes == (_A_NOTE,)
    assert Quantity.from_json_data({"value": 1, "unit": "hz"}) == Quantity(value=1.0, unit=Unit.hz)
    with pytest.raises(PatchbayValidationError):
        Pattern.model_validate(data)


@pytest.mark.parametrize(
    ("model", "data"),
    [
        (Quantity, {"value": "0.5", "unit": "hz"}),
        (Note, {**_NOTE, "pitch": True}),
        (Note, {**_NOTE, "pitch": 60.5}),
        (Quantity, {"value": math.nan, "unit": "hz"}),
        (Quantity, {"value": 0.5, "unit": "kelvin"}),
    ],
    ids=["a str for a float", "a bool for an int", "a fraction for an int", "NaN", "no such unit"],
)
def test_from_json_data_is_still_strict(model: type[PatchbayModel], data: object) -> None:
    """JSON's forms are admitted and nothing else: no value is converted from another type."""
    with pytest.raises(PatchbayValidationError) as caught:
        model.from_json_data(data)
    assert isinstance(caught.value.__cause__, ValidationError)


_CIRCULAR: list[object] = []
_CIRCULAR.append(_CIRCULAR)


@pytest.mark.parametrize(
    ("data", "cause"),
    [
        ({"value": 0.5, "unit": "hz", "extra": {1, 2}}, TypeError),
        ({"value": 0.5, "unit": "hz", "at": datetime.now(UTC)}, TypeError),
        (_CIRCULAR, ValueError),
    ],
    ids=["a set", "a datetime", "a circular reference"],
)
def test_from_json_data_refuses_data_json_cannot_hold(data: object, cause: type) -> None:
    """A value JSON has no form for is refused as patchbay, chained from json's own error."""
    with pytest.raises(PatchbayValidationError, match="data JSON can hold") as caught:
        Quantity.from_json_data(data)
    assert type(caught.value.__cause__) is cause
    assert [detail["type"] for detail in caught.value.details] == ["json_data"]


# --- Quantity -----------------------------------------------------------------------------------


@given(value=_FINITE, unit=st.sampled_from(Unit))
def test_a_quantity_is_valid_unless_a_ratio_outside_zero_to_one(value: float, unit: Unit) -> None:
    """Any finite value is valid in any unit, except a ratio, which is in [0, 1]."""
    if unit is Unit.ratio and not 0.0 <= value <= 1.0:
        with pytest.raises(PatchbayValidationError, match=r"a ratio is in \[0, 1\]"):
            Quantity(value=value, unit=unit)
    else:
        assert Quantity(value=value, unit=unit).value == value


def test_a_quantity_is_hashable_and_equal_by_value() -> None:
    """Frozen and holding a float and a Unit, a Quantity is a value: hashable, equal by value."""
    assert hash(Quantity(value=0.5, unit=Unit.ratio)) == hash(_QUANTITY)
    assert Quantity(value=0.5, unit=Unit.ratio) == _QUANTITY


# --- Parameter ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fields", [_CUTOFF, _WAVEFORM, _MONO], ids=["continuous", "choice", "boolean"]
)
def test_each_kind_of_parameter_is_valid(fields: dict[str, object]) -> None:
    """A continuous, a choice and a boolean parameter, each as the contract shapes it."""
    parameter = Parameter.model_validate(fields)
    assert parameter.kind == fields["kind"]
    assert parameter.default == fields["default"]


_PARAMETER_REFUSALS: tuple[tuple[str, dict[str, object], str], ...] = (
    ("empty id", {**_CUTOFF, "id": ""}, "at least 1 character"),
    ("empty label", {**_CUTOFF, "label": ""}, "at least 1 character"),
    ("unknown kind", {**_CUTOFF, "kind": "stepped"}, "continuous"),
    ("choice without choices", {**_WAVEFORM, "choices": None}, "names at least one choice"),
    ("choice with no choices", {**_WAVEFORM, "choices": ()}, "names at least one choice"),
    ("repeated choices", {**_WAVEFORM, "choices": ("sine", "sine", "saw")}, "distinct"),
    ("an empty choice", {**_WAVEFORM, "choices": ("sine", "", "saw")}, "non-empty"),
    ("choices on a continuous", {**_CUTOFF, "choices": ("a",)}, "only a choice parameter"),
    ("choices on a boolean", {**_MONO, "choices": ("off", "on")}, "only a choice parameter"),
    ("minimum above maximum", {**_CUTOFF, "minimum": 30000.0}, "is above maximum"),
    (
        "ratio bounds outside [0, 1]",
        {
            **_CUTOFF,
            "unit": Unit.ratio,
            "maximum": 2.0,
            "minimum": 0.0,
            "default": Quantity(value=0.5, unit=Unit.ratio),
        },
        r"lie in \[0, 1\]",
    ),
    ("choice bounds not its indices", {**_WAVEFORM, "maximum": 3.0}, "from 0 to 2"),
    (
        "choice in a unit",
        {**_WAVEFORM, "unit": Unit.hz, "default": Quantity(value=0.0, unit=Unit.hz)},
        "unit none",
    ),
    ("boolean bounds not 0 to 1", {**_MONO, "maximum": 2.0}, "from 0 to 1"),
    (
        "default out of range",
        {**_CUTOFF, "default": Quantity(value=5.0, unit=Unit.hz)},
        "not a value of parameter 'cutoff'",
    ),
    (
        "default in another unit",
        {**_CUTOFF, "default": Quantity(value=0.5, unit=Unit.ratio)},
        "takes unit 'hz'",
    ),
    (
        "choice default not a whole number",
        {**_WAVEFORM, "default": Quantity(value=0.5, unit=Unit.none)},
        "not a value of parameter 'waveform'",
    ),
)


@pytest.mark.parametrize(
    ("fields", "reason"),
    [(fields, reason) for _, fields, reason in _PARAMETER_REFUSALS],
    ids=[name for name, _, _ in _PARAMETER_REFUSALS],
)
def test_a_parameter_that_does_not_hold_together_is_refused(
    fields: dict[str, object], reason: str
) -> None:
    """Each validator refuses the parameter its rule rules out, and says why."""
    with pytest.raises(PatchbayValidationError, match=reason):
        Parameter.model_validate(fields)


def test_check_raises_unit_mismatch_for_another_unit() -> None:
    """The mismatch names the parameter, the unit it takes and the unit it was given."""
    cutoff = Parameter.model_validate(_CUTOFF)
    with pytest.raises(UnitMismatchError) as caught:
        cutoff.check(Quantity(value=0.5, unit=Unit.ratio))
    assert (caught.value.parameter_id, caught.value.expected, caught.value.given) == (
        "cutoff",
        Unit.hz,
        Unit.ratio,
    )


@pytest.mark.parametrize(
    ("fields", "given"),
    [(_CUTOFF, 19.0), (_CUTOFF, 20000.5), (_WAVEFORM, 3.0), (_WAVEFORM, 1.5), (_MONO, 0.5)],
    ids=["below", "above", "past the last choice", "between choices", "half a boolean"],
)
def test_check_raises_value_out_of_range(fields: dict[str, object], given: float) -> None:
    """Outside the bounds, or not a whole number for a choice or a boolean, is out of range."""
    parameter = Parameter.model_validate(fields)
    with pytest.raises(ValueOutOfRangeError) as caught:
        parameter.check(Quantity(value=given, unit=parameter.unit))
    assert (caught.value.minimum, caught.value.maximum, caught.value.given) == (
        parameter.minimum,
        parameter.maximum,
        given,
    )


@pytest.mark.parametrize(
    "fields", [_CUTOFF, _WAVEFORM, _MONO], ids=["continuous", "choice", "boolean"]
)
def test_check_accepts_both_bounds(fields: dict[str, object]) -> None:
    """The bounds are inclusive."""
    parameter = Parameter.model_validate(fields)
    parameter.check(Quantity(value=parameter.minimum, unit=parameter.unit))
    parameter.check(Quantity(value=parameter.maximum, unit=parameter.unit))


# --- Patch --------------------------------------------------------------------------------------

_QUANTITIES = st.one_of(
    st.builds(Quantity, value=st.floats(0.0, 1.0), unit=st.just(Unit.ratio)),
    st.builds(
        Quantity, value=_FINITE, unit=st.sampled_from([u for u in Unit if u is not Unit.ratio])
    ),
)


@given(
    instrument=st.text(min_size=1),
    values=st.dictionaries(st.text(min_size=1).map(ParameterId), _QUANTITIES),
    opaque=st.dictionaries(st.text(), st.binary()),
)
def test_a_patch_round_trips_through_json_byte_for_byte(
    instrument: str, values: dict[ParameterId, Quantity], opaque: dict[str, bytes]
) -> None:
    """Any patch comes back equal from its JSON, every opaque byte as it was."""
    patch = Patch(instrument=instrument, values=values, opaque=opaque)
    restored = Patch.model_validate_json(patch.model_dump_json())
    assert restored == patch
    assert dict(restored.opaque) == opaque


@given(
    instrument=st.text(min_size=1),
    values=st.dictionaries(st.text(min_size=1).map(ParameterId), _QUANTITIES),
    opaque=st.dictionaries(st.text(), st.binary()),
)
def test_a_patch_comes_back_from_its_json_data(
    instrument: str, values: dict[ParameterId, Quantity], opaque: dict[str, bytes]
) -> None:
    """json.loads of a patch's JSON is data in JSON's form, and from_json_data takes it back whole.

    Its units are strings and its opaque bytes base64, which model_validate's strict Python input
    refuses; from_json_data reads them as the JSON they are.
    """
    patch = Patch(instrument=instrument, values=values, opaque=opaque)
    data = json.loads(patch.model_dump_json())
    restored = Patch.from_json_data(data)
    assert restored == patch
    assert dict(restored.opaque) == opaque
    if values or opaque:
        with pytest.raises(PatchbayValidationError):
            Patch.model_validate(data)


@given(
    values=st.dictionaries(st.text(min_size=1).map(ParameterId), _QUANTITIES, min_size=2),
    opaque=st.dictionaries(st.text(), st.binary(), min_size=2),
)
def test_a_patch_has_one_json_whatever_order_it_was_built_in(
    values: dict[ParameterId, Quantity], opaque: dict[str, bytes]
) -> None:
    """Both mappings are sorted by key, so the same patch writes the same JSON."""
    forward = Patch(instrument="fake", values=values, opaque=opaque)
    backward = Patch(
        instrument="fake",
        values=dict(reversed(values.items())),
        opaque=dict(reversed(opaque.items())),
    )
    assert forward.model_dump_json() == backward.model_dump_json()
    assert list(forward.values) == sorted(values)


def test_a_patch_s_mappings_are_read_only() -> None:
    """A frozen patch is frozen inside: neither mapping takes an item, and the input is copied."""
    values = {ParameterId("cutoff"): Quantity(value=1000.0, unit=Unit.hz)}
    patch = Patch(instrument="fake", values=values)
    assert isinstance(patch.values, MappingProxyType)
    assert isinstance(patch.opaque, MappingProxyType)
    assert dict(patch.opaque) == {}
    with pytest.raises(TypeError):
        patch.values[ParameterId("level")] = _QUANTITY  # type: ignore[index]
    values[ParameterId("level")] = _QUANTITY
    assert list(patch.values) == ["cutoff"]


def test_a_patch_is_not_hashable() -> None:
    """A mapping has no hash, so neither does a patch; Python says so, not pydantic."""
    with pytest.raises(TypeError, match="unhashable type: 'Patch'"):
        hash(Patch(instrument="fake", values={}))


def test_a_patch_names_its_instrument() -> None:
    """An empty instrument name is refused."""
    with pytest.raises(PatchbayValidationError, match="at least 1 character"):
        Patch(instrument="", values={})


def test_a_patch_s_parameter_ids_are_not_empty() -> None:
    """A value's key is a parameter id, and a parameter id has a character, as Parameter.id does."""
    with pytest.raises(PatchbayValidationError, match=r"values\.\.\[key\]: String should have"):
        Patch(instrument="fake", values={ParameterId(""): _QUANTITY})


# --- Note and Pattern ---------------------------------------------------------------------------


@given(pitch=st.integers(), velocity=st.integers(), channel=st.integers())
def test_a_note_s_integers_are_midi(pitch: int, velocity: int, channel: int) -> None:
    """Pitch is 0-127, velocity 1-127 (0 is a note-off), channel 0-15; nothing else is a note."""
    fields = {**_NOTE, "pitch": pitch, "velocity": velocity, "channel": channel}
    if 0 <= pitch <= _MIDI_TOP and 1 <= velocity <= _MIDI_TOP and 0 <= channel <= _CHANNEL_TOP:
        assert Note.model_validate(fields).pitch == pitch
    else:
        with pytest.raises(PatchbayValidationError):
            Note.model_validate(fields)


@given(start=_FINITE, duration=_FINITE)
def test_a_note_starts_at_or_after_zero_and_lasts(start: float, duration: float) -> None:
    """start_beats is never negative and duration_beats is always positive."""
    fields = {**_NOTE, "start_beats": start, "duration_beats": duration}
    if start >= 0 and duration > 0:
        assert Note.model_validate(fields).start_beats == start
    else:
        with pytest.raises(PatchbayValidationError):
            Note.model_validate(fields)


@given(
    bars=st.integers(1, 8),
    beats_per_bar=st.integers(1, 7),
    start=st.floats(0, 64),
    duration=st.floats(0.001, 64),
)
def test_a_pattern_refuses_a_note_that_ends_after_it(
    bars: int, beats_per_bar: int, start: float, duration: float
) -> None:
    """A note may end on the pattern's last beat, and not after it."""
    note = Note.model_validate({**_NOTE, "start_beats": start, "duration_beats": duration})
    fields = {**_PATTERN, "bars": bars, "beats_per_bar": beats_per_bar, "notes": (note,)}
    if start + duration <= bars * beats_per_bar:
        assert Pattern.model_validate(fields).notes == (note,)
    else:
        with pytest.raises(PatchbayValidationError, match="after the pattern's"):
            Pattern.model_validate(fields)


@pytest.mark.parametrize(
    ("field", "value"),
    [("tempo_bpm", 0.0), ("tempo_bpm", -1.0), ("bars", 0), ("beats_per_bar", 0)],
)
def test_a_pattern_s_tempo_and_length_are_positive(field: str, value: float) -> None:
    """Tempo, bars and beats per bar are each above zero."""
    with pytest.raises(PatchbayValidationError, match=field):
        Pattern.model_validate({**_PATTERN, field: value})


# --- RenderRequest and RenderResult -------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value"), [("sample_rate", 0), ("sample_rate", -44100), ("tail_seconds", -0.5)]
)
def test_a_render_request_is_a_positive_rate_and_a_tail(field: str, value: float) -> None:
    """The sample rate is above zero and the tail never negative; a zero tail is allowed."""
    fields: dict[str, object] = {"sample_rate": 48000, "tail_seconds": 0.0}
    assert RenderRequest.model_validate(fields).tail_seconds == 0.0
    with pytest.raises(PatchbayValidationError, match=field):
        RenderRequest.model_validate({**fields, field: value})


def _length(tempo_bpm: float, bars: int, beats_per_bar: int) -> Pattern:
    return Pattern(tempo_bpm=tempo_bpm, bars=bars, beats_per_bar=beats_per_bar, notes=())


def test_samples_is_the_pattern_and_its_tail_at_the_rate() -> None:
    """Four beats at 120 bpm are two seconds; with a quarter-second tail at 48 kHz, 108000."""
    request = RenderRequest(sample_rate=48000, tail_seconds=0.25)
    assert request.samples(_length(120.0, 1, 4)) == (2 + 0.25) * 48000


def test_samples_rounds_half_to_even() -> None:
    """Half a second at 1, 3 and 5 Hz is 0.5, 1.5 and 2.5 samples: 0, 2 and 2."""
    half_second = _length(120.0, 1, 1)
    rates = (1, 3, 5)
    samples = [RenderRequest(sample_rate=r, tail_seconds=0.0).samples(half_second) for r in rates]
    assert samples == [0, 2, 2]


@given(
    tempo=st.floats(20.0, 999.0),
    beats_per_bar=st.integers(1, 16),
    rate=st.integers(8000, 192000),
    beat=st.floats(0.0, 16.0),
)
def test_sample_at_places_a_beat_by_the_rule_that_fixes_the_length(
    tempo: float, beats_per_bar: int, rate: int, beat: float
) -> None:
    """Beat 0 is sample 0; the pattern's last beat, with no tail, is its length; between, exact."""
    pattern = _length(tempo, 1, beats_per_bar)
    request = RenderRequest(sample_rate=rate, tail_seconds=0.0)
    assert request.sample_at(pattern, 0.0) == 0
    assert request.sample_at(pattern, float(beats_per_bar)) == request.samples(pattern)
    assert request.sample_at(pattern, beat) == round(Fraction(beat) * 60 / Fraction(tempo) * rate)


def test_sample_at_is_an_int_at_any_tempo() -> None:
    """Exact like samples: a beat at the slowest tempo is a very large int, not an overflow."""
    pattern = _length(sys.float_info.min, 1, 4)
    assert type(RenderRequest(sample_rate=48000, tail_seconds=0.0).sample_at(pattern, 1.0)) is int


@given(
    tempo=st.floats(20.0, 999.0),
    bars=st.integers(1, 64),
    beats_per_bar=st.integers(1, 16),
    tail=st.floats(0.0, 60.0),
    rate=st.integers(8000, 192000),
)
def test_samples_agrees_with_the_float_formula_on_ordinary_requests(
    tempo: float, bars: int, beats_per_bar: int, tail: float, rate: int
) -> None:
    """Within a sample of the float formula, and exactly the rational one rounded."""
    samples = RenderRequest(sample_rate=rate, tail_seconds=tail).samples(
        _length(tempo, bars, beats_per_bar)
    )
    exact = (Fraction(bars * beats_per_bar * 60) / Fraction(tempo) + Fraction(tail)) * rate
    assert samples == round(exact)
    assert abs(samples - (bars * beats_per_bar * 60 / tempo + tail) * rate) <= 1


@pytest.mark.parametrize(
    ("pattern", "request_"),
    [
        (_length(1e-300, 1, 4), RenderRequest(sample_rate=48000, tail_seconds=0.0)),
        (_length(sys.float_info.min, 1, 1), RenderRequest(sample_rate=48000, tail_seconds=0.0)),
        (_length(120.0, 1, 4), RenderRequest(sample_rate=48000, tail_seconds=1e308)),
        (_length(120.0, 1, 4), RenderRequest(sample_rate=10**400, tail_seconds=0.0)),
        (_length(120.0, 10**400, 4), RenderRequest(sample_rate=48000, tail_seconds=0.0)),
    ],
    ids=["tempo 1e-300", "tempo float min", "tail 1e308", "rate 10**400", "bars 10**400"],
)
def test_samples_is_an_int_however_long_the_render(
    pattern: Pattern, request_: RenderRequest
) -> None:
    """Exact arithmetic: no overflow and no infinity, only a very large int."""
    samples = request_.samples(pattern)
    assert type(samples) is int
    assert samples > 10**300


def _result(audio: np.ndarray[tuple[int, ...], np.dtype[np.float32]]) -> RenderResult:
    return RenderResult(audio=audio, sample_rate=8, elapsed_seconds=0.25)


def test_a_render_result_holds_a_read_only_copy() -> None:
    """The array is copied and locked; the caller's own array stays writeable and separate."""
    audio = np.zeros((2, 8), dtype=np.float32)
    result = _result(audio)
    assert not result.audio.flags.writeable
    with pytest.raises(ValueError, match="read-only"):
        result.audio[0, 0] = 1.0
    audio[0, 0] = 1.0
    assert result.audio[0, 0] == 0.0
    assert result.warnings == ()
    assert result.audio_seconds == 1.0


@pytest.mark.parametrize(
    "audio",
    [
        np.zeros((1, 8), dtype=np.float64),
        np.zeros(8, dtype=np.float32),
        np.zeros((1, 2, 4), dtype=np.float32),
        np.zeros((0, 8), dtype=np.float32),
    ],
    ids=["float64", "one dimension", "three dimensions", "no channel"],
)
def test_a_render_result_refuses_audio_of_another_shape(audio: object) -> None:
    """Audio is float32, (channels, samples), with one channel or more."""
    with pytest.raises(PatchbayValidationError, match="audio"):
        RenderResult.model_validate({"audio": audio, "sample_rate": 8, "elapsed_seconds": 0.0})


@pytest.mark.parametrize("sample", [math.nan, math.inf, -math.inf], ids=["NaN", "inf", "-inf"])
def test_a_render_result_refuses_audio_that_is_not_finite(sample: float) -> None:
    """Every sample is a number, so a result always equals itself."""
    audio = np.zeros((1, 8), dtype=np.float32)
    audio[0, 5] = sample
    with pytest.raises(PatchbayValidationError, match="audio is finite"):
        _result(audio)


def test_audio_seconds_holds_at_any_rate() -> None:
    """An int over an int: at a rate no float holds, the length is 0.0, not an OverflowError."""
    audio = np.zeros((1, 8), dtype=np.float32)
    result = RenderResult(audio=audio, sample_rate=10**400, elapsed_seconds=0.0)
    assert result.audio_seconds == 0.0


def test_render_results_compare_by_their_arrays() -> None:
    """Equal arrays and fields are equal results; a different sample is not."""
    audio = np.linspace(-1, 1, 8, dtype=np.float32).reshape(1, 8)
    assert _result(audio) == _result(audio.copy())
    changed = audio.copy()
    changed[0, 3] = 0.5
    assert _result(audio) != _result(changed)
    assert _result(audio) != "audio"


def test_a_render_result_is_not_hashable() -> None:
    """An array has no hash, so neither does a result."""
    with pytest.raises(TypeError, match="unhashable type: 'RenderResult'"):
        hash(_result(np.zeros((1, 8), dtype=np.float32)))


def test_a_render_result_s_elapsed_time_is_never_negative() -> None:
    """elapsed_seconds is wall-clock time, so it is zero or more."""
    with pytest.raises(PatchbayValidationError, match="elapsed_seconds"):
        RenderResult(audio=np.zeros((1, 8), dtype=np.float32), sample_rate=8, elapsed_seconds=-1.0)

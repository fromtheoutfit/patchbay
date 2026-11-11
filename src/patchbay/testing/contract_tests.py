"""The tests every adapter runs against its real instrument.

Each is a plain function, `<property>(instrument, bus) -> None`, taking an instrument that
publishes on `bus`, fresh for the test. Its name has no `test_` prefix, so pytest never collects
one an adapter imports by name: the adapter runs them through `CONTRACT_TESTS`, each once. A test
that finds the property broken raises `ContractViolationError`, an `AssertionError` naming the
test, what it expected and what it got; it never uses `assert`, which `python -O` strips, and
never imports pytest, which an installed package cannot count on. An exception the test does not
expect propagates as itself.

`CONTRACT_TESTS` lists all thirteen. An adapter's tests parametrize over it, with `instrument` and
`bus` fixtures in its `conftest.py` (`tests/unit/testing/conftest.py` here is the shape):

    @pytest.mark.parametrize("contract_test", CONTRACT_TESTS, ids=lambda test: test.__name__)
    def test_contract(contract_test: ContractTest, instrument: Instrument, bus: EventBus) -> None:
        contract_test(instrument, bus)

Each test works out what it expects from the instrument's parameters and the contract alone,
never from an implementation's code. Values are set at a parameter's bounds, which
`Instrument.get` promises every instrument holds exactly, whatever its resolution. A value one
float past a bound is set too and must be refused, so a check with any slack is caught.
"""

import math
import sys
from collections.abc import Callable
from functools import partial

from patchbay.contracts import Instrument
from patchbay.errors import (
    ParameterNotFoundError,
    PatchRejectedError,
    RenderFailedError,
    UnitMismatchError,
    ValueOutOfRangeError,
)
from patchbay.events import EventBus, ParameterChanged, PatchLoaded, RenderCompleted
from patchbay.models import (
    Note,
    Parameter,
    ParameterId,
    Patch,
    Pattern,
    Quantity,
    RenderRequest,
    Unit,
)
from patchbay.testing.recording import RecordingSubscriber

type ContractTest = Callable[[Instrument, EventBus], None]
"""A contract test: it takes the instrument and the bus it publishes on, and returns or raises."""

_PATTERN = Pattern(
    tempo_bpm=120.0,
    bars=1,
    beats_per_bar=4,
    notes=(Note(pitch=60, velocity=100, start_beats=0.0, duration_beats=1.0, channel=0),),
)
_REQUEST = RenderRequest(sample_rate=48000, tail_seconds=0.25)
# One beat at the slowest tempo a float holds: some 1e315 samples at 48 kHz, past any instrument.
_IMPOSSIBLE = Pattern(tempo_bpm=sys.float_info.min, bars=1, beats_per_bar=1, notes=())


class ContractViolationError(AssertionError):
    """An instrument broke a contract test: which test, what it expected, what it got."""

    def __init__(self, test: str, expected: str, actual: str) -> None:
        """Name the test, the expectation and what the instrument did instead."""
        super().__init__(test, expected, actual)
        self.test = test
        self.expected = expected
        self.actual = actual

    def __str__(self) -> str:
        """Say which test, and what it expected and got."""
        return f"{self.test}: expected {self.expected}, got {self.actual}"


def _require(test: str, expected: str, actual: object, *, holds: bool) -> None:
    """Raise ContractViolationError, saying what was expected and got, unless the check holds."""
    if not holds:
        raise ContractViolationError(test, expected, repr(actual))


def _raises[E: Exception](test: str, expected: type[E], action: Callable[[], object]) -> E:
    """Return the `expected` exception `action` raises; ContractViolationError if it raises none."""
    try:
        action()
    except expected as error:
        return error
    raise ContractViolationError(test, f"{expected.__name__} to be raised", "no exception")


def _recorder(bus: EventBus) -> RecordingSubscriber:
    recorder = RecordingSubscriber()
    bus.subscribe(None, recorder)
    return recorder


def _other_value(parameter: Parameter, current: Quantity) -> Quantity:
    """Return a bound of the parameter other than its current value, or the only bound it has."""
    bound = parameter.maximum if current.value != parameter.maximum else parameter.minimum
    return Quantity(value=bound, unit=parameter.unit)


def _out_of_range(parameter: Parameter) -> list[Quantity]:
    """Return values in the parameter's unit it does not take: past each bound, between steps.

    Past a bound is the next float beyond it, which a bound as large as 2**53 still has and
    `bound + 1.0` does not; a bound with no finite float beyond it, the largest float, has none.
    A ratio's candidates stay in [0, 1], all a ratio Quantity holds.
    """
    beyond = (
        math.nextafter(parameter.maximum, math.inf),
        math.nextafter(parameter.minimum, -math.inf),
    )
    candidates = [value for value in beyond if math.isfinite(value)]
    if parameter.unit is Unit.ratio:
        candidates = [value for value in candidates if 0.0 <= value <= 1.0]
    if parameter.kind != "continuous":
        candidates.append(parameter.minimum + 0.5)
    return [Quantity(value=value, unit=parameter.unit) for value in candidates]


def _unknown_id(instrument: Instrument) -> ParameterId:
    """Return an id none of the instrument's parameters has, sorting after every one of theirs."""
    known = [parameter.id for parameter in instrument.parameters()]
    return ParameterId(max(known, default="patchbay") + ".unknown")


def parameters_are_unique_and_typed(instrument: Instrument, bus: EventBus) -> None:
    """Check that the instrument exposes at least one Parameter, and no two share an id."""
    del bus
    test = "parameters_are_unique_and_typed"
    parameters = tuple(instrument.parameters())
    _require(test, "at least one parameter", parameters, holds=len(parameters) > 0)
    for parameter in parameters:
        _require(
            test, "every parameter a Parameter", parameter, holds=isinstance(parameter, Parameter)
        )
    ids = [parameter.id for parameter in parameters]
    _require(test, "every parameter id once", ids, holds=len(set(ids)) == len(ids))


def get_after_set_returns_what_was_set(instrument: Instrument, bus: EventBus) -> None:
    """Check that, for every parameter set at a bound, `get` returns the value `set` was given."""
    del bus
    test = "get_after_set_returns_what_was_set"
    for parameter in instrument.parameters():
        value = _other_value(parameter, instrument.get(parameter.id))
        instrument.set(parameter.id, value)
        got = instrument.get(parameter.id)
        _require(test, f"{parameter.id} at {value!r}", got, holds=got == value)


def set_with_the_wrong_unit_raises_unit_mismatch(instrument: Instrument, bus: EventBus) -> None:
    """Check that a value in another unit is refused, changing nothing and publishing nothing."""
    test = "set_with_the_wrong_unit_raises_unit_mismatch"
    recorder = _recorder(bus)
    before = instrument.patch()
    for parameter in instrument.parameters():
        wrong = next(unit for unit in Unit if unit is not parameter.unit)
        refused = Quantity(value=0.0, unit=wrong)
        error = _raises(test, UnitMismatchError, partial(instrument.set, parameter.id, refused))
        fields = (error.parameter_id, error.expected, error.given)
        wanted = (parameter.id, parameter.unit, wrong)
        _require(test, "the id, its unit and the unit given", fields, holds=fields == wanted)
    after = instrument.patch()
    _require(test, "the instrument unchanged", after, holds=after == before)
    _require(test, "no event", recorder.events, holds=not recorder.events)


def an_unknown_id_raises_parameter_not_found(instrument: Instrument, bus: EventBus) -> None:
    """Check that `get` and `set` refuse an id the instrument does not have, naming it."""
    test = "an_unknown_id_raises_parameter_not_found"
    recorder = _recorder(bus)
    unknown = _unknown_id(instrument)
    parameter = instrument.parameters()[0]
    calls: tuple[Callable[[], object], ...] = (
        partial(instrument.get, unknown),
        partial(instrument.set, unknown, parameter.default),
    )
    for call in calls:
        error = _raises(test, ParameterNotFoundError, call)
        fields = (error.parameter_id, error.instrument)
        wanted = (unknown, instrument.name)
        _require(test, "the id and the instrument's name", fields, holds=fields == wanted)
    _require(test, "no event", recorder.events, holds=not recorder.events)


def a_value_out_of_range_raises_value_out_of_range(instrument: Instrument, bus: EventBus) -> None:
    """Check that a value past a bound, or between a choice's or boolean's steps, is refused."""
    test = "a_value_out_of_range_raises_value_out_of_range"
    recorder = _recorder(bus)
    before = instrument.patch()
    for parameter in instrument.parameters():
        for value in _out_of_range(parameter):
            error = _raises(
                test, ValueOutOfRangeError, partial(instrument.set, parameter.id, value)
            )
            fields = (error.parameter_id, error.minimum, error.maximum, error.given)
            wanted = (parameter.id, parameter.minimum, parameter.maximum, value.value)
            _require(
                test, f"the id, its bounds and {value.value!r}", fields, holds=fields == wanted
            )
    after = instrument.patch()
    _require(test, "the instrument unchanged", after, holds=after == before)
    _require(test, "no event", recorder.events, holds=not recorder.events)


def patch_round_trips_through_load_patch(instrument: Instrument, bus: EventBus) -> None:
    """Check that a patch, through JSON and loaded back after a change, gives the same patch."""
    del bus
    test = "patch_round_trips_through_load_patch"
    patch = instrument.patch()
    _require(
        test,
        "the patch to name the instrument",
        patch.instrument,
        holds=patch.instrument == instrument.name,
    )
    parameter = instrument.parameters()[0]
    instrument.set(parameter.id, _other_value(parameter, instrument.get(parameter.id)))
    instrument.load_patch(Patch.model_validate_json(patch.model_dump_json()))
    after = instrument.patch()
    _require(test, "the patch loaded", after, holds=after == patch)


def a_rejected_patch_changes_nothing(instrument: Instrument, bus: EventBus) -> None:
    """Check that another instrument's patch is refused, changing nothing and publishing nothing."""
    test = "a_rejected_patch_changes_nothing"
    recorder = _recorder(bus)
    before = instrument.patch()
    other = Patch(instrument=f"{instrument.name}.other", values=before.values)
    _raises(test, PatchRejectedError, lambda: instrument.load_patch(other))
    after = instrument.patch()
    _require(test, "the instrument unchanged", after, holds=after == before)
    _require(test, "no event", recorder.events, holds=not recorder.events)


def a_patch_refused_part_way_changes_nothing(instrument: Instrument, bus: EventBus) -> None:
    """Check that a patch bad only at its last entry is refused whole: nothing loaded or published.

    A patch's values are sorted by id, so an instrument that loads them one at a time meets the
    bad entry last, after every good one. Each patch names the instrument and gives every
    parameter before the bad entry a value other than the one it holds. The bad entry is the
    last parameter in a wrong unit, or at each value it does not take, or an id after all of them.
    """
    test = "a_patch_refused_part_way_changes_nothing"
    recorder = _recorder(bus)
    before = instrument.patch()
    parameters = sorted(instrument.parameters(), key=lambda parameter: parameter.id)
    good = {p.id: _other_value(p, instrument.get(p.id)) for p in parameters}
    last = parameters[-1]
    wrong = next(unit for unit in Unit if unit is not last.unit)
    bad: list[tuple[ParameterId, Quantity]] = [
        (last.id, Quantity(value=0.0, unit=wrong)),
        *((last.id, value) for value in _out_of_range(last)),
        (_unknown_id(instrument), last.default),
    ]
    for parameter_id, value in bad:
        patch = Patch(instrument=instrument.name, values={**good, parameter_id: value})
        _raises(test, PatchRejectedError, partial(instrument.load_patch, patch))
        after = instrument.patch()
        expected = f"the instrument unchanged by a patch refused at {parameter_id} {value!r}"
        _require(test, expected, after, holds=after == before)
    _require(test, "no event", recorder.events, holds=not recorder.events)


def render_returns_the_declared_shape_and_sample_rate(
    instrument: Instrument, bus: EventBus
) -> None:
    """Check that a render is the pattern and its tail at the request's rate, in float32."""
    del bus
    test = "render_returns_the_declared_shape_and_sample_rate"
    result = instrument.render(_PATTERN, _REQUEST)
    samples = _REQUEST.samples(_PATTERN)
    _require(test, f"{samples} samples", result.audio.shape, holds=result.audio.shape[1] == samples)
    rate = _REQUEST.sample_rate
    _require(test, f"{rate} Hz", result.sample_rate, holds=result.sample_rate == rate)


def an_impossible_render_raises_render_failed(instrument: Instrument, bus: EventBus) -> None:
    """Check that a render no instrument could hold raises RenderFailedError, publishing nothing.

    The render is some 1e315 samples, past any instrument's limits, so it is the instrument's
    refusal that reports it, never a built-in exception or memory running out.
    """
    test = "an_impossible_render_raises_render_failed"
    recorder = _recorder(bus)
    _raises(test, RenderFailedError, partial(instrument.render, _IMPOSSIBLE, _REQUEST))
    _require(test, "no event", recorder.events, holds=not recorder.events)


def set_emits_parameter_changed_once(instrument: Instrument, bus: EventBus) -> None:
    """Check that one set publishes one ParameterChanged: which parameter, from what, to what."""
    test = "set_emits_parameter_changed_once"
    parameter = instrument.parameters()[0]
    old = instrument.get(parameter.id)
    new = _other_value(parameter, old)
    recorder = _recorder(bus)
    instrument.set(parameter.id, new)
    events = recorder.events
    once = len(events) == 1 and isinstance(events[0], ParameterChanged)
    _require(test, "one ParameterChanged and no other event", events, holds=once)
    changed = recorder.of_type(ParameterChanged)[0]
    fields = (changed.id, changed.old, changed.new)
    _require(
        test, "the id, the old value and the new", fields, holds=fields == (parameter.id, old, new)
    )


def load_patch_emits_patch_loaded_once(instrument: Instrument, bus: EventBus) -> None:
    """Check that one load publishes one PatchLoaded, naming the instrument and counting values."""
    test = "load_patch_emits_patch_loaded_once"
    patch = instrument.patch()
    recorder = _recorder(bus)
    instrument.load_patch(patch)
    events = recorder.events
    once = len(events) == 1 and isinstance(events[0], PatchLoaded)
    _require(test, "one PatchLoaded and no other event", events, holds=once)
    loaded = recorder.of_type(PatchLoaded)[0]
    fields = (loaded.instrument, loaded.parameter_count)
    wanted = (instrument.name, len(patch.values))
    _require(test, "the name and the count of values", fields, holds=fields == wanted)


def render_emits_render_completed_once(instrument: Instrument, bus: EventBus) -> None:
    """Check that one render publishes one RenderCompleted with the result's times and warnings."""
    test = "render_emits_render_completed_once"
    recorder = _recorder(bus)
    result = instrument.render(_PATTERN, _REQUEST)
    events = recorder.events
    once = len(events) == 1 and isinstance(events[0], RenderCompleted)
    _require(test, "one RenderCompleted and no other event", events, holds=once)
    completed = recorder.of_type(RenderCompleted)[0]
    fields = (
        completed.instrument,
        completed.elapsed_seconds,
        completed.audio_seconds,
        completed.warnings,
    )
    wanted = (instrument.name, result.elapsed_seconds, result.audio_seconds, result.warnings)
    _require(test, "the name, and the result's times and warnings", fields, holds=fields == wanted)


CONTRACT_TESTS: tuple[ContractTest, ...] = (
    parameters_are_unique_and_typed,
    get_after_set_returns_what_was_set,
    set_with_the_wrong_unit_raises_unit_mismatch,
    an_unknown_id_raises_parameter_not_found,
    a_value_out_of_range_raises_value_out_of_range,
    patch_round_trips_through_load_patch,
    a_rejected_patch_changes_nothing,
    a_patch_refused_part_way_changes_nothing,
    render_returns_the_declared_shape_and_sample_rate,
    an_impossible_render_raises_render_failed,
    set_emits_parameter_changed_once,
    load_patch_emits_patch_loaded_once,
    render_emits_render_completed_once,
)
"""Every contract test, in the order an adapter's report lists them."""

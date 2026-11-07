"""The contract tests pass against FakeInstrument, and each fails against a fake broken its way.

The suite proves the fake and the fake proves the suite. Every contract test runs here as an
adapter's would, parametrized over CONTRACT_TESTS with the conftest's fixtures. Each one also
runs against a FakeInstrument that breaks exactly the property it checks, and must raise
ContractViolationError naming itself: a test that cannot fail proves nothing. A fake with
parameters at the largest bounds a float has passes every one, so no test fails a correct
instrument at its edges.
"""

import sys

import numpy as np
import pytest

from patchbay.contracts import Instrument
from patchbay.errors import PatchbayError, PatchRejectedError
from patchbay.events import EventBus, ParameterChanged, RenderCompleted
from patchbay.models import (
    Parameter,
    ParameterId,
    Patch,
    Pattern,
    Quantity,
    RenderRequest,
    RenderResult,
    Unit,
)
from patchbay.testing import CONTRACT_TESTS, ContractTest, ContractViolationError, FakeInstrument
from patchbay.testing import contract_tests as contract
from patchbay.testing.fake import MAX_SAMPLES, PARAMETERS


@pytest.mark.parametrize("contract_test", CONTRACT_TESTS, ids=lambda test: test.__name__)
def test_contract(contract_test: ContractTest, instrument: Instrument, bus: EventBus) -> None:
    """Each contract test passes against FakeInstrument, run the way an adapter runs it."""
    contract_test(instrument, bus)


# --- one fake broken for each contract test -----------------------------------------------------


class _RepeatsAParameter(FakeInstrument):
    def parameters(self) -> tuple[Parameter, ...]:
        return (*PARAMETERS, PARAMETERS[0])


class _ForgetsWhatWasSet(FakeInstrument):
    def get(self, parameter_id: ParameterId, /) -> Quantity:
        return next(p.default for p in self.parameters() if p.id == parameter_id)


class _TakesAnyUnit(FakeInstrument):
    def set(self, parameter_id: ParameterId, value: Quantity, /) -> None:
        if value.unit is self.get(parameter_id).unit:
            super().set(parameter_id, value)


class _AnswersForAnyId(FakeInstrument):
    def get(self, parameter_id: ParameterId, /) -> Quantity:
        if parameter_id in {p.id for p in self.parameters()}:
            return super().get(parameter_id)
        return PARAMETERS[0].default


class _ClampsIntoRange(FakeInstrument):
    def set(self, parameter_id: ParameterId, value: Quantity, /) -> None:
        parameter = next(p for p in self.parameters() if p.id == parameter_id)
        clamped = min(max(round(value.value), parameter.minimum), parameter.maximum)
        super().set(parameter_id, Quantity(value=clamped, unit=value.unit))


class _IgnoresALoadedPatch(FakeInstrument):
    def load_patch(self, patch: Patch, /) -> None:
        del patch


class _LoadsAnyonesPatch(FakeInstrument):
    def load_patch(self, patch: Patch, /) -> None:
        super().load_patch(Patch(instrument=self.name, values=patch.values, opaque=patch.opaque))


class _LoadsUntilARefusal(FakeInstrument):
    """Checks the patch's instrument, then sets its values one at a time, stopping at a refusal."""

    def load_patch(self, patch: Patch, /) -> None:
        if patch.instrument != self.name:
            msg = "another instrument's patch"
            raise PatchRejectedError(msg)
        try:
            for parameter_id, value in patch.values.items():
                self.set(parameter_id, value)
        except PatchbayError as error:
            raise PatchRejectedError(str(error)) from error


class _RendersASampleShort(FakeInstrument):
    def render(self, pattern: Pattern, request: RenderRequest, /) -> RenderResult:
        result = super().render(pattern, request)
        return RenderResult(
            audio=np.ascontiguousarray(result.audio[:, :-1]),
            sample_rate=result.sample_rate,
            elapsed_seconds=result.elapsed_seconds,
        )


class _RendersAnyLength(FakeInstrument):
    """Renders one silent sample for a render too long to make, instead of refusing it."""

    def render(self, pattern: Pattern, request: RenderRequest, /) -> RenderResult:
        if request.samples(pattern) > MAX_SAMPLES:
            silence = np.zeros((1, 1), dtype=np.float32)
            return RenderResult(audio=silence, sample_rate=request.sample_rate, elapsed_seconds=0)
        return super().render(pattern, request)


class _PublishesASetTwice(FakeInstrument):
    def __init__(self, bus: EventBus) -> None:
        super().__init__(bus)
        self._own_bus = bus

    def set(self, parameter_id: ParameterId, value: Quantity, /) -> None:
        old = self.get(parameter_id)
        super().set(parameter_id, value)
        self._own_bus.publish(
            ParameterChanged(
                source="fake", correlation_id="again", id=parameter_id, old=old, new=value
            )
        )


class _PublishesChangesOnLoad(FakeInstrument):
    def __init__(self, bus: EventBus) -> None:
        super().__init__(bus)
        self._own_bus = bus

    def load_patch(self, patch: Patch, /) -> None:
        super().load_patch(patch)
        level = PARAMETERS[0].id
        self._own_bus.publish(
            ParameterChanged(
                source="fake",
                correlation_id="load",
                id=level,
                old=patch.values[level],
                new=patch.values[level],
            )
        )


class _PublishesTheWrongTime(FakeInstrument):
    def __init__(self, bus: EventBus) -> None:
        self._own_bus = EventBus()
        super().__init__(self._own_bus)
        self._real_bus = bus

    def render(self, pattern: Pattern, request: RenderRequest, /) -> RenderResult:
        result = super().render(pattern, request)
        self._real_bus.publish(
            RenderCompleted(
                source="fake",
                correlation_id="render",
                instrument=self.name,
                elapsed_seconds=result.elapsed_seconds + 1.0,
                audio_seconds=result.audio_seconds,
            )
        )
        return result


# Each contract test, the fake broken its way, and the expectation the test must say it missed.
_BROKEN: tuple[tuple[ContractTest, type[FakeInstrument], str], ...] = (
    (contract.parameters_are_unique_and_typed, _RepeatsAParameter, "every parameter id once"),
    (
        contract.get_after_set_returns_what_was_set,
        _ForgetsWhatWasSet,
        "level at Quantity(value=1.0",
    ),
    (
        contract.set_with_the_wrong_unit_raises_unit_mismatch,
        _TakesAnyUnit,
        "UnitMismatchError to be raised",
    ),
    (
        contract.an_unknown_id_raises_parameter_not_found,
        _AnswersForAnyId,
        "ParameterNotFoundError to be raised",
    ),
    (
        contract.a_value_out_of_range_raises_value_out_of_range,
        _ClampsIntoRange,
        "ValueOutOfRangeError to be raised",
    ),
    (contract.patch_round_trips_through_load_patch, _IgnoresALoadedPatch, "the patch loaded"),
    (
        contract.a_rejected_patch_changes_nothing,
        _LoadsAnyonesPatch,
        "PatchRejectedError to be raised",
    ),
    (
        contract.a_patch_refused_part_way_changes_nothing,
        _LoadsUntilARefusal,
        "the instrument unchanged by a patch refused at waveform",
    ),
    (
        contract.render_returns_the_declared_shape_and_sample_rate,
        _RendersASampleShort,
        "108000 samples",
    ),
    (
        contract.an_impossible_render_raises_render_failed,
        _RendersAnyLength,
        "RenderFailedError to be raised",
    ),
    (
        contract.set_emits_parameter_changed_once,
        _PublishesASetTwice,
        "one ParameterChanged and no other event",
    ),
    (
        contract.load_patch_emits_patch_loaded_once,
        _PublishesChangesOnLoad,
        "one PatchLoaded and no other event",
    ),
    (
        contract.render_emits_render_completed_once,
        _PublishesTheWrongTime,
        "the name, and the result's times and warnings",
    ),
)


def test_every_contract_test_has_a_broken_fake() -> None:
    """No contract test goes unproven: each appears once in _BROKEN, and nothing else does."""
    assert [test for test, _, _ in _BROKEN] == list(CONTRACT_TESTS)


@pytest.mark.parametrize(
    ("contract_test", "broken", "expected"), _BROKEN, ids=[test.__name__ for test, _, _ in _BROKEN]
)
def test_each_contract_test_catches_its_broken_fake(
    contract_test: ContractTest, broken: type[FakeInstrument], expected: str
) -> None:
    """Against a fake broken its way, the test raises ContractViolationError for that reason."""
    bus = EventBus()
    with pytest.raises(ContractViolationError) as caught:
        contract_test(broken(bus), bus)
    assert caught.value.test == contract_test.__name__
    assert caught.value.expected.startswith(expected)


# --- a correct instrument at the edges of a float ------------------------------------------------


class _WideRange(FakeInstrument):
    """The fake with two more parameters: one up to 2**53, one over every finite float."""

    def parameters(self) -> tuple[Parameter, ...]:
        largest = sys.float_info.max
        return (
            *PARAMETERS,
            Parameter(
                id=ParameterId("far"),
                label="Far",
                kind="continuous",
                unit=Unit.hz,
                minimum=0.0,
                maximum=2.0**53,
                default=Quantity(value=0.0, unit=Unit.hz),
            ),
            Parameter(
                id=ParameterId("widest"),
                label="Widest",
                kind="continuous",
                unit=Unit.db,
                minimum=-largest,
                maximum=largest,
                default=Quantity(value=0.0, unit=Unit.db),
            ),
        )


@pytest.mark.parametrize("contract_test", CONTRACT_TESTS, ids=lambda test: test.__name__)
def test_a_correct_instrument_with_the_widest_bounds_passes(contract_test: ContractTest) -> None:
    """At 2**53, bound + 1.0 is the bound, and past the largest float there is none to give.

    Both broke the out-of-range test for a correct instrument before it took the next float past
    each bound (the PR 11 review's finding 6); the widened fake reads its parameters through
    parameters(), so the extra two are set, patched and checked like the rest.
    """
    bus = EventBus()
    contract_test(_WideRange(bus), bus)


def test_the_contract_tests_are_never_collected_by_pytest() -> None:
    """No name starts with test_, so one an adapter imports by name runs once, from the tuple."""
    assert not [test.__name__ for test in CONTRACT_TESTS if test.__name__.startswith("test")]
    assert not [name for name in vars(contract) if name.startswith("test")]


def test_a_contract_violation_is_an_assertion_error_with_fields() -> None:
    """It is a failed assertion to pytest, with a message built from its three fields."""
    violation = ContractViolationError("test_x", "one event", "()")
    assert isinstance(violation, AssertionError)
    assert (violation.test, violation.expected, violation.actual) == ("test_x", "one event", "()")
    assert str(violation) == "test_x: expected one event, got ()"

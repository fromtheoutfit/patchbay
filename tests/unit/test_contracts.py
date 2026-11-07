"""The Instrument protocol is implementable, checked by name at runtime and by mypy statically."""

from collections.abc import Sequence

import numpy as np
import pytest

from patchbay import contracts, events
from patchbay.contracts import Instrument, Subscriber
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


class _Silent:
    """The least that satisfies Instrument: no parameters, silence, and a name as an attribute."""

    name = "silent"

    def parameters(self) -> Sequence[Parameter]:
        return ()

    def get(self, parameter_id: ParameterId, /) -> Quantity:
        del parameter_id
        return Quantity(value=0.0, unit=Unit.none)

    def set(self, parameter_id: ParameterId, value: Quantity, /) -> None:
        del parameter_id, value

    def load_patch(self, patch: Patch, /) -> None:
        del patch

    def patch(self) -> Patch:
        return Patch(instrument=self.name, values={})

    def render(self, pattern: Pattern, request: RenderRequest, /) -> RenderResult:
        del pattern
        audio = np.zeros((1, request.sample_rate), dtype=np.float32)
        return RenderResult(audio=audio, sample_rate=request.sample_rate, elapsed_seconds=0.0)


class _NoRender:
    """Every member but render."""

    name = "mute"

    def parameters(self) -> Sequence[Parameter]:
        return ()


def test_an_object_with_every_member_is_an_instrument() -> None:
    """Statically, mypy holds _Silent to every signature; at runtime, isinstance agrees."""
    instrument: Instrument = _Silent()
    assert isinstance(instrument, Instrument)


def test_an_object_missing_a_member_is_not_an_instrument() -> None:
    """An object without every member of the protocol fails the isinstance check."""
    assert not isinstance(_NoRender(), Instrument)


def test_issubclass_is_refused_for_a_protocol_with_a_data_member() -> None:
    """`name` is a data member, so issubclass is refused: by mypy statically, by Python at runtime.

    The ignore names mypy's refusal, and warn_unused_ignores fails the gate if it ever stops.
    """
    with pytest.raises(TypeError, match="non-method members"):
        issubclass(_Silent, Instrument)  # type: ignore[misc]


def test_subscriber_is_the_events_module_s_own() -> None:
    """The contracts module exports the Subscriber events defines, not a second protocol."""
    assert Subscriber is events.Subscriber
    assert set(contracts.__all__) == {"Instrument", "Subscriber"}

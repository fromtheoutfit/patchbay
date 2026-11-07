"""FakeInstrument: the reference implementation of Instrument, deliberately boring.

It exists so the contracts are shown implementable and every later test has an instrument to run
against. Eight parameters cover the three kinds and seven units. It renders one channel: a sine
per note at the note's pitch, scaled by velocity and the level parameter, falling linearly to
silence over the decay parameter's seconds, and cut at the note's end. The other parameters are
stored, reported and patched like any other, and change nothing in the sound.

Summed notes that pass full scale are clipped to it, and the result says so in its warnings: a
degraded render, not a failed one. A render longer than MAX_SAMPLES, or faster than
MAX_SAMPLE_RATE, is refused with RenderFailedError before anything is allocated. The notes are
mixed straight into the one float32 buffer the result copies. Every call that changes or renders
publishes its event on the bus the instrument was given, after the change is made, under a
correlation id of its own; a call it refuses publishes nothing.

A subclass may widen the parameters by overriding `parameters()`: the instrument reads them
through it.
"""

import time
import uuid
from types import MappingProxyType
from typing import TYPE_CHECKING

import numpy as np

from patchbay.errors import (
    ParameterNotFoundError,
    PatchbayError,
    PatchRejectedError,
    RenderFailedError,
)
from patchbay.events import EventBus, ParameterChanged, PatchLoaded, RenderCompleted
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

if TYPE_CHECKING:
    from collections.abc import Mapping

_A4_HZ = 440.0
_A4_PITCH = 69
_SEMITONES_PER_OCTAVE = 12
_VELOCITY_TOP = 127

MAX_SAMPLES = 2**24
"""The longest render the fake makes, in samples: about 5.8 minutes at 48 kHz, 64 MiB of float32."""

MAX_SAMPLE_RATE = 768_000
"""The fastest sample rate the fake renders at, the highest standard PCM rate.

Within it and MAX_SAMPLES, every float the voice computes is finite.
"""

_LEVEL = ParameterId("level")
_DECAY = ParameterId("decay")


def _continuous(
    parameter_id: ParameterId, label: str, unit: Unit, bounds: tuple[float, float], default: float
) -> Parameter:
    minimum, maximum = bounds
    return Parameter(
        id=parameter_id,
        label=label,
        kind="continuous",
        unit=unit,
        minimum=minimum,
        maximum=maximum,
        default=Quantity(value=default, unit=unit),
    )


PARAMETERS: tuple[Parameter, ...] = (
    _continuous(_LEVEL, "Level", Unit.ratio, (0.0, 1.0), 0.8),
    _continuous(ParameterId("cutoff"), "Cutoff", Unit.hz, (20.0, 20000.0), 20000.0),
    _continuous(ParameterId("resonance"), "Resonance", Unit.percent, (0.0, 100.0), 0.0),
    _continuous(_DECAY, "Decay", Unit.seconds, (0.01, 10.0), 0.5),
    _continuous(ParameterId("detune"), "Detune", Unit.semitones, (-12.0, 12.0), 0.0),
    _continuous(ParameterId("drive"), "Drive", Unit.db, (0.0, 24.0), 0.0),
    Parameter(
        id=ParameterId("waveform"),
        label="Waveform",
        kind="choice",
        unit=Unit.none,
        minimum=0.0,
        maximum=3.0,
        default=Quantity(value=0.0, unit=Unit.none),
        choices=("sine", "triangle", "saw", "square"),
    ),
    Parameter(
        id=ParameterId("mono"),
        label="Mono",
        kind="boolean",
        unit=Unit.none,
        minimum=0.0,
        maximum=1.0,
        default=Quantity(value=0.0, unit=Unit.none),
    ),
)
"""FakeInstrument's parameters, in the order `parameters()` gives them."""


class FakeInstrument:
    """An Instrument with eight parameters and a sine voice, publishing on the bus it is given."""

    def __init__(self, bus: EventBus) -> None:
        """Start at every parameter's default, with no opaque sections."""
        self._bus = bus
        parameters = self.parameters()
        self._parameters = {parameter.id: parameter for parameter in parameters}
        self._values = {parameter.id: parameter.default for parameter in parameters}
        self._opaque: Mapping[str, bytes] = MappingProxyType({})

    @property
    def name(self) -> str:
        """Always "fake"."""
        return "fake"

    def parameters(self) -> tuple[Parameter, ...]:
        """Return the eight parameters, in PARAMETERS' order."""
        return PARAMETERS

    def get(self, parameter_id: ParameterId, /) -> Quantity:
        """Return the parameter's value; ParameterNotFoundError when there is no such id."""
        return self._values[self._parameter(parameter_id).id]

    def set(self, parameter_id: ParameterId, value: Quantity, /) -> None:
        """Check the value against the parameter, store it, then publish ParameterChanged.

        The event is published even when the value is the one already held: a set is a set.
        """
        parameter = self._parameter(parameter_id)
        parameter.check(value)
        old = self._values[parameter.id]
        self._values[parameter.id] = value
        self._bus.publish(
            ParameterChanged(
                source=self.name, correlation_id=_correlation(), id=parameter.id, old=old, new=value
            )
        )

    def load_patch(self, patch: Patch, /) -> None:
        """Load every value and opaque section, then publish PatchLoaded.

        The whole patch is checked before anything changes. A parameter the patch leaves out goes
        to its default. PatchRejectedError for another instrument's patch, an id this instrument
        does not have, or a value its parameter refuses, raised from the error that refused it.
        """
        self._check_whole(patch)
        self._values = {
            parameter.id: patch.values.get(parameter.id, parameter.default)
            for parameter in self.parameters()
        }
        self._opaque = patch.opaque
        self._bus.publish(
            PatchLoaded(
                source=self.name,
                correlation_id=_correlation(),
                instrument=self.name,
                parameter_count=len(patch.values),
            )
        )

    def patch(self) -> Patch:
        """Return every parameter's value and the opaque sections last loaded."""
        return Patch(instrument=self.name, values=self._values, opaque=self._opaque)

    def render(self, pattern: Pattern, request: RenderRequest, /) -> RenderResult:
        """Render the pattern and its tail as one channel, then publish RenderCompleted.

        `request.samples(pattern)` samples, each note from `request.sample_at` its start to its
        end. RenderFailedError, with nothing allocated and nothing published, past MAX_SAMPLES or
        MAX_SAMPLE_RATE. The notes sum in the one float32 buffer the result copies, so a render
        holds two buffers its full length, besides each note's own while it is mixed.
        """
        started = time.perf_counter()
        rate = request.sample_rate
        if rate > MAX_SAMPLE_RATE:
            msg = f"the fake renders at up to {MAX_SAMPLE_RATE} Hz, and was asked for a faster rate"
            raise RenderFailedError(msg)
        total = request.samples(pattern)
        if total > MAX_SAMPLES:
            msg = f"the fake renders up to {MAX_SAMPLES} samples, and this render is longer"
            raise RenderFailedError(msg)
        mix = np.zeros((1, total), dtype=np.float32)
        level = self._values[_LEVEL].value
        decay = self._values[_DECAY].value
        for note in pattern.notes:
            start = request.sample_at(pattern, note.start_beats)
            end = min(request.sample_at(pattern, note.start_beats + note.duration_beats), total)
            elapsed = np.arange(end - start, dtype=np.float64) / rate
            frequency = _A4_HZ * 2.0 ** ((note.pitch - _A4_PITCH) / _SEMITONES_PER_OCTAVE)
            envelope = np.clip(1.0 - elapsed / decay, 0.0, None)
            gain = level * note.velocity / _VELOCITY_TOP
            mix[0, start:end] += gain * envelope * np.sin(2.0 * np.pi * frequency * elapsed)
        warnings: tuple[str, ...] = ()
        peak = float(max(np.max(mix, initial=0.0), -np.min(mix, initial=0.0)))
        if peak > 1.0:
            np.clip(mix, -1.0, 1.0, out=mix)
            warnings = (f"clipped: the notes summed to {peak:.3f} of full scale",)
        result = RenderResult(
            audio=mix,
            sample_rate=rate,
            elapsed_seconds=time.perf_counter() - started,
            warnings=warnings,
        )
        self._bus.publish(
            RenderCompleted(
                source=self.name,
                correlation_id=_correlation(),
                instrument=self.name,
                elapsed_seconds=result.elapsed_seconds,
                audio_seconds=result.audio_seconds,
                warnings=result.warnings,
            )
        )
        return result

    def _parameter(self, parameter_id: ParameterId) -> Parameter:
        try:
            return self._parameters[parameter_id]
        except KeyError:
            raise ParameterNotFoundError(parameter_id, self.name) from None

    def _check_whole(self, patch: Patch) -> None:
        """Raise PatchRejectedError unless the whole patch loads, from the error that refuses it.

        The cause is the ParameterNotFoundError for an id this instrument does not have, or what
        Parameter.check raises for a value; another instrument's patch has none.
        """
        if patch.instrument != self.name:
            msg = f"the patch is for instrument {patch.instrument!r}, not {self.name!r}"
            raise PatchRejectedError(msg)
        try:
            for parameter_id, value in patch.values.items():
                self._parameter(parameter_id).check(value)
        except PatchbayError as error:
            raise PatchRejectedError(str(error)) from error


def _correlation() -> str:
    """Return a fresh id for one call's events."""
    return uuid.uuid4().hex

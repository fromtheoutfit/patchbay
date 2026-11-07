"""The values that cross a package boundary: frozen pydantic models, each validated as it is built.

Every model derives from `PatchbayModel`, so every model is frozen, refuses a field it does not
declare, refuses NaN and infinity, and validates strictly: the type is the contract, so "0.5" is
not 0.5 and 1 is not True (an int is still a float, and a dict for a nested model is validated as
strictly). `frozen=True` is written on the class line of each model, where mypy reads it, so mypy
refuses an assignment and a subclass that leaves it out.

A model whose input is refused raises `PatchbayValidationError`, never pydantic's
`ValidationError`, from each of its own entry points: the constructor, `model_validate`,
`model_validate_json`, `model_validate_strings`, `from_json_data`, and an assignment or deletion.
Validation pydantic runs on behalf of something else is that thing's, and raises pydantic's
`ValidationError`: a `TypeAdapter` over a model, or a plain `BaseModel` with a patchbay model as a
field. A model that derives from `PatchbayModel` has the promise, which is why an adapter's own
models derive from it. `model_copy(update=...)` validates nothing, as pydantic documents, and is
not a way in.

Python input is Python's types, strictly. Data in JSON's form, as `json.loads`, a YAML or a TOML
parser gives it, goes through `from_json_data`, which validates it by pydantic's JSON rules: an
enum by its value, bytes as base64, a time as an ISO string, an array for a tuple.

Containers inside a frozen model are read-only too: a `Patch`'s mappings are `MappingProxyType`s
and a `RenderResult`'s array is marked unwriteable. Neither model is hashable.
"""

import functools
import json
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from enum import StrEnum
from fractions import Fraction
from types import MappingProxyType
from typing import TYPE_CHECKING, Annotated, ClassVar, Literal, NewType, Self

import numpy as np
from numpy.typing import NDArray
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializerFunctionWrapHandler,
    ValidationError,
    field_serializer,
    field_validator,
    model_validator,
)

from patchbay.errors import (
    PatchbayError,
    PatchbayValidationError,
    UnitMismatchError,
    ValueOutOfRangeError,
)

if TYPE_CHECKING:
    from pydantic_core import ErrorDetails

ParameterId = NewType("ParameterId", str)
"""The key an instrument's host knows a parameter by."""

PresetKey = NewType("PresetKey", str)
"""The key a preset file knows a value by; never a ParameterId, which the type checker holds."""


class Unit(StrEnum):
    """The unit of a Quantity; `none` is no unit at all, a choice's index or a boolean's 0 or 1."""

    none = "none"
    ratio = "ratio"
    percent = "percent"
    hz = "hz"
    semitones = "semitones"
    seconds = "seconds"
    db = "db"
    bpm = "bpm"


@contextmanager
def _refusals() -> Iterator[None]:
    """Raise pydantic's ValidationError, wherever it comes from, as PatchbayValidationError."""
    try:
        yield
    except ValidationError as error:
        raise PatchbayValidationError(tuple(error.errors(include_url=False))) from error


def _refusing[**P, R](validate: Callable[P, R]) -> Callable[P, R]:
    """Wrap one of pydantic's validating methods so a refusal is raised as PatchbayValidationError.

    The wrapper takes whatever the method takes and forwards it whole, so it never restates the
    method's signature.
    """

    @functools.wraps(validate)
    def refusing(*args: P.args, **kwargs: P.kwargs) -> R:
        with _refusals():
            return validate(*args, **kwargs)

    return refusing


class PatchbayModel(BaseModel, frozen=True):
    """The base of every patchbay model: frozen, closed, finite, strict, refusing as patchbay.

    A subclass writes `frozen=True` on its class line too; mypy refuses one that does not.
    """

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    def __init__(self, /, **data: object) -> None:
        """Validate the fields, raising PatchbayValidationError for any refusal."""
        with _refusals():
            super().__init__(**data)

    # pydantic calls a model's own __init__ to build a nested model, with the parsed input in
    # Python mode: a JSON "ratio" would meet strict's refusal of a str for Unit, and a nested
    # refusal would surface without its path. This __init__ validates exactly what BaseModel's
    # does, so it carries BaseModel's marker, and pydantic validates nested models itself (the
    # contracts spec's verification/probes.txt, models_init.py).
    __init__.__pydantic_base_init__ = True  # type: ignore[attr-defined]

    # pydantic's three validating classmethods, wrapped rather than restated. mypy does not read
    # this block, so it checks every call against pydantic's own signatures (Self-typed, each
    # keyword by name); at runtime each wrapper forwards what it is given, a keyword a later
    # pydantic adds among it, and raises a refusal as PatchbayValidationError (the PR 11
    # revision's verification/probes.txt, footing.py A and footing_typing.py). model_validate_json
    # refuses bad JSON the same way; model_validate_strings parses "0.5" as a float even under
    # strict, parsing strings being its purpose.
    if not TYPE_CHECKING:
        model_validate = classmethod(_refusing(BaseModel.model_validate.__func__))
        model_validate_json = classmethod(_refusing(BaseModel.model_validate_json.__func__))
        model_validate_strings = classmethod(_refusing(BaseModel.model_validate_strings.__func__))

    @classmethod
    def from_json_data(cls, data: object, /) -> Self:
        """Validate data in JSON's form, as `json.loads`, a YAML or a TOML parser gives it.

        The data meets pydantic's JSON rules, exactly as `model_validate_json` holds its text to
        them: an enum by its value, bytes as base64 where the model reads them so, a time as an
        ISO string, an array for a tuple. Strict still holds, so "0.5" is not 0.5 and 1 is not
        True. A value JSON cannot hold, a set or a datetime or a circular reference, is refused
        too; every refusal is PatchbayValidationError.
        """
        try:
            text = json.dumps(data)
        except (TypeError, ValueError) as error:
            detail: ErrorDetails = {
                "type": "json_data",
                "loc": (),
                "msg": f"Input should be data JSON can hold: {error}",
                "input": data,
            }
            raise PatchbayValidationError((detail,)) from error
        return cls.model_validate_json(text)

    def __setattr__(self, name: str, value: object) -> None:
        """Refuse the assignment, the model being frozen, as PatchbayValidationError."""
        with _refusals():
            super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        """Refuse the deletion, the model being frozen, as PatchbayValidationError."""
        with _refusals():
            super().__delattr__(name)


class Quantity(PatchbayModel, frozen=True):
    """A value in a unit. A normalized value is a ratio, and a ratio is in `[0, 1]`."""

    value: float
    unit: Unit

    @model_validator(mode="after")
    def _ratio_is_normalized(self) -> Self:
        if self.unit is Unit.ratio and not 0.0 <= self.value <= 1.0:
            msg = f"a ratio is in [0, 1], given {self.value!r}"
            raise ValueError(msg)
        return self


class Parameter(PatchbayModel, frozen=True):
    """One parameter an instrument exposes: what it is called, what it takes, where it starts.

    A continuous parameter takes any value in `[minimum, maximum]` in its unit. A choice takes the
    index of one of its `choices`, a boolean 0 or 1, each as a whole number in `Unit.none`.
    """

    id: ParameterId = Field(min_length=1)
    label: str = Field(min_length=1)
    kind: Literal["continuous", "choice", "boolean"]
    unit: Unit
    minimum: float
    maximum: float
    default: Quantity
    choices: tuple[str, ...] | None = None

    def check(self, value: Quantity) -> None:
        """Raise unless `value` is one this parameter takes.

        UnitMismatchError when its unit is not the parameter's; ValueOutOfRangeError when it is
        outside `[minimum, maximum]` or, for a choice or a boolean, not a whole number.
        """
        if value.unit is not self.unit:
            raise UnitMismatchError(self.id, self.unit, value.unit)
        whole = self.kind == "continuous" or value.value.is_integer()
        if not (self.minimum <= value.value <= self.maximum and whole):
            raise ValueOutOfRangeError(self.id, self.minimum, self.maximum, value.value)

    @model_validator(mode="after")
    def _choices_belong_to_a_choice(self) -> Self:
        if self.kind == "choice":
            if not self.choices:
                msg = "a choice parameter names at least one choice"
                raise ValueError(msg)
            if len(set(self.choices)) != len(self.choices) or not all(self.choices):
                msg = f"choices are non-empty and distinct, given {self.choices!r}"
                raise ValueError(msg)
        elif self.choices is not None:
            msg = f"only a choice parameter has choices; this one is {self.kind}"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _bounds_fit_the_kind(self) -> Self:
        if self.minimum > self.maximum:
            msg = f"minimum {self.minimum!r} is above maximum {self.maximum!r}"
            raise ValueError(msg)
        if self.unit is Unit.ratio and not 0.0 <= self.minimum <= self.maximum <= 1.0:
            msg = "a ratio parameter's bounds lie in [0, 1]"
            raise ValueError(msg)
        if self.kind != "continuous":
            top = len(self.choices or ()) - 1 if self.kind == "choice" else 1
            if (self.unit, self.minimum, self.maximum) != (Unit.none, 0.0, float(top)):
                msg = f"a {self.kind} parameter is in unit none from 0 to {top}"
                raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _default_is_a_value(self) -> Self:
        try:
            self.check(self.default)
        except PatchbayError as error:
            msg = f"default: {error}"
            raise ValueError(msg) from error
        return self


class Patch(PatchbayModel, frozen=True):
    """An instrument's state: a value for each parameter, and the sections it does not interpret.

    `opaque` holds what the package passes through unread, a wavetable say, byte for byte; JSON
    carries those bytes as base64. Both mappings are sorted by key and read-only, so a patch's
    JSON is the same for the same patch.
    """

    model_config = ConfigDict(ser_json_bytes="base64", val_json_bytes="base64")

    instrument: str = Field(min_length=1)
    values: Mapping[Annotated[ParameterId, Field(min_length=1)], Quantity]
    opaque: Mapping[str, bytes] = Field(default_factory=dict, validate_default=True)

    # Unhashable, said the way Python says it: pydantic's frozen hash would raise on a mapping.
    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    @field_validator("values", "opaque", mode="after")
    @classmethod
    def _sorted_and_read_only[V](cls, mapping: Mapping[str, V]) -> Mapping[str, V]:
        return MappingProxyType(dict(sorted(mapping.items())))

    @field_serializer("values", "opaque", mode="wrap")
    def _as_plain_dict[V](
        self, mapping: Mapping[str, V], handler: SerializerFunctionWrapHandler
    ) -> object:
        return handler(dict(mapping))


class Note(PatchbayModel, frozen=True):
    """One MIDI note, placed in beats from the start of its pattern."""

    pitch: int = Field(ge=0, le=127)
    velocity: int = Field(ge=1, le=127)
    start_beats: float = Field(ge=0)
    duration_beats: float = Field(gt=0)
    channel: int = Field(ge=0, le=15)


class Pattern(PatchbayModel, frozen=True):
    """Notes at a tempo, over a whole number of bars; no note ends after the last bar."""

    tempo_bpm: float = Field(gt=0)
    bars: int = Field(gt=0)
    beats_per_bar: int = Field(gt=0)
    notes: tuple[Note, ...]

    @model_validator(mode="after")
    def _notes_end_within(self) -> Self:
        length = self.bars * self.beats_per_bar
        for index, note in enumerate(self.notes):
            end = note.start_beats + note.duration_beats
            if end > length:
                msg = f"note {index} ends at beat {end!r}, after the pattern's {length}"
                raise ValueError(msg)
        return self


_SECONDS_PER_MINUTE = 60


def _seconds(pattern: Pattern, beats: Fraction) -> Fraction:
    """Return how long `beats` of the pattern last at its tempo, exactly."""
    return beats * _SECONDS_PER_MINUTE / Fraction(pattern.tempo_bpm)


class RenderRequest(PatchbayModel, frozen=True):
    """How to render a pattern: at what sample rate, and how long to let it ring after the end.

    `samples` and `sample_at` are the one rule for where a render's samples fall, each computed in
    exact rational arithmetic and rounded half to even, so each is an int for every valid pattern
    and request: never an overflow and never infinite, however long the render.
    """

    sample_rate: int = Field(gt=0)
    tail_seconds: float = Field(ge=0)

    def samples(self, pattern: Pattern, /) -> int:
        """Return how many samples rendering `pattern` as this request asks gives.

        `round((bars * beats_per_bar * 60 / tempo_bpm + tail_seconds) * sample_rate)`. Every
        instrument's render is this many samples long (`Instrument.render`); one that cannot
        render that many raises RenderFailedError.
        """
        beats = Fraction(pattern.bars * pattern.beats_per_bar)
        seconds = _seconds(pattern, beats) + Fraction(self.tail_seconds)
        return round(seconds * self.sample_rate)

    def sample_at(self, pattern: Pattern, beat: float, /) -> int:
        """Return the sample `beat` of `pattern` falls on, counting from the pattern's start.

        `round(beat * 60 / tempo_bpm * sample_rate)`: where an instrument starts and ends a note,
        by the rule that fixes the render's length.
        """
        return round(_seconds(pattern, Fraction(beat)) * self.sample_rate)


_CHANNELS_BY_SAMPLES = 2  # the dimensions of a rendered buffer: (channels, samples)


class RenderResult(PatchbayModel, frozen=True):
    """Rendered audio, `(channels, samples)` float32, and how long the render took.

    `elapsed_seconds` is wall-clock time, measured by the instrument around the render; the
    audio's own length is `audio_seconds`. A result with warnings is degraded but usable; an
    instrument with nothing usable raises RenderFailedError instead. The array is a read-only
    copy, and every sample in it is finite. Two results are equal when their arrays and every
    other field are; neither is hashable, and pydantic's JSON form of one is not offered (the
    array has none).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    audio: NDArray[np.float32]
    sample_rate: int = Field(gt=0)
    elapsed_seconds: float = Field(ge=0)
    warnings: tuple[str, ...] = ()

    # Unhashable, said the way Python says it: an array has no hash, and __eq__ is defined here.
    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    @property
    def audio_seconds(self) -> float:
        """The audio's length: its samples over its sample rate.

        An int over an int, which Python divides exactly rounded, so no rate overflows it.
        """
        return int(self.audio.shape[1]) / self.sample_rate

    @field_validator("audio", mode="after")
    @classmethod
    def _float32_channels_by_samples(cls, audio: NDArray[np.float32]) -> NDArray[np.float32]:
        if audio.dtype != np.float32:
            msg = f"audio is float32, given {audio.dtype}"
            raise ValueError(msg)
        if audio.ndim != _CHANNELS_BY_SAMPLES or audio.shape[0] < 1:
            msg = f"audio is (channels, samples) with one channel or more, given {audio.shape}"
            raise ValueError(msg)
        if not np.isfinite(audio).all():
            msg = "audio is finite: no sample is NaN or infinite"
            raise ValueError(msg)
        locked = audio.copy()
        locked.flags.writeable = False
        return locked

    def __eq__(self, other: object) -> bool:
        """Equal when the arrays are equal element for element and the other fields are equal."""
        if not isinstance(other, RenderResult):
            return NotImplemented
        return (
            self.sample_rate == other.sample_rate
            and self.elapsed_seconds == other.elapsed_seconds
            and self.warnings == other.warnings
            and bool(np.array_equal(self.audio, other.audio))
        )

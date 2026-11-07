"""The exceptions patchbay raises: one root, each error carrying the fields that say what failed.

`PatchbayError` is the root, so a caller catches every failure the package reports with one
`except`. No built-in exception leaves a public method: a lookup that fails is a
`ParameterNotFoundError`, not a `KeyError`, and pydantic's `ValidationError` (a `ValueError`) is
raised as `PatchbayValidationError`.

Each error takes its fields as arguments, keeps them as attributes and passes them to `Exception`,
so `args` and pickling carry them, and builds its message from them in `__str__`. The fields are
plain values: an id or a unit is a `str` (a `ParameterId` and a `Unit` each are one), so this
module imports nothing else from the package and every other module can import it.
"""

from pydantic_core import ErrorDetails


class PatchbayError(Exception):
    """The root of every exception patchbay raises."""


class ParameterNotFoundError(PatchbayError):
    """An instrument was asked for a parameter it does not have."""

    def __init__(self, parameter_id: str, instrument: str) -> None:
        """Name the id that was not found and the instrument that was asked."""
        super().__init__(parameter_id, instrument)
        self.parameter_id = parameter_id
        self.instrument = instrument

    def __str__(self) -> str:
        """Say which parameter, on which instrument."""
        return f"instrument {self.instrument!r} has no parameter {self.parameter_id!r}"


class UnitMismatchError(PatchbayError):
    """A value was given in a unit other than the parameter's own."""

    def __init__(self, parameter_id: str, expected: str, given: str) -> None:
        """Name the parameter, the unit it takes and the unit it was given."""
        super().__init__(parameter_id, expected, given)
        self.parameter_id = parameter_id
        self.expected = expected
        self.given = given

    def __str__(self) -> str:
        """Say which unit the parameter takes and which it was given."""
        return (
            f"parameter {self.parameter_id!r} takes unit {str(self.expected)!r}, "
            f"given {str(self.given)!r}"
        )


class ValueOutOfRangeError(PatchbayError):
    """A value is not one the parameter takes.

    Outside the parameter's `[minimum, maximum]`, or not a whole number for a choice or a boolean.
    """

    def __init__(self, parameter_id: str, minimum: float, maximum: float, given: float) -> None:
        """Name the parameter, its bounds and the value it was given."""
        super().__init__(parameter_id, minimum, maximum, given)
        self.parameter_id = parameter_id
        self.minimum = minimum
        self.maximum = maximum
        self.given = given

    def __str__(self) -> str:
        """Say which value was refused, and the bounds of the parameter that refused it."""
        return (
            f"{self.given!r} is not a value of parameter {self.parameter_id!r} "
            f"(minimum {self.minimum!r}, maximum {self.maximum!r})"
        )


class PatchRejectedError(PatchbayError):
    """An instrument refused to load a patch, and nothing about it changed."""

    def __init__(self, reason: str) -> None:
        """Say why the patch was refused."""
        super().__init__(reason)
        self.reason = reason

    def __str__(self) -> str:
        """Give the reason."""
        return f"patch rejected: {self.reason}"


class RenderFailedError(PatchbayError):
    """A render produced nothing usable; a degraded render is a result with warnings instead."""

    def __init__(self, reason: str) -> None:
        """Say why nothing usable was rendered."""
        super().__init__(reason)
        self.reason = reason

    def __str__(self) -> str:
        """Give the reason."""
        return f"render failed: {self.reason}"


class SubscriberFailedError(PatchbayError):
    """One or more subscribers raised while an event was delivered; every subscriber still ran."""

    def __init__(self, event_name: str, errors: tuple[Exception, ...]) -> None:
        """Name the event and carry every subscriber's exception, in the order they were raised."""
        super().__init__(event_name, errors)
        self.event_name = event_name
        self.errors = errors

    def __str__(self) -> str:
        """Say which event, and what each failing subscriber raised."""
        raised = "; ".join(f"{type(error).__name__}: {error}" for error in self.errors)
        return f"{len(self.errors)} subscriber(s) failed on {self.event_name!r}: {raised}"


class PatchbayValidationError(PatchbayError):
    """A model refused its input: pydantic's `ValidationError`, raised as the package's own."""

    def __init__(self, errors: tuple[ErrorDetails, ...]) -> None:
        """Carry pydantic's error details, one per refusal, each with its location and message."""
        super().__init__(errors)
        self.errors = errors

    def __str__(self) -> str:
        """List each refusal as `location: message`, the location dotted."""
        refusals = "; ".join(
            f"{'.'.join(str(part) for part in error['loc']) or '(model)'}: {error['msg']}"
            for error in self.errors
        )
        return f"{len(self.errors)} validation error(s): {refusals}"

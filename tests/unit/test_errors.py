"""Every error is a PatchbayError carrying its fields, with a message built from them."""

import copy

import pytest
from pydantic_core import ErrorDetails

from patchbay.errors import (
    ParameterNotFoundError,
    PatchbayError,
    PatchbayValidationError,
    PatchRejectedError,
    RenderFailedError,
    SubscriberFailedError,
    UnitMismatchError,
    ValueOutOfRangeError,
)

_DETAILS: tuple[ErrorDetails, ...] = (
    {
        "type": "float_type",
        "loc": ("default", "value"),
        "msg": "Input should be a valid number",
        "input": "0.5",
    },
    {"type": "value_error", "loc": (), "msg": "Value error, minimum is above maximum", "input": {}},
)

# One instance of each error, with the message its fields must build.
_ERRORS: tuple[tuple[PatchbayError, str], ...] = (
    (
        ParameterNotFoundError("cutoff", "fake"),
        "instrument 'fake' has no parameter 'cutoff'",
    ),
    (
        UnitMismatchError("cutoff", "hz", "ratio"),
        "parameter 'cutoff' takes unit 'hz', given 'ratio'",
    ),
    (
        ValueOutOfRangeError("cutoff", 20.0, 20000.0, 30000.0),
        "30000.0 is not a value of parameter 'cutoff' (minimum 20.0, maximum 20000.0)",
    ),
    (
        PatchRejectedError("the patch is for instrument 'vital'"),
        "patch rejected: the patch is for instrument 'vital'",
    ),
    (
        RenderFailedError("the device stopped answering"),
        "render failed: the device stopped answering",
    ),
    (
        SubscriberFailedError("parameter.changed", (KeyError("x"), RuntimeError("down"))),
        "2 subscriber(s) failed on 'parameter.changed': KeyError: 'x'; RuntimeError: down",
    ),
    (
        PatchbayValidationError(_DETAILS),
        (
            "2 validation error(s): default.value: Input should be a valid number; "
            "(model): Value error, minimum is above maximum"
        ),
    ),
)


@pytest.mark.parametrize(("error", "message"), _ERRORS, ids=lambda e: type(e).__name__)
def test_message_is_built_from_the_fields(error: PatchbayError, message: str) -> None:
    """str() of each error is the message its fields say, and nothing else."""
    assert str(error) == message


@pytest.mark.parametrize("error", [error for error, _ in _ERRORS], ids=lambda e: type(e).__name__)
def test_error_is_a_patchbay_error_and_no_builtin_subtype(error: PatchbayError) -> None:
    """Each error is caught by `except PatchbayError`, and by no built-in narrower than Exception.

    PatchbayValidationError especially: pydantic's ValidationError is a ValueError and the
    package's is not, so a caller's `except ValueError` never catches a refusal by accident.
    """
    assert isinstance(error, PatchbayError)
    builtins = {cls for cls in type(error).__mro__ if cls.__module__ == "builtins"}
    assert builtins == {Exception, BaseException, object}


@pytest.mark.parametrize(("error", "message"), _ERRORS, ids=lambda e: type(e).__name__)
def test_error_is_rebuilt_from_its_args(error: PatchbayError, message: str) -> None:
    """The fields are args in constructor order, so the reduce protocol rebuilds the error.

    copy and pickle both rebuild an exception as `type(error)(*error.args)`; a constructor whose
    parameters did not match args would raise here.
    """
    rebuilt = copy.deepcopy(error)
    assert type(rebuilt) is type(error)
    assert repr(rebuilt.args) == repr(error.args)
    assert str(rebuilt) == message


def test_fields_are_attributes() -> None:
    """Each field the constructor takes is an attribute of the same name."""
    missing = ParameterNotFoundError("cutoff", "fake")
    assert (missing.parameter_id, missing.instrument) == ("cutoff", "fake")
    mismatch = UnitMismatchError("cutoff", "hz", "ratio")
    assert (mismatch.parameter_id, mismatch.expected, mismatch.given) == ("cutoff", "hz", "ratio")
    out = ValueOutOfRangeError("cutoff", 20.0, 20000.0, 30000.0)
    assert (out.parameter_id, out.minimum, out.maximum, out.given) == (
        "cutoff",
        20.0,
        20000.0,
        30000.0,
    )
    assert PatchRejectedError("why").reason == "why"
    assert RenderFailedError("why").reason == "why"
    first, second = KeyError("x"), RuntimeError("down")
    failed = SubscriberFailedError("parameter.changed", (first, second))
    assert failed.event_name == "parameter.changed"
    assert failed.errors == (first, second)
    assert PatchbayValidationError(_DETAILS).errors == _DETAILS

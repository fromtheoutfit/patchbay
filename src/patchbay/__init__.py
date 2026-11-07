"""patchbay-core: the contracts, host and CLI that patchbay-<instrument> adapters plug into.

The package re-exports what an adapter and a script use, and nothing else lives here: the
Instrument protocol and the Subscriber its events reach (`patchbay.contracts`), the models that
cross a boundary (`patchbay.models`), the events and their bus (`patchbay.events`) and the errors
(`patchbay.errors`). What an adapter's tests use, the contract tests and FakeInstrument among it,
is `patchbay.testing`, imported by name and not re-exported here.

`__version__` is the one in pyproject.toml, read from the installed distribution's metadata so
there is one place it is written. Import the package installed (`uv sync`): from a bare src/ on
sys.path there is no distribution to read, so importlib.metadata raises PackageNotFoundError
rather than the package inventing a version.
"""

import importlib.metadata as _metadata

from patchbay.contracts import Instrument, Subscriber
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
from patchbay.events import Event, EventBus, ParameterChanged, PatchLoaded, RenderCompleted
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

__version__ = _metadata.version("patchbay-core")

__all__ = [
    "Event",
    "EventBus",
    "Instrument",
    "Note",
    "Parameter",
    "ParameterChanged",
    "ParameterId",
    "ParameterNotFoundError",
    "Patch",
    "PatchLoaded",
    "PatchRejectedError",
    "PatchbayError",
    "PatchbayModel",
    "PatchbayValidationError",
    "Pattern",
    "PresetKey",
    "Quantity",
    "RenderCompleted",
    "RenderFailedError",
    "RenderRequest",
    "RenderResult",
    "Subscriber",
    "SubscriberFailedError",
    "Unit",
    "UnitMismatchError",
    "ValueOutOfRangeError",
    "__version__",
]

"""What every adapter promises: the Instrument protocol, and the Subscriber its events reach.

An adapter's instrument implements `Instrument` structurally; it inherits nothing from here. mypy
holds an implementation to the signatures, and the contract tests in `patchbay.testing` hold it
to the behaviour. `isinstance(x, Instrument)` asks only whether `x` has every member, since that
is all a runtime-checkable protocol can ask; `issubclass` is refused, `name` being a data member.

Every method is synchronous. `render` may take wall-clock time, a hardware adapter's say, and its
result records how long (`RenderResult.elapsed_seconds`). Each parameter is positional-only, so an
implementation names its own. An instrument reports a failure as a `PatchbayError`: a parameter it
does not have, a value in the wrong unit or out of range, a patch it refuses, a render it cannot
produce or with nothing usable. A call the instrument refuses changes nothing and publishes
nothing; one it carries out publishes `ParameterChanged`, `PatchLoaded` or `RenderCompleted` once,
on the `EventBus` the instrument was given. A render is `RenderRequest.samples(pattern)` samples
long.

`Subscriber` is defined in `patchbay.events`, beside the bus that takes it, and exported here too.
"""

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from patchbay.events import Subscriber
from patchbay.models import (
    Parameter,
    ParameterId,
    Patch,
    Pattern,
    Quantity,
    RenderRequest,
    RenderResult,
)

__all__ = ["Instrument", "Subscriber"]


@runtime_checkable
class Instrument(Protocol):
    """A software instrument patchbay controls without its screen."""

    @property
    def name(self) -> str:
        """The instrument's name; a patch it loads names the same instrument."""

    def parameters(self) -> Sequence[Parameter]:
        """Every parameter the instrument exposes, each id once."""

    def get(self, parameter_id: ParameterId, /) -> Quantity:
        """Return the parameter's value, the one it holds.

        After `set`, that is the value the parameter holds nearest the one given, as the instrument
        measures it, which is the value given at a bound and at any value `get` has returned; at a
        tie, either of the two. ParameterNotFoundError when there is no such id.
        """

    def set(self, parameter_id: ParameterId, value: Quantity, /) -> None:
        """Set the parameter, then publish ParameterChanged.

        The instrument may hold the nearest value it can to the one given (see `get`). The event's
        `new` is the value the parameter holds after the set, the one `get` returns.
        ParameterNotFoundError, UnitMismatchError or ValueOutOfRangeError when the id, the unit or
        the value is not one the instrument takes; a refused value changes nothing and publishes
        nothing.
        """

    def load_patch(self, patch: Patch, /) -> None:
        """Load the patch whole, then publish PatchLoaded.

        PatchRejectedError when the instrument cannot load all of it, changing nothing.
        """

    def patch(self) -> Patch:
        """Return the instrument's state now, which `load_patch` takes back unchanged."""

    def render(self, pattern: Pattern, request: RenderRequest, /) -> RenderResult:
        """Render the pattern as the request asks, then publish RenderCompleted.

        The result is `request.samples(pattern)` samples long, at the request's sample rate. A
        degraded render is a result with warnings. RenderFailedError, publishing nothing, when
        nothing usable can be rendered, a render longer than the instrument can produce among it.
        """

"""The fixtures an adapter's conftest.py copies: a fresh bus, and an instrument publishing on it.

An adapter returns its own instrument from `instrument`, built on the `bus` fixture, and the
contract tests run against it unchanged. Both are function-scoped: every test starts fresh.
"""

import pytest

from patchbay.contracts import Instrument
from patchbay.events import EventBus
from patchbay.testing import FakeInstrument


@pytest.fixture
def bus() -> EventBus:
    """Give each test a bus no other test has published on."""
    return EventBus()


@pytest.fixture
def instrument(bus: EventBus) -> Instrument:
    """Give each test the instrument under test, publishing on its bus."""
    return FakeInstrument(bus)

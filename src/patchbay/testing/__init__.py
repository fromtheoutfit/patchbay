"""What an adapter's tests use: the contract tests, a reference instrument, a recording subscriber.

`CONTRACT_TESTS` are the tests every adapter runs against its real instrument, each failing with
`ContractViolationError`; `FakeInstrument` is the reference implementation they are proven
against; `RecordingSubscriber` keeps the events it receives. Nothing here is imported by the
package itself, and nothing here imports pytest.
"""

from patchbay.testing.contract_tests import CONTRACT_TESTS, ContractTest, ContractViolationError
from patchbay.testing.fake import FakeInstrument
from patchbay.testing.recording import RecordingSubscriber

__all__ = [
    "CONTRACT_TESTS",
    "ContractTest",
    "ContractViolationError",
    "FakeInstrument",
    "RecordingSubscriber",
]

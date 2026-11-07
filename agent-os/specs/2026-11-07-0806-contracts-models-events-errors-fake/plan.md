# Issue #10: contracts, models, errors, events and FakeInstrument

## Context

Issue #10 is the first code in core. It covers the contracts every adapter implements, the
models that cross package boundaries, the error hierarchy, the in-process event bus, and a
FakeInstrument with contract tests that show the contracts can be implemented. The issue is the
spec's scope and the first Decision in `shape.md`. It is shaped to what one adapter
(patchbay-vital) needs, and anything speculative is named as deferred. You answered 16 shaping
questions (below). Where the issue's design ran into a Python problem, your answer is the
Decision, and each change to the issue's text is recorded against it.

**Scope judgement: one review, not split.** The planned split would ship a Protocol that nothing
implements. The issue's own test plan has the fake and the suite prove each other. Estimate:
about 900 lines in `src/` and 900 in `tests/`, each module small and on its own.

Spec folder: `agent-os/specs/2026-11-07-0806-contracts-models-events-errors-fake/`. Branch:
`feature/10-contracts-instrument-protocol-models-errors-events-and-the-fakeinstrument-reference-implementation`
(current).

## Shaping answers (become shape.md's Shaping answers and Decisions)

- Steps 2–5: no visuals; references are `src/patchbay/__init__.py`, `tests/unit/test_version.py`
  and `tests/unit/test_package.py` (their docstring style and hypothesis form); the product is
  aligned as written; standards are `base/python/toolchain` (core) plus `process/ownership`,
  `process/standards-retrospective`, `process/verification-gate` and `process/standards-sync`,
  as the snapshot at `11ceffd`.
- **Build order (dependency order):** errors → models → events → contracts → testing (recording,
  fake) → contract_tests → `__init__`, with the gate green after each step.
- **Subscriber moves to `events.py`** (it was in `contracts.py`), which removes the
  events↔contracts cycle. `contracts.py` holds `Instrument` and re-exports
  `from patchbay.events import Subscriber as Subscriber`.
- **Version stays 0.0.1.** The entry goes under `[Unreleased]`. 0.1.0 waits until patchbay-vital
  passes the contract tests.
- **Read-only at runtime.** Patch's two mappings are sorted by key and held as
  `MappingProxyType`, with a wrap serializer that hands pydantic a plain dict. `audio` is copied
  and made read-only with `flags.writeable = False`. `RenderResult.__eq__` compares arrays with
  `np.array_equal`. Patch and RenderResult cannot be hashed, and a test asserts that.
- **ValidationError is wrapped at every model entry point.** `PatchbayModel` wraps
  `__init__`, `model_validate`, `model_validate_json`, `model_validate_strings`, `__setattr__`
  and `__delattr__`, and raises `PatchbayValidationError(errors) from` pydantic's error.
  Validators raise `ValueError` inside, as pydantic expects.
- **`Event.at` is set when the event is built:** `datetime.now(UTC)` by default. A validator
  refuses a naive or non-UTC time. The bus never changes an event. This departs from "set by the
  bus".
- **Generic Subscriber:** `class Subscriber[E: Event](Protocol)` with
  `__call__(self, event: E, /) -> None`, `@runtime_checkable`. `subscribe` has two overloads:
  `(type[E], Subscriber[E])` and `(None, Subscriber[Event])`.
- **Contract tests fail with `ContractViolationError(AssertionError)`.** Its fields are `test`,
  `expected` and `actual`. They never import pytest. A test that expects an error goes through a
  `_raises(expected_type, action)` helper.
- **Render duration is renamed `elapsed_seconds`:** the wall-clock time the instrument measures
  around the render with `perf_counter`, at least 0. `audio_seconds` is a plain `@property`
  equal to `audio.shape[1] / sample_rate` and is not stored. `RenderCompleted` carries both
  `elapsed_seconds` and `audio_seconds` as fields. This rename is recorded against the issue's
  `duration_seconds`.
- **`ValueOutOfRangeError(parameter_id, minimum, maximum, given)` is new**, recorded against the
  issue's error list. `load_patch` reports the same case as `PatchRejectedError`.
- **Choice and boolean values:** a choice is `Quantity(index, Unit.none)` with bounds 0 to n−1,
  and a boolean is `Quantity(0|1, Unit.none)` with bounds 0 to 1. Both must be whole numbers.
- **`set` takes only the parameter's own unit.** Any other unit, `ratio` included, raises
  `UnitMismatchError`. Mapping a host's normalized values is the adapter's job and is deferred
  from core.
- **Errors take the `Error` suffix** to satisfy ruff N818, recorded against the issue's names:
  `ParameterNotFoundError`, `UnitMismatchError`, `ValueOutOfRangeError`,
  `PatchRejectedError`, `RenderFailedError`, `SubscriberFailedError`,
  `ContractViolationError`. `PatchbayError` and `PatchbayValidationError` keep their names.
- **`PatchbayModel` is public**: it lives in `models.py`, is listed in `__all__`, and is the
  base of every model and event.
- **Strict mode** (from plan review): `PatchbayModel` sets `strict=True`. See Model config below.
- **`Parameter.check(value)` is public** and raises `UnitMismatchError` or
  `ValueOutOfRangeError`. Parameter's validator uses it for `default` and converts the error to
  `ValueError` for pydantic. The fake and later adapters call it too.

## Decisions taken without a question (listed in shape.md for review)

- **Dependencies.** `pydantic>=2.14.3,<3` (MIT; published 2026-11-05) validates and serializes
  the frozen, typed models. `dataclasses` has no validation and no JSON round trip. `numpy>=2.5.4,<3`
  (BSD-3-Clause, with bundled 0BSD/MIT/Zlib/CC0-1.0; published 2026-10-10) holds the typed
  `(channels, samples)` float32 buffer, which the stdlib `array` module cannot (it is 1-D and has
  no dtype or shape typing). Each lower bound is the locked version and each upper bound is the
  next major. Transitive dependencies get their licenses recorded as `uv.lock` resolves them.
  pydantic needs `typing-extensions>=4.16.0`, and the lock already holds 4.16.0. After `uv lock`,
  `verification/uv-lock-diff.txt` must show additions only, with the ruff, mypy and pytest
  resolutions unchanged, since those are gate files.
- **No pydantic mypy plugin.** `[tool.mypy]` is a gate file. mypy reads pydantic through
  `dataclass_transform`.
- **No ignore-list growth** (the gate's file). A rule the code trips is fixed in code. A coded
  `# noqa` is allowed only where the issue requires the behaviour: `BLE001` on the bus's catch of
  `Exception` from subscribers. PERF203 is avoided with a `_deliver` helper.
- **Protocol shape.** `Instrument.name` is a read-only `@property`, so an implementation can use
  an attribute or a property. Methods take positional-only parameters (`/`), so implementations
  can name theirs freely. `isinstance(x, Instrument)` checks only that the names exist, and
  `issubclass` is unsupported because `name` is a data member. The contract tests check
  behaviour. mypy checks `FakeInstrument` against `Instrument` statically.
- **Model config:** `frozen=True`, `extra="forbid"`, `allow_inf_nan=False`, **`strict=True`**
  (your decision at plan review, recorded against the plan's earlier "Lax mode stays"). The
  reason: a contract library that quietly turns "0.5" into 0.5, or 1 into True, makes the kind of
  implicit conversion the units rule exists to forbid. Under strict, the type is the contract.
  Expected effects, which Task 2 probes:
  - An int is accepted for a float field.
  - A str is refused for a float, and "ratio" is refused where a `Unit` is expected in Python
    mode.
  - A nested model must be an instance, not a dict.
  - A list is refused where a tuple is expected.
  - JSON input behaves the same way, apart from JSON's own forms (an enum value string, an
    object for a nested model, an array for a tuple, base64 for bytes).

  If a probe disagrees with this design, the build stops and comes back to you rather than
  reverting to lax. Only `RenderResult` sets `arbitrary_types_allowed`. Patch sets
  `ser_json_bytes`/`val_json_bytes="base64"` so opaque bytes round-trip unchanged.
- **Validators beyond the issue's text** follow "validators on the model": id, label and
  instrument must be non-empty; `minimum <= maximum`; a ratio parameter's bounds lie within
  [0, 1]; `choices` must be non-empty and unique; `default` must pass `check`; `audio` must have
  at least one channel; `Event.name` must be dotted lowercase (two or more segments); `version`
  must be at least 1. `opaque` defaults to an empty mapping (`validate_default=True`) and
  `choices` defaults to `None`.
- **Event bus.** Subscribers are delivered in subscription order, from a snapshot of the list,
  and type filtering uses `isinstance`. `SubscriberFailedError(event_name, errors)` is raised
  after every subscriber has run, chained `from errors[0]`. Only `Exception` is caught, never
  `BaseException`. There is no unsubscribe (deferred).
- **FakeInstrument semantics.** `set` checks the value, stores it, then publishes
  `ParameterChanged(id, old, new)` once, even when old equals new. `load_patch` rejects with
  `PatchRejectedError` (wrong instrument, unknown id, wrong unit, out of range), checks
  everything before changing anything, fills missing parameters with their defaults, keeps
  opaque sections as given, and publishes only `PatchLoaded(instrument, len(values))`. If a
  subscriber fails, `SubscriberFailedError` propagates from the method after the change is
  committed. `correlation_id` is a `uuid4().hex` per call, and `source` is the instrument's name.
  `render` produces one channel of float32: a sine per note at its pitch, scaled by velocity and
  level, with a linear decay over the decay parameter. Summed audio is clipped to ±1, and any
  clipping adds a warning (the degraded-result path). The sample count is
  `round((bars × beats_per_bar × 60 / tempo + tail) × sample_rate)`. The other parameters are
  stored but don't affect the sound ("deliberately boring").
- **Eight fake parameters:** level (ratio), cutoff (hz), resonance (percent), decay (seconds),
  detune (semitones), drive (db), waveform (choice), mono (boolean). They cover all three kinds
  and seven units.
- **Contract tests**, each `test_<property>(instrument, bus) -> None` and listed in
  `CONTRACT_TESTS`:
  - parameters are unique and typed
  - get after set returns what was set
  - a wrong unit raises `UnitMismatchError`
  - an unknown id raises `ParameterNotFoundError`
  - an out-of-range value raises `ValueOutOfRangeError`
  - `patch()` round-trips through `load_patch`
  - `render` returns the declared shape and sample rate (the exact sample count above, one
    channel or more)
  - `set`, `load_patch` and `render` each emit their event exactly once
  - a refused mutation emits nothing and changes nothing

  They compute the expected sample count on their own, not through the fake's code.
- **Layout.** `RecordingSubscriber` goes in `testing/recording.py`. `testing/__init__.py` holds
  only re-exports and `__all__`. The root `__init__` re-exports contracts, models, events and
  errors (not `testing`) and keeps `__version__`, which predates the issue's "nothing else". No
  `from __future__ import annotations`, because pydantic needs real annotations.
- **Deferred (shape.md):** the pedalboard host, the CLI, entry-point discovery, transports,
  async, and event persistence (all from the issue); plus unsubscribe, JSON and JSON-schema
  output for `RenderResult` (its pydantic serialization isn't wrapped), normalized-value mapping,
  and the pydantic mypy plugin (a gate spec).

## Tasks

**Task 1: Save the spec documentation.** Create the spec folder with `plan.md` (this plan),
`shape.md`, `standards.md`, `references.md` and an empty `verification/`. `shape.md`'s first
Decision cites issue #10. `standards.md` holds the full text of the five standards. The template
is `agent-os/specs/2026-11-07-0711-gate-revision-after-pr-9-review/shape.md`.

**Task 2: Dependencies and probes.** Add pydantic and numpy to `[project] dependencies`, run
`uv lock` (never `--upgrade`), then `uv sync --locked`, and save `verification/uv-lock-diff.txt`.
On a scratch copy, probe the pinned versions and write `verification/probes.txt`:
- `Mapping` validates to a dict; `MappingProxyType` with the wrap serializer gives clean JSON
  with no warning; base64 bytes round-trip.
- frozen `hash()` raises `TypeError` on a dict or array; `==` on arrays raises `ValueError`
  before the fix.
- an `NDArray[np.float32]` arbitrary type is checked with `isinstance`.
- mypy, without the plugin, still synthesizes typed `__init__` for subclasses of a base that
  overrides `__init__`.
- `__setattr__`/`__delattr__` on a frozen model raise `ValidationError`.
- `runtime_checkable` `isinstance` works with a property member.
- PEP 695 Subscriber variance comes out contravariant.
- Strict mode, in both Python and JSON input:
  - int accepted for a float field
  - str refused for float, int and `Unit` (Python mode)
  - an enum value string accepted from JSON
  - bool refused for int and int refused for bool
  - a nested dict refused in Python mode and accepted from JSON
  - a list refused for a tuple in Python mode and accepted from JSON
  - base64 bytes accepted from JSON
  - whether a `MappingProxyType`, such as another Patch's `values`, is accepted for a `Mapping`
    field (if it is refused, the fake passes `dict(...)`)
- If a strict probe disagrees with the design, stop and ask before going further.

Each probe uses cases that tell the competing claims apart, and shows its setup worked.

**Task 3: `src/patchbay/errors.py`** with `tests/unit/test_errors.py`.
- Each error takes typed fields and calls `super().__init__(*fields)`, so `args` and pickle
  round-trip work.
- Each builds `__str__` from its fields.
- `PatchbayValidationError.errors` is a `tuple[ErrorDetails, ...]`.
- Model types are imported under `TYPE_CHECKING`.
- Tests cover `__str__`, the fields, a pickle round trip of each error, and the hierarchy.
- Gate green.

**Task 4: `models.py`** with `tests/unit/test_models.py`.
- Covers `ParameterId`/`PresetKey`, `Unit`, `PatchbayModel`, `Quantity`, `Parameter`
  (with `check`), `Patch`, `Note`, `Pattern`, `RenderRequest` and `RenderResult`.
- Unit tests for every validator.
- Hypothesis properties: `Quantity` ratio bounds; the `Note` and `Pattern` validators; `Patch`
  JSON round trip with arbitrary `st.binary()` opaque bytes and arbitrary keys, with
  deterministic key order.
- Read-only mappings and array, `RenderResult` equality, unhashability, and every entry point
  raising `PatchbayValidationError` (never pydantic's).
- A typing test: passing a `PresetKey` where `ParameterId` is expected carries
  `# type: ignore[arg-type]`, so strict mypy's `warn_unused_ignores` fails if the refusal ever
  stops.
- Gate green.

**Task 5: `events.py`** with `tests/unit/test_events.py`.
- Covers `Event`, `ParameterChanged`, `PatchLoaded`, `RenderCompleted` (each `name` a `Literal`
  default), `Subscriber` and `EventBus`.
- Delivery: type filtering, the `None` case, order, a snapshot under re-entrancy.
- A failing subscriber doesn't hide the event from the others, and `SubscriberFailedError`
  carries every error.
- `at` defaults to UTC and refuses naive or non-UTC times.
- Gate green.

**Task 6: `contracts.py`** with `tests/unit/test_contracts.py`.
- `Instrument` and the re-exported `Subscriber`.
- `isinstance` succeeds for a conforming object and fails for one missing a member; a plain
  function `isinstance`-checks as a `Subscriber`.
- Gate green.

**Task 7: `testing/__init__.py`, `testing/recording.py` and `testing/fake.py`**, with
`tests/unit/testing/conftest.py` (the `bus` and `instrument` fixtures an adapter copies),
`test_recording.py` and `test_fake.py`.
- `instrument: Instrument = FakeInstrument(bus)` is checked by mypy.
- The render output is checked: sample count, decay, clipping warning.
- Each mutating method's event is asserted (table below).
- Gate green.

**Task 8: `testing/contract_tests.py`** with `tests/unit/testing/test_contract_tests.py`.
- Every entry in `CONTRACT_TESTS` passes against FakeInstrument (parametrized, as an adapter
  would).
- Each contract test also has a deliberately broken `FakeInstrument` subclass that makes it
  raise `ContractViolationError`. That shows the suite can fail, which is how the fake proves the
  suite.
- Gate green.

**Task 9: `src/patchbay/__init__.py`**: re-exports and `__all__`, plus `__version__`.
`test_package.py` gains a check that every name in `__all__` resolves. Gate green.

**Task 10: Docs and CHANGELOG.**
- `README.md`: Layout says what the package exports and that `tests/` now has
  `unit/testing/conftest.py`.
- The `__init__` docstring.
- `tech-stack.md`: a numpy line, and pydantic in use.
- A `CHANGELOG.md` `[Unreleased]` → `### Added` entry for the seventh spec, with the version at
  0.0.1.

**Task 11 (final): Verification gate.**
1. `scripts/gate.sh` runs steps 1–6 in order:
   1. `bash -n` on every shell script git lists under `scripts/`, at the repository root
   2. `uv sync --locked`, then `ruff format --check`
   3. `ruff check`
   4. `mypy`
   5. `pytest`
   6. `scripts/sync-standards.sh --check` against `../patchbay-standards` at `11ceffd`

   It exits 1 at the first failure and 2 on usage. Its output is saved to
   `verification/gate-run.txt`, headed with the date and branch, as the last act. No gate file
   changes, so no negative tests are rerun.
2. **Docs** (step 7): record in `shape.md` what was checked, including the
   `base/python/toolchain.md` lines this spec makes false: "dependencies is empty", "patchbay has
   none yet" (noqa) and "imports nothing untyped yet".
3. **Version** (step 8): the `[Unreleased]` entry, with no bump.
4. **Standards retrospective** (step 9, from the shipped diff):
   - Write proposals for the layout, typing, models, errors, events and testing standards the
     issue expects, plus the toolchain.md corrections. N818 is a candidate for the gate spec's
     ignore list, and the runtime dependency specifier form needs stating.
   - Present them with AskUserQuestion, multi-select: at most three per question, each question
     ending with "None of these", at most four questions per call.
   - File the approved ones as one `gh issue create --repo fromtheoutfit/patchbay-standards`, with
     no attribution, and write the number beside each. Mark each declined one
     `declined by owner, <date>`.
   - Always record `Proposals sent upstream:`.
5. Stop. Print `git status --short`, listing the retrospective's files separately. No stage,
   commit, push or PR.

## Events asserted per public mutating method

| Method | Event | Asserted in |
|---|---|---|
| `FakeInstrument.set` | `ParameterChanged` ×1 (none when refused) | test_fake, contract test |
| `FakeInstrument.load_patch` | `PatchLoaded` ×1 (none when rejected) | test_fake, contract test |
| `FakeInstrument.render` | `RenderCompleted` ×1 | test_fake, contract test |
| `EventBus.publish` | the given event, once to each subscriber | test_events |
| `EventBus.subscribe` | none by design; its test asserts later delivery | test_events |
| `RecordingSubscriber.__call__` | records the event; no event of its own | test_recording |

## Verification

- After each of Tasks 3–9: run `scripts/gate.sh` and get exit 0.
- After Task 2: the lock diff contains additions only, and the probes match the design (a probe
  that disagrees stops the build and comes back to you).
- End to end: `uv run --locked pytest -q`. The contract suite passes against FakeInstrument, and
  every broken-fake case fails with `ContractViolationError`.
- `verification/gate-run.txt` comes from the final run.

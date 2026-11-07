# Contracts, models, errors, events and FakeInstrument — Shaping Notes

Shaped 2026-11-07 in plan mode with this repository's customized `/agent-os:shape-spec`. The owner
answered the Step 2–5 questions and twelve design questions, one of them in their own words (the
render duration), changed one plan Decision at plan review (strict mode), and answered three
questions the probes raised before any module was written (`verification/probes.txt`).

## Core Architecture (Non-Negotiable)

- `base/python/toolchain` — included without asking (Step 5a); its full text in `standards.md`.
  It applies to every file this spec adds.

## Scope

GitHub issue #10, "Contracts: Instrument protocol, models, errors, events and the FakeInstrument
reference implementation": the first code in core. `src/patchbay/` gains `errors.py`,
`models.py`, `events.py`, `contracts.py` and `testing/` (`recording.py`, `fake.py`,
`contract_tests.py`), and `__init__.py` re-exports them; `tests/unit/` mirrors `src/`. pydantic
and numpy join `[project] dependencies`. No host, no CLI, no plugin dependency. Judged one review
at shaping, not split at the issue's seam: the first half would ship a Protocol nothing
implements, and the issue's own test plan has the fake and the suite prove each other.

## Shaping answers

- **Step 1, scope:** issue #10, as the arguments to the command gave it.
- **Step 2, visuals:** none.
- **Step 3, references:** the existing Python, `references.md`.
- **Step 4, product context:** aligned as written; numpy gets its line in `tech-stack.md`.
- **Step 5, standards:** `base/python/toolchain` (core); `process/ownership`,
  `process/standards-retrospective`, `process/verification-gate`, `process/standards-sync`.
  Snapshot at `11ceffd`.
- **Build order** (owner): dependency order, not the issue's listing order, since `contracts.py`
  cannot pass mypy before the models and events it names exist: errors, models, events,
  contracts, testing, contract_tests, `__init__`, the gate green after each.
- **Version** (owner): stays 0.0.1; 0.1.0 when patchbay-vital runs the contract tests green.
- **Frozen insides** (owner): read-only at runtime.
- **Validation boundary** (owner): every model entry point.
- **`Event.at`** (owner): stamped at construction.
- **Subscriber** (owner): generic, positional-only.
- **Contract test failures** (owner): `ContractViolationError`, no pytest import.
- **Render duration** (owner, in their words): "Wall-clock render time, but named elapsed_seconds
  (>= 0, measured by the instrument around the render), not duration_seconds. The audio's length
  is a computed property audio_seconds = audio.shape[1] / sample_rate, not stored.
  RenderCompleted carries elapsed_seconds and audio_seconds both, since an event subscriber has
  no array to measure. Record the rename as a Decision against the issue's text."
- **Out of range** (owner): a new `ValueOutOfRangeError`.
- **Choice and boolean values** (owner): an index, and 0 or 1, in `Unit.none`.
- **Normalized values** (owner): `set` takes the parameter's own unit only.
- **The events/contracts cycle** (owner): `Subscriber` moves to `events.py`.
- **ruff N818** (owner): the errors take the `Error` suffix.
- **Shared base model** (owner): public `PatchbayModel`.
- **The value rule** (owner): public `Parameter.check`.
- **Strict mode** (owner, at plan review): "strict=True in PatchbayModel, not lax. A contract
  library that silently coerces "0.5" to 0.5 or 1 to True is the implicit conversion the units
  rule exists to forbid; strict makes the type the contract."
- **After the probes** (owner, three answers; `verification/probes.txt`):
  - *A dict for a nested model:* strict accepts one in Python input, every field inside it still
    strict; the plan said an instance was required. Accepted as pydantic's strict; no
    `InstanceOf` annotations.
  - *`model_validate_strings`:* parses "0.5" as a float under strict, string input being its
    format. Kept, and wrapped like every other entry point.
  - *Where `frozen` is written:* mypy does not see it through `model_config`, and does through
    the class keyword. `frozen=True` goes on the class line of `PatchbayModel` and of every model
    and event, so mypy refuses an assignment and a subclass that leaves the keyword out.

## Decisions

- **Issue #10 is the spec's scope** (fromtheoutfit/patchbay#10): it names the modules, the
  Protocol's methods, every model's fields, the events and the errors by field, the tests and
  the two dependencies. What follows records where this spec departs from its text, each with
  the owner's answer, and what it decided that the issue leaves open.

### Against the issue's text (each the owner's)

- **`Subscriber` lives in `events.py`**, and `contracts.py` re-exports it
  (`from patchbay.events import Subscriber as Subscriber`). `EventBus.subscribe` takes a
  `Subscriber` and `Subscriber` is bounded by `Event`, so the two modules named each other; with
  `Subscriber` beside the bus, `contracts.py` imports `events.py` and nothing imports back.
- **`Subscriber` is generic**: `class Subscriber[E: Event](Protocol)`, `__call__(self, event: E,
  /) -> None`, `@runtime_checkable`. Callable parameters are contravariant, so under the issue's
  `__call__(Event)` mypy refuses `subscribe(ParameterChanged, handler)` for a handler taking a
  `ParameterChanged`. `EventBus.subscribe` has two overloads, `(type[E], Subscriber[E])` and
  `(None, Subscriber[Event])`. The parameter is positional-only, so a handler names its own.
- **`Event.at` is set when the event is built**, `datetime.now(UTC)` by default, and a validator
  refuses a naive or non-UTC time; the bus never alters an event. The issue's "set by the bus if
  absent" on a frozen event makes `at` optional in every subscriber's type and delivers a copy in
  place of the object published.
- **`RenderResult.duration_seconds` is `elapsed_seconds`**, the wall-clock time the instrument
  measures around the render (`time.perf_counter`), `>= 0`. The audio's length is the property
  `audio_seconds = audio.shape[1] / sample_rate`, a plain `@property`, not stored and not
  serialized. `RenderCompleted` carries `elapsed_seconds` and `audio_seconds` as fields, since a
  subscriber has no array to measure.
- **`ValueOutOfRangeError(parameter_id, minimum, maximum, given)` joins `errors.py`.** A value
  outside `[minimum, maximum]`, or a choice or boolean value that is not a whole number, had no
  error in the issue's list, and a built-in may not escape. `load_patch` reports the same case
  as `PatchRejectedError`.
- **Every exception but the root's two ends in `Error`**: `ParameterNotFoundError`,
  `UnitMismatchError`, `ValueOutOfRangeError`, `PatchRejectedError`, `RenderFailedError`,
  `SubscriberFailedError` and, in `patchbay.testing`, `ContractViolationError`. ruff's N818 refuses
  the issue's names under `select = ["ALL"]`, and the ignore list grows only in the gate's spec.
- **`PatchbayModel` is public**, in `models.py` and `__all__`: the base of every model and event,
  so an adapter's own models follow the same rules by inheriting it. A name the issue does not
  list.
- **`Parameter.check(value)` is public**: it raises `UnitMismatchError` when the unit is not the
  parameter's, and `ValueOutOfRangeError` when the value is outside the range or, for a choice or
  boolean, not a whole number. `Parameter`'s validator holds `default` to it, the fake's `set`
  and `load_patch` call it, and so will an adapter. A method the issue does not name.
- **`PatchbayModel` is strict** (`strict=True`; the owner, at plan review, against the plan's
  "Lax mode stays"): the type is the contract, so "0.5" is not 0.5 and 1 is not True. What strict
  admits and refuses at the pinned pydantic is `verification/probes.txt`: an int for a float, a
  dict for a nested model (strict inside), and `model_validate_strings`' parsing of strings are
  admitted, the last two corrected against the plan with the owner after the probes.

### What the issue leaves open

- **pydantic and numpy join `[project] dependencies`.**
  - **pydantic** (`pydantic>=2.14.3,<3`; 2.14.3 published 2026-11-05; MIT): validates and
    serializes the frozen, typed models every contract crosses a boundary in, with validators on
    the model and a JSON round trip. The standard library's `dataclasses` validates nothing and
    has no JSON form. It brings `pydantic-core` (MIT), `annotated-types` (MIT),
    `typing-inspection` (MIT) and `typing-extensions` (PSF-2.0), the last already locked for mypy
    at the version pydantic needs.
  - **numpy** (`numpy>=2.5.4,<3`; 2.5.4 published 2026-10-10; BSD-3-Clause, its wheels bundling
    code under 0BSD, MIT, Zlib and CC0-1.0): the rendered audio, a typed `(channels, samples)`
    float32 buffer. The standard library's `array` is one-dimensional and its type carries no
    dtype or shape.
  - **The specifier form:** the version the gate ran as the floor, the next major as the
    ceiling. A library's dependencies are ranges, not the dev group's exact pins: an adapter
    installs core beside its own dependencies. No standard says this yet.
- **`[tool.mypy]` gets no pydantic plugin**, since it is a gate file; mypy reads the models through
  pydantic's `dataclass_transform`.
- **No rule is ignored; the code is fixed.** One coded suppression, `# noqa: BLE001` on the bus's
  catch of `Exception` from a subscriber, the behaviour the issue asks for.
- **The Protocol.** `Instrument.name` is a read-only `@property`, so an implementation may use an
  attribute or a property. Every method's parameters are positional-only, so an implementation
  names its own. `isinstance(x, Instrument)` checks that the names exist, and `issubclass` is
  refused for a Protocol with a data member: the contract tests check behaviour, mypy checks the
  fake against the Protocol.
- **Model config.** `extra="forbid"`, `allow_inf_nan=False` and `strict=True` in `PatchbayModel`'s
  `model_config`; `frozen=True` as a class keyword on `PatchbayModel` and repeated on every model
  and event (owner, after the probes), which mypy reads and `model_config` it does not.
  `RenderResult` alone allows arbitrary types. `Patch` serializes and validates bytes as base64 in
  JSON, so opaque bytes round-trip whatever they hold.
- **Read-only at runtime** (owner). `Patch.values` and `Patch.opaque` are sorted by key and held as
  `MappingProxyType`, with a wrap serializer that hands pydantic a plain dict; `RenderResult.audio`
  is copied and marked read-only; `RenderResult.__eq__` compares arrays with `np.array_equal`.
  Neither model is hashable, and a test holds that.
- **Every model entry point raises `PatchbayValidationError`** (owner): `PatchbayModel` wraps
  `__init__`, `model_validate`, `model_validate_json`, `model_validate_strings`, `__setattr__` and
  `__delattr__`, raising `PatchbayValidationError(errors)` from pydantic's error. Validators raise
  `ValueError`, as pydantic expects.
- **Validators beyond the issue's text**, as "validators on the model" asks: non-empty id, label,
  instrument, source and correlation id; `minimum <= maximum`; a ratio parameter's bounds within
  `[0, 1]`; `choices` non-empty and unique; a choice's bounds `0` to `len(choices) - 1` and a
  boolean's `0` to `1`, both in `Unit.none`; `default` passing `check`; at least one channel of
  audio; `Event.name` dotted lowercase with two or more segments; `version >= 1`. `opaque`
  defaults to an empty mapping and `choices` to `None`.
- **The bus.** Subscribers run in the order they subscribed, over a snapshot of the list, so one
  that subscribes during a publish is not called for that event; a type filter is `isinstance`.
  `SubscriberFailedError(event_name, errors)` is raised after every subscriber has run, from the
  first error. Only `Exception` is caught. No unsubscribe.
- **FakeInstrument.** `set` checks, stores, then publishes `ParameterChanged(id, old, new)` once,
  even when the value is unchanged. `load_patch` checks the whole patch before changing anything
  and refuses with `PatchRejectedError` (another instrument's patch, an unknown id, a wrong unit,
  a value out of range), sets the parameters the patch leaves out to their defaults, keeps its
  opaque sections as given, and publishes `PatchLoaded(instrument, len(values))` and no
  `ParameterChanged`. A subscriber's failure reaches the caller as `SubscriberFailedError`
  after the change is made. Each call's events carry a fresh `uuid4().hex` correlation id, and
  the instrument's name as their source. `render` is one float32 channel: a sine per note at its
  pitch, scaled by velocity and level, falling linearly to silence over the decay parameter;
  summed audio is clipped to ±1 and a clip adds a warning, the degraded path. Its length is
  `round((bars × beats_per_bar × 60 / tempo_bpm + tail_seconds) × sample_rate)` samples. The
  other parameters are stored and do not sound: deliberately boring.
- **The fake's eight parameters**: `level` (ratio), `cutoff` (hz), `resonance` (percent),
  `decay` (seconds), `detune` (semitones), `drive` (db), `waveform` (choice) and `mono`
  (boolean): every kind and seven of the eight units.
- **The contract tests** are functions `test_<property>(instrument, bus) -> None`, listed in
  `CONTRACT_TESTS` for an adapter to parametrize over, each failing with
  `ContractViolationError(test, expected, actual)`. They compute what they expect themselves,
  never through the fake's code.
- **Layout.** `RecordingSubscriber` lives in `testing/recording.py`; `testing/__init__.py` holds
  re-exports and `__all__` only. The root `__init__.py` re-exports contracts, models, events and
  errors (not `testing`) and keeps `__version__`, which predates the issue's "nothing else". No
  module uses `from __future__ import annotations`: pydantic reads the annotations at runtime.
- **Every public mutating method has a test asserting its event**: `FakeInstrument.set`,
  `load_patch` and `render` (in `tests/unit/testing/test_fake.py` and the contract tests),
  `EventBus.publish` (`tests/unit/test_events.py`). `EventBus.subscribe` and
  `RecordingSubscriber.__call__` are the event mechanism and emit none; their tests assert
  delivery and recording.

### Found while building, recorded here before the spec was done

- **`PatchbayModel.__init__` carries pydantic's base-init marker.** The first draft overrode
  `__init__` to wrap refusals, and a `Patch`'s JSON round trip failed. pydantic calls a model's
  own `__init__` to build a nested model, with the parsed input in Python mode, so strict refused
  JSON's enum string and the refusal lost its path. `BaseModel.__init__` carries
  `__pydantic_base_init__ = True`. Ours validates exactly what it does, so it carries the same
  marker (`verification/probes.txt`, `models_init.py`; `tests/unit/test_models.py`,
  `test_a_patch_round_trips_through_json_byte_for_byte`).
- **`errors.py` imports nothing from the package.** An id or a unit is typed `str`, which a
  `ParameterId` and a `Unit` each are, and a bound or value is typed `float`. In dependency order
  errors comes first and passes the gate alone, and `models.py` imports it, so it cannot import
  `models.py` back. The issue's names and fields are unchanged.
- **`Patch` and `RenderResult` say they are unhashable the way Python does,** with
  `__hash__: ClassVar[None] = None`. pydantic's frozen hash would raise on a mapping or an array,
  and ruff's PLW1641 asks for it beside `RenderResult.__eq__`.
- **The coded suppressions, each for a reason the code cannot remove:**
  - `# noqa: BLE001` in the bus. Catching every `Exception` is the behaviour the issue asks for.
  - `# noqa: PLR0913` on `model_validate`, `model_validate_json` and `model_validate_strings`.
    Their parameters are pydantic's, and mypy holds an override to them, so wrapping every entry
    point (the owner's answer) means overriding them whole.
  - `# type: ignore[attr-defined]` on the base-init marker, and `# type: ignore[assignment]` on
    the two `__hash__ = None`.

  The plan named only BLE001; the PLR0913s follow from two decisions already taken. Every other
  rule the code tripped was fixed in the code. In the tests, a `# type: ignore[<code>]` holds a
  refusal mypy must keep making, and strict's `warn_unused_ignores` fails the gate if one stops:
  a `PresetKey` where a `ParameterId` is expected, `issubclass` of `Instrument`, an assignment to
  a frozen field (twice) and an item assigned into a `Patch`'s mapping.
- **`tests/unit/test_package.py` leaves submodules out** of the names it holds to `__all__`.
  Importing `patchbay.errors` binds `errors` on the package, which is the import system's doing
  rather than an export. The test also holds every exported name to the object its module
  defines.
- **The contract tests are eleven.** "A refused mutation emits nothing and changes nothing" is
  checked inside the wrong-unit, unknown-id and out-of-range tests, and for `load_patch` by
  `test_a_rejected_patch_changes_nothing`. They set values at a parameter's bounds. Each is
  proven by a fake broken its way, and the test asserts the reason it gives, not only that it
  fails.
- **`RecordingSubscriber.of_type(E)`** returns the recorded events of one type, typed as that
  type. **`patchbay.testing.fake.PARAMETERS`** is public, so a test can read the fake's
  parameters without building one.

## Deferred

From the issue: the pedalboard host, the CLI, entry-point discovery of adapters, any transport
(WebSocket, OSC, MIDI), async, persistence of events. From shaping: unsubscribe; JSON and JSON
schema for `RenderResult` (pydantic's serialization of it is not wrapped); mapping a host's
normalized values onto a parameter's range; the pydantic mypy plugin, a gate spec's to add. Each
arrives when a spec needs it.

## Context

- **Visuals:** None.
- **References:** `references.md`.
- **Product alignment:** aligned as written: FakeInstrument's parameters are generic fixtures,
  not a synth's concepts; `tech-stack.md` already names pydantic and gains numpy.

## Standards Applied

**Core (always applied):**
- `base/python/toolchain` — Step 5a; every file this spec adds is formatted, linted, typed and
  tested under it, and its Dependencies section asks each dependency's Decision above.

**Feature-specific:**
- `base/process/ownership` — no stage, commit, push or pull request; the upstream issue carries no
  attribution.
- `base/process/standards-retrospective` — the layout, typing, models, errors, events and testing
  standards the issue expects are proposals from this tree, presented to the owner and filed.
- `base/process/verification-gate` — not the gate's spec: its files, the ruff ignore list and
  `[tool.mypy]` among them, do not change here.
- `base/process/standards-sync` — step 6 of the gate; nothing here syncs.

## Verification Gate

Spec is not complete until `scripts/gate.sh` passes — `bash -n` on every shell script under
`scripts/` as git lists them, at a work-tree top that is the repository root; `uv sync --locked`,
then `uv run --locked ruff format --check` and `uv run --locked ruff check` over the `.py` and
`.pyi` files git lists, `uv run --locked mypy` over those under `src/` and `tests/`, and
`uv run --locked pytest` once nothing it would read is ignored, under `pyproject.toml`'s `[tool.*]`
rule set and `uv.lock`'s pins; and `scripts/sync-standards.sh --check` against
`../patchbay-standards` at the commit in `agent-os/standards/base/.version` — and the three
judgment steps are recorded, in this order: Docs, Version, then the standards retrospective below.

**Results (2026-11-07):** exit 0 on branch
`feature/10-contracts-instrument-protocol-models-errors-events-and-the-fakeinstrument-reference-implementation`,
`verification/gate-run.txt`, the last thing done before hand-over. The gate was green after each
build step, in the owner's dependency order: errors (28 tests), models (103), events (127),
contracts (131), testing with the fake (162), the contract tests (186) and `__init__` (188). No
gate file changed, so no negative test was rerun. `verification/probes.txt` holds the pydantic,
numpy and mypy behaviour the design rests on. `verification/uv-lock-diff.txt` shows the lock
gaining pydantic, numpy and their dependencies and nothing else.

**Docs (step 7):**

- **`README.md`:** Layout names each module, `testing/` and the conftest an adapter copies, and
  says the package exports more than `__version__`. Install says `uv sync` installs pydantic and
  numpy too. The gate and sync sections are unchanged and still read true.
- **`agent-os/product/tech-stack.md`:** pydantic in use on `PatchbayModel`, and numpy's line.
  `mission.md` is unchanged and reads true: nothing synth-specific is in core.
- **Headers and docstrings:** each new module's docstring was read against the code beside it.
  `__init__.py`'s docstring now names the re-exports. `pyproject.toml`'s header still says adding
  a dependency is a Decision; the comment over `dependencies` says why the entries are ranges.
- **`CLAUDE.md` and `shape-spec.md`:** no statement about the package's contents; unchanged.
- **`base/python/toolchain.md` against this tree** reads false in three places, which are
  proposals below, not edits:
  - "Dependencies": `dependencies` is no longer empty.
  - "ruff": the tree now has coded suppressions, so "patchbay has none yet" is stale.
  - Neither "ruff" nor "mypy" says how a `type: ignore` is written.

  Its other rules read true: pydantic and numpy are typed, so `[tool.mypy]` still needs no
  override.
- **Line widths:** no prose line this spec wrote is over 100 columns.

**Version (step 8):** the seventh spec's entry, under `[Unreleased]`, `### Added`, in
`CHANGELOG.md`. The version stays 0.0.1 (the owner): 0.1.0 when patchbay-vital passes the contract
tests.

## Standards Retrospective

Step 9, always last, from the shipped diff against `3f910d8`.

1. *A pattern no standard covers?* Most of the spec: it is the first code in core, and the issue
   says the layout, typing, models, errors, events and testing standards are written in
   `patchbay-standards` from this tree. Each is a proposal below (1–6). No project standard
   exists to take any of them, and each belongs to every patchbay package, not only to core.
2. *A standard wrong or stale?* `base/python/toolchain.md`, in three places (Docs, above):
   proposals 7 and 8.
3. *A deliberate deviation?*
   - **Deviation, not a standard change:** the modules were built in dependency order, not the
     issue's listing order (the owner, at shaping), since `contracts.py` cannot pass mypy before
     what it names exists. Proposal 6 states the order a package's modules are built in.
   - **Deviation, not a standard change:** where this spec departs from the issue's text, each
     departure is the owner's answer and a Decision above. The issue's text is the scope, not a
     standard.
   - ruff's N818 was kept, not proposed for the ignore list: the owner chose the `Error` suffix,
     so the rule is right for this tree.
4. *A moved pointer?* None. `toolchain.md`'s pointers into this repository
   (`tests/unit/test_package.py`, `pyproject.toml`'s sections) still resolve.

No project standard exists to edit, and `agent-os/standards/index.yml` is untouched. The
retrospective's own change set is this section; it edited no file outside this spec folder.

Proposals sent upstream: fromtheoutfit/patchbay-standards#21.

### Standards retrospective (proposed, base)

Presented to the owner on 2026-11-07 with AskUserQuestion, multi-select, in three questions: 1–3,
4–6 and 7–8, each ending with "None of these". All eight were approved and filed as one issue,
fromtheoutfit/patchbay-standards#21, a standards spec, since none needs a gate file changed. It has
one section per proposal with its verification pointers, a "Depends on" line naming this branch,
and the rules its spec is held to. No AI attribution.

Each is verified against this spec's shipped files and tests, and against
`verification/probes.txt` where it rests on how pydantic, numpy or mypy behave.

1. `base/python/models.md` (new): every model derives from one public base. It is frozen (as a
   class keyword on every class line, which mypy reads and `model_config` it does not), closed
   (`extra="forbid"`), finite (`allow_inf_nan=False`) and strict. Every entry point pydantic
   validates through raises the package's error from pydantic's: the constructor (carrying the
   base-init marker), `model_validate`, `model_validate_json`, `model_validate_strings`,
   assignment and deletion. Validators raise `ValueError` inside. Containers in a frozen model
   are read-only (a `MappingProxyType` with a wrap serializer, an unwriteable array copy). A
   model that cannot hash says so with `__hash__ = None`. Bytes go into JSON as base64.
   Verified against `src/patchbay/models.py`, `tests/unit/test_models.py` and probes
   `runtime.py`, `typing_probe.py`, `frozen_kw2.py`, `config_form.py` and `models_init.py`.
   Proposed, not applied; filed as fromtheoutfit/patchbay-standards#21.
2. `base/python/errors.md` (new): one root per package. Every exception ends in `Error`
   (ruff N818). Each takes its fields as arguments in order, keeps them as attributes and passes
   them to `Exception`, so `args` and the reduce protocol rebuild it, and builds `__str__` from
   them. No built-in leaves a public method. The errors module imports nothing from its package,
   typing fields as plain values. Verified against `src/patchbay/errors.py` and
   `tests/unit/test_errors.py`. Proposed, not applied; filed as fromtheoutfit/patchbay-standards#21.
3. `base/python/events.md` (new):
   - An event is a frozen model whose dotted, past-tense name is fixed per class by a `Literal`.
     It is stamped in UTC when built, a naive or offset time is refused, and its payload is typed
     fields.
   - The bus is synchronous and in-process. It delivers in subscription order over a snapshot,
     runs every subscriber before raising one error carrying each failure (`Exception` only),
     and never alters an event.
   - The subscriber protocol is generic, contravariant and positional-only.

   Verified against `src/patchbay/events.py`, `tests/unit/test_events.py` and probe
   `typing_probe.py` (G–I). Proposed, not applied; filed as fromtheoutfit/patchbay-standards#21.
4. `base/python/testing.md` (new):
   - Contract tests ship in the package's `testing` subpackage as plain functions
     `test_<property>(instrument, bus)`, listed in one tuple an adapter parametrizes over. They
     fail with an `AssertionError` subclass carrying fields, never `assert` and never pytest.
   - Each contract test is proven by a reference fake broken its way, asserted for its reason.
   - The fixtures are function-scoped `bus` and `instrument` in a `conftest.py`.
   - Tests mirror the source, one module per module.
   - A `# type: ignore[<code>]` in a test holds a refusal mypy must keep making.

   Verified against `src/patchbay/testing/contract_tests.py`,
   `tests/unit/testing/test_contract_tests.py`, `tests/unit/testing/conftest.py` and
   `tests/unit/test_models.py` (`test_a_preset_key_is_not_a_parameter_id`). Proposed, not
   applied; filed as fromtheoutfit/patchbay-standards#21.
5. `base/python/typing.md` (new):
   - Distinct keys are distinct `NewType`s.
   - A Protocol's data members are read-only properties and its methods' parameters
     positional-only. A runtime check is `isinstance`, which checks names only (`issubclass` is
     refused, by mypy too, for a protocol with a data member).
   - Generics use PEP 695 syntax.
   - A module re-exports through `__all__` under `implicit_reexport = false`.
   - No `from __future__ import annotations` where pydantic reads the annotations.

   Verified against `src/patchbay/contracts.py`, `events.py`, `models.py`,
   `tests/unit/test_contracts.py` and probes `runtime.py` (7) and `typing_probe.py`. Proposed,
   not applied; filed as fromtheoutfit/patchbay-standards#21.
6. `base/python/layout.md` (new):
   - `src/<package>/` holds a module per concern: contracts, models, events, errors, and a
     `testing/` subpackage shipped in the wheel for adapters' tests.
   - `__init__.py` holds re-exports, `__all__` and `__version__` only.
   - Modules are built in dependency order, the errors module a leaf.
   - The surface test leaves submodules out of the names it holds to `__all__`.

   Verified against `src/patchbay/`, `tests/unit/test_package.py` and the gate green after each
   module (Results, above). Proposed, not applied; filed as fromtheoutfit/patchbay-standards#21.
7. `base/python/toolchain.md`, "Dependencies":
   - A runtime dependency is a range: the version the gate ran as the floor, the next major as
     the ceiling, since an adapter installs the package beside its own.
   - Adding one shows, in the spec's `verification/`, that the lock gained it and changed no
     tool the gate runs.
   - The example "`dependencies` is empty" is replaced by patchbay's pydantic and numpy.

   Verified against `pyproject.toml` and `verification/uv-lock-diff.txt`. Proposed, not applied;
   filed as fromtheoutfit/patchbay-standards#21.
8. `base/python/toolchain.md`, "ruff" and "mypy":
   - "patchbay has none yet" (suppressions) is replaced by the rule this tree followed: a
     suppression only where the code cannot change, either because the issue requires the
     behaviour (BLE001) or because a third party's signature is overridden whole (PLR0913), each
     with its reason beside it.
   - A `# type: ignore` names its code, as a `noqa` does (PGH003 under `ALL`).
   - In a test, one holds a refusal that strict's `warn_unused_ignores` keeps honest.

   Verified against `src/patchbay/events.py`, `models.py` and the tests that carry one.
   Proposed, not applied; filed as fromtheoutfit/patchbay-standards#21.

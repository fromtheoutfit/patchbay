# Contracts revision after the review of PR 11

## Context

The owner reviewed PR 11 at head `6f4e7a8` (issue comment of 2026-11-07, fromtheoutfit/patchbay#11) and found 17 issues in the contracts spec (`agent-os/specs/2026-11-07-0806-contracts-models-events-errors-fake/`):

- six that break the contract (1–6);
- six smaller correctness gaps (7–12);
- five design and maintainability issues (13–17).

The probes run while shaping reproduced 1, 2, 3, 5, 6, 8 and 9. They also found three more gaps of the same kind:

- **P1:** `RenderRequest(sample_rate=10**400)` makes `render()` raise `OverflowError`.
- **P2:** `Pattern(bars=10**400)` does the same, and so does `RenderResult(sample_rate=10**400).audio_seconds`.
- **P3:** `ParameterChanged.id` accepts `""`.

This spec fixes all 20 in a new spec folder on the same branch, so PR 11 carries the fix. The PR 3, 4 and 9 revisions set that precedent. The agent does not stage, commit or push.

## Shaping answers (owner, 2026-11-07)

- **Scope:** all 17 findings plus P1–P3, in a new folder `agent-os/specs/2026-11-07-<HHMM>-contracts-revision-after-pr-11-review/`. `<HHMM>` is taken at Task 1.
- **Visuals:** none. **References:** the review comment, the PR 9 revision's plan, and the contracts spec's `shape.md` and `verification/probes.txt`. **Product:** unchanged.
- **Standards:** the core `base/python/toolchain`, plus `process/ownership`, `process/standards-retrospective`, `process/verification-gate` and `process/standards-sync`, snapshotted at `11ceffd`.
- **5, JSON-shaped data:** a new classmethod on `PatchbayModel` validates such data under pydantic's JSON rules. `model_validate` stays exactly as strict as now.
- **1, render bound:** both choices below were the owner's.
  - A shared, exact sample count. The fake refuses a render past its declared limit with `RenderFailedError`.
  - A new contract test requires every adapter to raise `RenderFailedError` for a render no instrument could produce.
- **9, `Event.at`:** only a zone whose offset is zero at every instant is accepted. The time is stored as `datetime.UTC`. A naive time, or `Europe/London` in any month, is refused.
- **2 and 10, the bus:** `subscribe()` returns a `Subscription` handle, which has `cancel()` and works as a context manager. A bad `event_type`, or a subscriber that cannot be called, raises a new `SubscriptionRejectedError(reason)`.
- **11 and 12, error fields:**
  - `PatchbayValidationError.errors` is renamed `.details` and `SubscriberFailedError.errors` is renamed `.exceptions`. There is no `errors()` method.
  - `pydantic-core` is declared in `[project] dependencies`.
- **13, the `model_validate*` overrides:** wrap pydantic's three methods without restating their signatures.
- **16, the audio copy:** fix the fake and keep `RenderResult`'s copy, so the read-only guarantee stays absolute.
- **17, the contract test names:** drop the `test_` prefix.

## Task 1: Save spec documentation

- **`plan.md`:** this plan, with its dispositions table.
- **`shape.md`:**
  - The first Decision: the review is the scope, answered in a new folder.
  - The answers above. The "No unsubscribe" Decision from the contracts spec is reversed by the owner's review.
  - The Decisions this plan makes: the name `from_json_data`, `MAX_SAMPLES` and `MAX_SAMPLE_RATE`, and the timing of `cancel()`.
  - The `pydantic-core` dependency Decision: what it does, why the standard library cannot, its license.
- **`standards.md`:** the five standards verbatim, at `11ceffd`.
- **`references.md`.**
- **The contracts spec's `shape.md`:** one pointer line naming this revision.

## Task 2: Probes, before any source edit (`verification/probes.txt`)

The scripts live in the session scratchpad and run as `uv run --locked python` and `uv run --locked mypy` from the repository root. Each script's source is shown before its output, as in the contracts spec's `probes.txt`.

1. **The findings, reproduced at `6f4e7a8`:**
   - 1, P1, P2: `render()` raises at tempo `1e-300`, tail `1e308`, rate `10**400` and bars `10**400`. The `1e-6` tempo case is shown as its sample count (about 1.15e13), not allocated.
   - 2: after `subscribe("parameter.changed", fn)`, `publish` raises `TypeError`, and `FakeInstrument.set` has already stored the value.
   - 3: a `TypeAdapter`, and a plain `BaseModel` with a `Quantity` field, raise pydantic's `ValidationError`.
   - 4: a fake that loads values one at a time passes all eleven contract tests.
   - 5: the JSON-shaped dict is refused by strict validation, and is accepted through JSON text.
   - 6: at `2**53`, `max + 1.0 == max`; at `float max`, `nextafter` gives `inf`.
   - 7: NaN audio is accepted, and `r == r` is `False`.
   - 8 and P3: `""` is accepted as a `Patch.values` key and as `ParameterChanged.id`.
   - 9: `Europe/London` is accepted in January and refused in July.
   - The probes run while shaping already show most of these.
2. **The design's footing:**
   - mypy strict reads pydantic's `Self`-typed signatures through an `if not TYPE_CHECKING:` wrap, and catches a misspelled keyword. No unreachable warning is raised (checked while shaping).
   - At runtime the wrap keeps a nested model's JSON round trip and every refusal. `inspect.signature` of each wrapped method equals pydantic's.
   - `round(Fraction)` is exact, returns an `int` and rounds half to even.
   - `utcoffset(None)` is zero for `UTC`, `timezone.utc`, `ZoneInfo("UTC")` and pydantic's `TzInfo(0)`, and `None` for `Europe/London`.
   - `Annotated[ParameterId, Field(min_length=1)]` works as a `Mapping` key.
   - `json.dumps` then `model_validate_json`, under strict, admits enum values, base64 and arrays, and still refuses `"0.5"` and `1` for `True`.

If a probe contradicts the design, stop and bring it to the owner.

## Task 3: `errors.py` (11, 12, the error for 2)

- `PatchbayValidationError(details)` keeps its details as `.details`, and `__str__` reads from it.
- `SubscriberFailedError(event_name, exceptions)` keeps the exceptions as `.exceptions`.
- New `SubscriptionRejectedError(reason)`, whose message is `subscription rejected: {reason}`. It follows the shape of `PatchRejectedError`.
- `pyproject.toml` `[project] dependencies` gains `"pydantic-core>=2.50.4,<3"`, with a comment: the `ErrorDetails` type that `errors.py` imports.
  - Run `uv lock`. Only patchbay-core's `requires-dist` changes, recorded in `verification/uv-lock-diff.txt`.
  - `[project]` is the package's section, so no gate file changes.
- Gate green.

## Task 4: `models.py` (3, 5, 7, 8, 13, 14, 1, P1, P2)

- **13:**
  - Add a `_refusing[**P, R]` decorator that runs the call inside `_refusals()`, using `functools.wraps`.
  - Inside `PatchbayModel`, under `if not TYPE_CHECKING:`, set `model_validate`, `model_validate_json` and `model_validate_strings` each to `classmethod(_refusing(BaseModel.<name>.__func__))`.
  - A comment says why: mypy reads pydantic's own signatures, and every keyword pydantic adds passes through.
  - The three `# noqa: PLR0913` and the `ExtraValues` import go. `__init__` (with its marker), `__setattr__` and `__delattr__` are unchanged.
- **5:** `PatchbayModel.from_json_data(data: object) -> Self` validates data shaped as `json.loads`, YAML or TOML give it, under pydantic's JSON rules.
  - It runs `model_validate_json(json.dumps(data))`.
  - A value JSON cannot hold, from json's `TypeError` or `ValueError`, raises `PatchbayValidationError` with one detail at the root, chained from json's error.
- **3:** narrow the promise in the module docstring and `errors.py`'s.
  - A patchbay model's own entry points raise `PatchbayValidationError`: the constructor, the three `model_validate*`, `from_json_data`, assignment and deletion.
  - Validation pydantic runs for something else (a `TypeAdapter`, a plain `BaseModel` holding a patchbay field) raises pydantic's `ValidationError`.
  - A model derived from `PatchbayModel` gets the promise.
- **7:** `RenderResult` refuses audio that is not finite: `np.isfinite(audio).all()`, checked before the copy.
- **8:** `Patch.values: Mapping[Annotated[ParameterId, Field(min_length=1)], Quantity]`.
- **14, 1:** `RenderRequest.samples(pattern) -> int` is `round((Fraction(bars × beats_per_bar × 60) / Fraction(tempo_bpm) + Fraction(tail_seconds)) × sample_rate)`. It is exact and never overflows for any valid pair.
- **P2:** `audio_seconds` becomes `self.audio.shape[1] / self.sample_rate`. Dividing an int by an int gives no `OverflowError` at any rate.
- Gate green.

## Task 5: `events.py` (2, 9, 10, P3)

- **9:**
  - `_in_utc` refuses unless `at.tzinfo` is set and `at.tzinfo.utcoffset(None) == timedelta(0)`, and returns `at.astimezone(UTC)`.
  - Every event's `at.tzinfo is UTC`, including after a JSON round trip.
- **2, 10:**
  - A public `Subscription` holds the event type and the subscriber.
  - `cancel()` removes it, a second call does nothing, and it takes effect from the next event: `publish` delivers over a snapshot, the same as a subscribe during a publish.
  - `__enter__` returns the handle, and `__exit__` cancels.
  - Both `subscribe` overloads return `Subscription`. A subscription is refused with `SubscriptionRejectedError` unless `event_type` is `None` or a subclass of `Event`, and the subscriber is callable.
- **P3:** `ParameterChanged.id` gets `Field(min_length=1)`.
- The module docstring is updated. `__init__.py` re-exports `Subscription` and `SubscriptionRejectedError` and lists them in `__all__`.
- Gate green.

## Task 6: `contracts.py`

`Instrument.render`'s docstring says:

- the result is `request.samples(pattern)` samples long;
- `RenderFailedError` is raised when the instrument cannot render that many, and nothing is published.

The module docstring stays in step.

## Task 7: `testing/fake.py` (1, 15, 16)

- `__init__` and `load_patch` read the parameters through `self.parameters()`, so a test's subclass can widen them (used for 6).
- **1:**
  - New public `MAX_SAMPLES = 2**24` (about 5.8 minutes at 48 kHz) and `MAX_SAMPLE_RATE = 768_000`. They sit beside `PARAMETERS`.
  - `render` refuses past either with `RenderFailedError`, before allocating anything and without publishing.
  - Within both limits every float the voice computes is finite.
- **14:** the length is `request.samples(pattern)`, and `_SECONDS_PER_MINUTE` goes.
- **16:**
  - The voice mixes straight into one `(1, total)` float32 array, and clips it in place.
  - The full-size buffers become two: the mix, and `RenderResult`'s copy.
- **15:**
  - `_refusal` and `_fault` give way to one check of the whole patch, raising `PatchRejectedError(str(error)) from error`.
  - The cause is the `ParameterNotFoundError` from `_parameter()`, or the error from `Parameter.check`. A wrong instrument gives a plain `PatchRejectedError`.
- Gate green.

## Task 8: `testing/contract_tests.py` (4, 6, 17, 1)

- **17:**
  - Every function loses `test_`, e.g. `get_after_set_returns_what_was_set`, and so does each `test = "…"` string.
  - The module docstring's form becomes `<property>(instrument, bus)`. The parametrize example is unchanged.
- **6:**
  - `_out_of_range` uses `math.nextafter(maximum, inf)` and `math.nextafter(minimum, -inf)`, each kept only when finite, and for a ratio only when within `[0, 1]`.
  - It keeps `minimum + 0.5` for a choice or a boolean.
- **4:** new `a_patch_refused_part_way_changes_nothing`.
  - Each patch names the instrument correctly, sets every earlier parameter to another value, and puts the bad entry last in sorted key order.
  - The bad entries:
    - the last parameter in a wrong unit;
    - the last parameter at each of its out-of-range values;
    - an id that sorts after every parameter id.
  - Each must raise `PatchRejectedError`, leave the instrument unchanged and publish nothing.
- **1:** new `an_impossible_render_raises_render_failed`.
  - The input is `Pattern(tempo_bpm=sys.float_info.min, bars=1, beats_per_bar=1, notes=())` at 48 kHz, about 1.3e315 samples.
  - It must raise `RenderFailedError` and publish nothing.
- `render_returns_the_declared_shape_and_sample_rate` expects `_REQUEST.samples(_PATTERN)`.
- `CONTRACT_TESTS` holds thirteen. Gate green.

## Task 9: Tests (one module per source module, as now)

- **`test_errors.py`:** the renamed fields, and `SubscriptionRejectedError` in `_ERRORS` (its message, its fields, rebuilt from `args`).
- **`test_models.py`:**
  - 5: `from_json_data`:
    - a hypothesis property: `Patch.from_json_data(json.loads(p.model_dump_json())) == p` for any opaque bytes;
    - a `Pattern` built from JSON data with a list of notes;
    - it still refuses `"0.5"`, and `True` for an int;
    - a `set` is refused, chained from `TypeError`;
    - `model_validate` of the same dict is still refused.
  - 3: a `TypeAdapter` raises pydantic's error, and a `PatchbayModel` subclass raises patchbay's.
  - 13: each wrapped method's signature equals `BaseModel`'s, and a pydantic keyword passes through (`strict=False`).
  - 7: NaN and inf audio are refused.
  - 8: an `""` key is refused.
  - 14, 1, P1, P2: `samples` agrees with the float formula on ordinary inputs and returns an int for every extreme case. `audio_seconds` at rate `10**400` is `0.0`.
- **`test_events.py`:**
  - 9: London is refused in January and in July. `timezone.utc`, `ZoneInfo("UTC")` and JSON `Z` are accepted, each stored as `UTC`.
  - 2: a str or non-Event type, and a non-callable subscriber, are refused, and delivery goes on.
  - 10: `cancel` stops delivery from the next event and is harmless twice. `with` cancels on exit. A cancel during a publish takes effect from the next event. One of two subscriptions of the same subscriber can be cancelled alone.
  - P3: an empty `id` is refused.
- **`test_fake.py`:**
  - 1: every extreme case raises `RenderFailedError` with no event: tempo `1e-300` and `1e-6`, tail `1e308`, rate `10**400` and `768_001`, bars `10**400`.
  - 15: each rejection's `__cause__`, with the message equal to the cause's.
  - A clip still warns with the float32 mix.
- **`tests/unit/testing/test_contract_tests.py`:**
  - The broken fakes for the new tests: `_LoadsUntilARefusal`, which checks the name and then calls `set` per value, caught by "the instrument unchanged"; and `_RendersAnyLength`, which returns one silent sample instead of raising, caught by "RenderFailedError to be raised".
  - 6: a `_WideRange` fake with a parameter up to `2.0**53` and one over `[-float max, float max]` passes every contract test.
- **`test_package.py`:** the new names in `__all__`.

## Task 10: Docs

- **`README.md`:**
  - The layout lines for `models.py` (the JSON-data entry point), `events.py` (subscriptions) and `testing/` (thirteen contract tests, unprefixed).
  - Install mentions `pydantic-core`.
- **`agent-os/product/tech-stack.md`:** read against the change.
- **`CHANGELOG.md`:**
  - A `### Changed` entry under `[Unreleased]` for this revision.
  - The seventh spec's bullets that now read false ("eleven", the entry-point list, `.errors`) rewritten to the tree.
- **Every changed file's module docstring and header**, read against its code.
- **PR 11's body:** rewritten to the shipped tree, with no attribution. Drafted in the spec folder, and applied with `gh pr edit 11 --body-file` only once the owner approves the text.

## Task N (FINAL): Verification gate

1. **`scripts/gate.sh`, steps 1–6:** green.
2. **Docs (7):** as Task 10. Also `base/python/toolchain.md` re-read against the tree: the PLR0913 suppressions are gone, and `pydantic-core` is declared.
3. **Version (8):** the `[Unreleased]` entry. The version stays 0.0.1 (owner: 0.1.0 when patchbay-vital passes the contract tests).
4. **Standards retrospective (9)**, from the shipped diff against `6f4e7a8`:
   - No project standard exists, and `index.yml` is unchanged.
   - Revise the proposals in fromtheoutfit/patchbay-standards#21 that this diff proves stale:
     - 1, `models.md`: the narrowed entry-point list, `from_json_data`, "wrap, don't restate", finite audio, non-empty keys.
     - 2, `errors.md`: no field named like a third party's method; a module imported directly is a declared dependency.
     - 3, `events.md`: UTC judged by the zone; subscribe validates and returns a cancellable `Subscription`.
     - 4, `testing.md`: unprefixed contract functions; bounds probed by `nextafter`; the part-way and impossible-render properties.
     - 7, `toolchain.md` Dependencies: a dependency imported directly is declared even when another dependency brings it in.
     - 8, suppressions: PLR0913 is gone, and the rule about overriding a third party's signature whole is replaced by wrapping without restating.
   - Present each to the owner with AskUserQuestion, multi-select, at most three to a question, each question ending with "None of these".
   - Edit #21's body in place with a "Revised 2026-11-07 after fromtheoutfit/patchbay#11's review" paragraph, as the PR 9 revision did with #20, with no attribution. Ask the owner whether they want a new issue instead.
   - Mark each declined proposal `declined by owner, <date>`, and record `Proposals sent upstream:`.

**Last act:** run `scripts/gate.sh` into `verification/gate-run.txt` (date and branch first, `exit=0` last), then print `git status --short`. Report the retrospective's edits separately from the feature's. No stage, commit or push.

## Dispositions

The owner's review of PR 11 (2026-11-07, at `6f4e7a8`), plus the probe finds.

| # | Finding | Disposition |
| --- | --- | --- |
| 1 | extreme valid inputs make `render` raise built-ins or exhaust memory | exact `RenderRequest.samples`; the fake refuses past `MAX_SAMPLES` / `MAX_SAMPLE_RATE` with `RenderFailedError`; new contract test `an_impossible_render_raises_render_failed` |
| 2 | a bad `event_type` breaks every publish | `subscribe` refuses it, or a non-callable, with `SubscriptionRejectedError` |
| 3 | `PatchbayValidationError` misses `TypeAdapter` and foreign models | promise narrowed in the docs to a patchbay model's own entry points; tests pin both sides (no wrap point covers every path without losing error paths) |
| 4 | no contract test for a partly applied patch | new `a_patch_refused_part_way_changes_nothing`, proven by `_LoadsUntilARefusal` |
| 5 | strict refuses the JSON-shaped dict | `PatchbayModel.from_json_data`, pydantic's JSON rules; `model_validate` unchanged |
| 6 | `_out_of_range` at `2**53` and float max | `math.nextafter`, non-finite skipped; `_WideRange` regression |
| 7 | NaN or inf audio accepted | `RenderResult` refuses non-finite audio |
| 8 | `""` accepted as a `Patch.values` key | `min_length=1` on the key |
| 9 | `_in_utc` reads the instant's offset | zone offset zero at every instant; stored as `UTC` |
| 10 | no unsubscribe | `subscribe` returns a `Subscription` (`cancel()`, context manager) |
| 11 | `.errors` shadows pydantic's `errors()`; same name, two types | `.details` and `.exceptions` |
| 12 | `pydantic_core` imported, not declared | `pydantic-core>=2.50.4,<3` in `[project]` |
| 13 | the overrides copy pydantic's signatures | wrapped under `if not TYPE_CHECKING:`, not restated; three PLR0913 gone |
| 14 | the sample count written three ways | one `RenderRequest.samples(pattern)` |
| 15 | `_refusal` copies a message; no `from` | one whole-patch check raising `from` the cause |
| 16 | three full-size buffers in the fake's render | float32 mix in place; the copy kept |
| 17 | `test_*` contract functions collected twice | prefix dropped |
| P1 | `sample_rate=10**400` overflows `render` | refused by the fake (`MAX_SAMPLE_RATE`, `MAX_SAMPLES`) |
| P2 | `bars=10**400` overflows `render`; huge rate overflows `audio_seconds` | exact `samples`; int ÷ int `audio_seconds` |
| P3 | `""` accepted as `ParameterChanged.id` | `min_length=1` |

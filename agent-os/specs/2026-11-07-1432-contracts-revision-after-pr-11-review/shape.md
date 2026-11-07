# Contracts revision after the review of PR 11 — Shaping Notes

Shaped 2026-11-07 in plan mode with this repository's customized `/agent-os:shape-spec`. The
owner answered the Step 1–5 questions and eight design questions, one for each finding that had
more than one sound answer. Most findings had more than one; only finding 3 had none that worked
(see Decisions).

## Core Architecture (Non-Negotiable)

- `base/python/toolchain` — included without asking (Step 5a); its full text in `standards.md`.
  It applies to every file this spec changes.

## Scope

The owner's review of PR 11 at `6f4e7a8` (issue comment of 2026-11-07 on fromtheoutfit/patchbay#11)
gives 17 findings against the contracts spec
(`agent-os/specs/2026-11-07-0806-contracts-models-events-errors-fake/`):

- six that break the contract (1–6);
- six smaller correctness gaps (7–12);
- five design and maintainability issues (13–17).

The probes run at shaping found three more of the same kind:

- **P1:** `RenderRequest(sample_rate=10**400)` makes `FakeInstrument.render` raise `OverflowError`.
- **P2:** `Pattern(bars=10**400)` does the same, and so does
  `RenderResult(sample_rate=10**400).audio_seconds`.
- **P3:** `ParameterChanged.id` accepts `""`.

All 20 are fixed here, in a new spec folder on the same branch, so PR 11 carries the fix. The
PR 3, 4 and 9 revisions set that precedent. The agent does not stage, commit or push.
`plan.md`'s dispositions table answers each finding.

## Shaping answers (owner, 2026-11-07)

- **Step 1, scope:** all 17 findings plus P1–P3, in a new folder.
- **Step 2, visuals:** none.
- **Step 3, references:** the review comment, the PR 9 revision's plan, and the contracts spec's
  `shape.md` and `verification/probes.txt` (`references.md`).
- **Step 4, product context:** unchanged.
- **Step 5, standards:** `base/python/toolchain` (core); `process/ownership`,
  `process/standards-retrospective`, `process/verification-gate`, `process/standards-sync`.
  Snapshot at `11ceffd`, the pin unchanged.
- **Finding 5, JSON-shaped data:** a new entry point on `PatchbayModel` validates JSON-shaped data
  under pydantic's JSON rules. `model_validate` stays exactly as strict as now.
- **Finding 1, the render bound:** a shared, exact sample count, and a limit the fake declares,
  past which it raises `RenderFailedError`. A new contract test requires every adapter to raise
  `RenderFailedError`, and publish nothing, for a render no instrument could produce.
- **Finding 9, `Event.at`:** UTC zones only. A time is accepted when its zone's offset is zero at
  every instant, and is stored as `datetime.UTC`. A naive time, or `Europe/London` in any month,
  is refused.
- **Findings 2 and 10, the bus:** `subscribe()` returns a `Subscription` handle, with `cancel()`,
  usable as a context manager. A bad `event_type`, or a subscriber that cannot be called, raises
  a new `SubscriptionRejectedError(reason)` at subscribe time.
- **Findings 11 and 12, the error fields:** rename only. `PatchbayValidationError.errors` becomes
  `.details` and `SubscriberFailedError.errors` becomes `.exceptions`, with no `errors()` method.
  `pydantic-core` is declared in `[project] dependencies`.
- **Finding 13, the `model_validate*` overrides:** wrap pydantic's three methods without
  restating their signatures.
- **Finding 16, the audio copy:** fix the fake and keep `RenderResult`'s copy, so the read-only
  guarantee the owner chose in the contracts spec stays absolute. Revisit when patchbay-vital
  measures long renders.
- **Finding 17, the contract test names:** drop the `test_` prefix.

## Decisions

- **The review is the scope** (fromtheoutfit/patchbay#11), answered in a new folder on the same
  branch. The contracts spec's `shape.md` gets one pointer line naming this revision; its text is
  otherwise the record of what was decided then.

### Against the contracts spec's Decisions (each the owner's, from the review)

- **Unsubscribe exists.** The contracts spec deferred it ("No unsubscribe"). Finding 10 brings it
  in as `Subscription`.
- **The validation promise is narrowed** (finding 3). A patchbay model's own entry points raise
  `PatchbayValidationError`: the constructor, `model_validate`, `model_validate_json`,
  `model_validate_strings`, `from_json_data`, assignment and deletion. Validation pydantic runs on
  behalf of something else raises pydantic's `ValidationError`: a `TypeAdapter`, or a plain
  `BaseModel` that holds a patchbay field. A model derived from `PatchbayModel` gets the promise.
  The review offered two answers, and the other one does not work. Moving the wrapping "to a
  point every path goes through" would mean raising a non-`ValueError` from inside a validator.
  pydantic-core lets such an exception through unwrapped, so it would abort the outer model's
  validation at the first nested refusal, drop the outer location from the error, and leave the
  outer model's own refusals as `ValidationError` anyway. Tests hold both sides of the narrowed
  boundary.
- **`Event.at` is refused by its zone, not by its instant's offset** (finding 9). The contracts
  spec's rule, refuse a naive or non-UTC time, stands. Only the check changes:
  `at.tzinfo.utcoffset(None) == timedelta(0)`, which a fixed-offset zone answers and a
  zone with daylight saving cannot (`None`). The accepted time is normalized with
  `astimezone(UTC)`, so `at.tzinfo is UTC` for every event, including one read back from JSON,
  whose zone pydantic parses as its own `TzInfo(0)`.
- **The error fields are renamed** (finding 11): `PatchbayValidationError(details)` keeps
  `.details`, and `SubscriberFailedError(event_name, exceptions)` keeps `.exceptions`, the name
  `ExceptionGroup` uses. Neither field shadows a third party's method of another type.
- **The contract tests lose their `test_` prefix** (finding 17), so pytest never collects one an
  adapter imports by name. Issue #10 asked for plain functions taking an `Instrument` and an
  `EventBus`, not for the prefix. The `test` field of `ContractViolationError` keeps its name and
  holds the new names.
- **`RenderResult` keeps its copy** (finding 16). The fake mixes straight into one float32 array
  and clips it in place, and takes its peak without an `abs` copy, so a render holds two buffers
  its full length, its mix and the result's copy, where it held three: a float64 mix, its float32
  cast and the copy. Each note's own temporaries, as long as the note, are as before.

### What this revision decides that the answers leave open

- **The JSON-data entry point is `PatchbayModel.from_json_data(data)`** (finding 5). It runs
  `model_validate_json(json.dumps(data))`, so the data meets pydantic's JSON rules exactly: an
  enum by its value, bytes as base64 (`Patch`'s `val_json_bytes`), a time as an ISO string, an
  array for a tuple. Strict still refuses `"0.5"` for a float and `1` for `True`. A value JSON
  cannot hold, such as a set or a `datetime`, makes `json.dumps` raise `TypeError`, and a
  circular reference makes it raise `ValueError`. Either is refused as `PatchbayValidationError`,
  with one detail at the root, chained from json's error. The name avoids pydantic's `model_`
  namespace, where a later pydantic method could land.
- **`RenderRequest.samples(pattern) -> int`** is the one sample count (findings 1, 14, P1, P2):
  `round((bars × beats_per_bar × 60 / tempo_bpm + tail_seconds) × sample_rate)`, computed in
  exact rational arithmetic (`fractions.Fraction`), so it never overflows and never gives `inf`
  for any valid pattern and request. The fake, the contract test and `Instrument.render`'s
  docstring all name it. It rounds half to even, as `round` does.
- **`RenderRequest.sample_at(pattern, beat) -> int`** joins `samples`, found while building: the
  fake places each note's start and end in samples, and with only `samples` shared it would have
  kept its own minute constant and float formula for that, the duplication finding 14 names.
  `sample_at` is `round(beat × 60 / tempo_bpm × sample_rate)`, exact like `samples`, and the beat
  at the pattern's end with no tail is `samples` exactly (a test holds it). An adapter that
  schedules notes needs the same rule.
- **The fake's limits are `MAX_SAMPLES = 2**24` and `MAX_SAMPLE_RATE = 768_000`**, public in
  `testing/fake.py` beside `PARAMETERS`. 2**24 samples is about 5.8 minutes at 48 kHz, and
  768 kHz is the highest standard PCM rate. `render` checks both before allocating anything, and
  refuses with `RenderFailedError`, publishing nothing. The rate limit is needed beside the
  sample limit: at a tempo near `float max`, a rate far beyond any float passes the sample limit
  with a handful of samples, and then overflows in the voice's per-note arithmetic. Within both
  limits every float the voice computes is finite.
- **`Subscription.cancel()` takes effect from the next event.** `publish` delivers over a
  snapshot taken when it starts, so a cancel during a publish works like a subscribe during a
  publish. A second `cancel()` does nothing. `with bus.subscribe(...) as subscription:` cancels
  on exit. Each `subscribe` is its own subscription, so the same subscriber subscribed twice has
  two, cancelled one at a time.
- **`SubscriptionRejectedError(reason)`** takes the shape of `PatchRejectedError`: a reason in its
  args, and the message `subscription rejected: <reason>`. `subscribe` refuses an `event_type`
  that is neither `None` nor a subclass of `Event` (a str such as `"parameter.changed"` among
  them), and a subscriber that is not callable.
- **The overrides are wrapped, not restated** (finding 13). Inside `PatchbayModel`, under
  `if not TYPE_CHECKING:`, `model_validate`, `model_validate_json` and `model_validate_strings`
  are each `classmethod(_refusing(BaseModel.<name>.__func__))`. `_refusing[**P, R]` is a
  `functools.wraps` decorator that runs the call inside `_refusals()`. mypy reads pydantic's own
  `Self`-typed signatures, a misspelled keyword is still a type error, and any keyword a later
  pydantic adds passes through at runtime. The three `# noqa: PLR0913` go. Checked at shaping:
  mypy strict raises no unreachable warning for the block, and an assertion of the returned type
  holds (`verification/probes.txt`).
- **`RenderResult` refuses audio that is not finite** (finding 7), and **every parameter id is
  non-empty** (finding 8, P3): the key of `Patch.values`
  (`Annotated[ParameterId, Field(min_length=1)]`) and `ParameterChanged.id`, as `Parameter.id`
  already was.
- **`audio_seconds` divides an int by an int** (P2): `self.audio.shape[1] / self.sample_rate`.
  Python rounds that division correctly and raises no `OverflowError` at any rate.
- **The fake checks the whole patch once, raising from the cause** (finding 15). One check
  replaces `_refusal` and `_fault`, and raises `PatchRejectedError(str(error)) from error`. The
  cause is the `ParameterNotFoundError` that `_parameter()` raises, or the error from
  `Parameter.check`. A patch for another instrument has no cause and is refused plainly.
- **The fake reads its parameters through `parameters()`** in `__init__` and `load_patch`, so a
  test's subclass that widens them gets an instrument that agrees with itself. The finding 6
  regression test uses this.
- **The part-way contract test** (finding 4), `a_patch_refused_part_way_changes_nothing`. Each
  patch names the instrument correctly, sets every parameter that sorts before the bad entry to
  another value, and puts the bad entry last, since a `Patch` sorts its keys and an adapter that
  loads one value at a time loads them in that order. The bad entries:
  - the last parameter in a wrong unit;
  - the last parameter at each of its out-of-range values;
  - an id that sorts after every parameter id.

  Each must raise `PatchRejectedError`, leave the instrument unchanged and publish nothing.
- **The impossible-render contract test**, `an_impossible_render_raises_render_failed`, renders
  `Pattern(tempo_bpm=sys.float_info.min, bars=1, beats_per_bar=1, notes=())` at 48 kHz, about
  1.3e315 samples. No instrument can render that, so the test requires `RenderFailedError` and no
  event. There are now thirteen contract tests.
- **Out-of-range values sit one float past each bound** (finding 6), from `math.nextafter`. A
  bound with no finite float beyond it, `float max` or its negative, gets no candidate there. For
  a ratio, only a candidate within `[0, 1]` is kept. `minimum + 0.5` stays for a choice or a
  boolean. The probe corrects one detail of the review: at `float max`, `maximum + 1.0` rounds to
  `maximum` as it does at 2**53, so the old code failed a correct instrument there too, with "no
  exception". It is `nextafter`, the fix, that gives `inf`, which `Quantity` refuses; hence the
  skip. `verification/mutations.txt` puts the old arithmetic back and shows the regression test
  fail twice.
- **A contract test's docstring is imperative, "Check that …"**, found while building: without
  the `test_` prefix, ruff's D401 holds the functions to the imperative mood it waives for tests.
  All thirteen take the same form.

### Dependency: `pydantic-core` (finding 12)

- **`pydantic-core>=2.50.4,<3`** joins `[project] dependencies`, a range like its neighbours: the
  locked version as the floor, the next major as the ceiling.
- **What it does:** `errors.py` imports `ErrorDetails`, pydantic-core's type of one refusal,
  which `PatchbayValidationError.details` carries. pydantic does not re-export it (probed:
  `hasattr(pydantic, "ErrorDetails")` is `False`).
- **Why the standard library cannot:** the type is pydantic-core's own description of its errors.
  A copy written here would drift from the errors it describes.
- **License:** MIT. It is already locked, at 2.50.4, as pydantic 2.14.3's dependency, so the lock
  gains only patchbay-core's own `requires-dist` entry (`verification/uv-lock-diff.txt`).

## Deferred

Unchanged from the contracts spec except for unsubscribe, which now exists:

- From the issue: the host, the CLI, discovering adapters, transports, async and persisting
  events.
- From that spec's shaping: JSON for `RenderResult`, mapping a host's normalized values, and the
  pydantic mypy plugin.
- From this one:
  - `RenderResult` taking ownership of a locked array without a copy (finding 16's other answer),
    until an adapter measures the cost;
  - an `errors()` method like pydantic's (finding 11's other answer).

## Context

- **Visuals:** none.
- **References:** `references.md`.
- **Product alignment:** N/A. Nothing synth-specific is added, and `mission.md` and
  `tech-stack.md` keep their decisions.

## Standards Applied

**Core (always applied):**

- `base/python/toolchain` — Step 5a. Every file changed is formatted, linted, typed and tested
  under it. Its Dependencies section asks for the `pydantic-core` Decision above, and its ruff
  section's coded-suppression rule is what finding 13 removes three suppressions under.

**Feature-specific:**

- `base/process/ownership` — no stage, commit, push or pull request. The PR body and the upstream
  issue carry no attribution, and each is changed only after the owner approves the text.
- `base/process/standards-retrospective` — the eight proposals in patchbay-standards#21 are
  checked against this diff and revised where it proves them stale.
- `base/process/verification-gate` — not the gate's spec: no gate file changes. `[project]` is the
  package's section of `pyproject.toml`.
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
build step, in dependency order: errors (192 tests), models (223), events (242), the fake (250,
with `contracts.py`'s docstrings), the contract tests (268), and `sample_at`'s tests with the
docs (270). No gate file changed, so no negative test was rerun.

The other verification files:

- `verification/probes.txt`: every finding reproduced at `6f4e7a8`, and the pydantic, mypy and
  Python behaviour the design rests on.
- `verification/mutations.txt`: finding 6's regression test failing twice with the old bound
  arithmetic put back.
- `verification/uv-lock-diff.txt`: the lock gaining only patchbay-core's own entry for
  pydantic-core.

**Docs (step 7):**

- **`README.md`:** the Layout lines now describe the new surfaces: `models.py` (`from_json_data`,
  `RenderRequest.samples`), `events.py` (`Subscription`) and `testing/` (thirteen contract tests,
  unprefixed). The runtime dependencies are three, and Install names pydantic-core. The gate and
  sync sections are unchanged and still read true.
- **`CHANGELOG.md`:** the eighth spec's entry under `### Changed`. The seventh spec's bullet that
  said "eleven contract tests" now points to this revision for their names and number. Its other
  bullets still read true: the entry points it lists are a model's own.
- **`agent-os/product/tech-stack.md`:** read against the change and unchanged. Its pydantic line
  (frozen, strict models on one base) and numpy line still read true, and it lists no
  dependencies by name for pydantic-core to join. `mission.md` is unchanged and reads true.
- **Headers and docstrings:** every changed module's docstring was read against its code, and two
  were corrected in the reading:
  - `contracts.py` and `fake.py` now say a call the instrument *refuses* publishes nothing, since
    a subscriber's failure is raised after a call is carried out;
  - the probe pointers in `models.py` and `events.py` name which spec's `probes.txt` they mean.

  `testing/__init__.py`, `recording.py` and `tests/unit/testing/conftest.py` are unchanged and
  read true. `pyproject.toml`'s comment over `dependencies` names this spec for pydantic-core and
  states the rule it followed.
- **`CLAUDE.md` and `shape-spec.md`:** they say nothing about the package's contents; unchanged.
- **`base/python/toolchain.md` against this tree:** it still reads false where #21's proposals 7
  and 8 say (`dependencies` is not empty, and the tree has coded suppressions). Revisions R7 and
  R8 bring those proposals up to date. Its sentence that patchbay "lists neither" ISC001 nor
  PLR2004 still reads true: this revision tripped PLR2004 and fixed it in the code.
- **The contracts spec's `shape.md`:** one pointer line naming this revision.
- **PR 11's body:** rewritten to the revised tree, naming both specs, with no attribution. The
  owner approved the text, and it was applied with `gh pr edit 11 --body-file` on 2026-11-07,
  before the revision is committed. It was read back identical but for the final newline `gh`
  drops.
- **Line widths:** no prose line this spec wrote is over 100 columns. The transcripts in
  `verification/` hold scripts and their output as they ran.

**Version (step 8):** the eighth spec's entry under `[Unreleased]`, `### Changed`, in
`CHANGELOG.md`. The version stays 0.0.1 (the owner): 0.1.0 when patchbay-vital passes the contract
tests.

## Standards Retrospective

Step 9, always last, from the shipped diff against `6f4e7a8`.

1. *A pattern no standard covers?* Yes, in every module the review touched. No standard holds any
   of it yet: the six new base standards are still proposals in fromtheoutfit/patchbay-standards#21,
   filed from this branch's first round. This revision proves four of those proposals and both
   `toolchain.md` corrections stale, so its proposals are revisions of #21's (below), not new
   standards. No project standard exists to take any of them, and each belongs to every patchbay
   package.
2. *A standard wrong or stale?* `base/python/toolchain.md`, the synced text, still reads false
   where #21's proposals 7 and 8 already say: `dependencies` is not empty, and the tree has coded
   suppressions. Proposals 7 and 8 themselves are now stale: patchbay declares three runtime
   dependencies, and the PLR0913 case they name is gone. Revisions R7 and R8, below.
3. *A deliberate deviation?* None from a standard. The diff is the review's dispositions, each
   an owner's answer or a Decision above.
4. *A moved pointer?* None. `toolchain.md`'s pointers into this repository
   (`tests/unit/test_package.py`, `pyproject.toml`'s sections) still resolve, and #21's
   verification pointers name files that still exist. The probes it cites moved by nothing; this
   revision's probes are in its own `verification/`.

No project standard exists to edit, and `agent-os/standards/index.yml` is untouched. The
retrospective's own change set is this section; it edited no file outside this spec folder.

### Standards retrospective (proposed, base)

Revisions of the open fromtheoutfit/patchbay-standards#21, each verified against this revision's
shipped files and tests, and against its `verification/probes.txt` and `mutations.txt` where a
rule rests on how pydantic or mypy behave. #21's proposals 5 (`typing.md`) and 6 (`layout.md`)
stand as filed.

- **R1, #21 proposal 1, `base/python/models.md`:**
  - The validation promise covers a model's own entry points. These are the constructor, the
    three `model_validate*`, the JSON-data entry point, assignment and deletion.
  - Validation pydantic runs for something else raises pydantic's error: a `TypeAdapter`, or a
    plain `BaseModel` holding the model.
  - Data in JSON's form goes through one entry point that applies pydantic's JSON rules
    (`from_json_data`). Python input stays strict.
  - pydantic's validating classmethods are wrapped under `if not TYPE_CHECKING:`, never restated
    with copied signatures. mypy then reads pydantic's own signatures, and every keyword passes
    through.
  - An array holds only finite values, and an id is non-empty wherever it appears, as a mapping
    key too.
  - A count every implementation must agree on is one method on the model, in exact arithmetic
    (`RenderRequest.samples`, `sample_at`).
  - Verified against `src/patchbay/models.py`, `tests/unit/test_models.py`
    (`test_validation_run_for_something_else_raises_pydantic_s_error`,
    `test_the_validating_classmethods_keep_pydantic_s_signatures`,
    `test_a_patch_comes_back_from_its_json_data`, `test_samples_is_an_int_however_long_the_render`)
    and probes `footing.py` A, B, E and `footing_typing.py`.
- **R2, #21 proposal 2, `base/python/errors.md`:** no error's field takes the name of a third
  party's method of another type. A validation error's refusals are `.details`, where pydantic's
  `errors` is a method, and a failure carrying exceptions holds them as `.exceptions`, the name
  `ExceptionGroup` uses. Verified against `src/patchbay/errors.py` and `tests/unit/test_errors.py`
  (`test_no_field_is_named_like_pydantic_s_errors_method`) and probe `findings.py` 11.
- **R3, #21 proposal 3, `base/python/events.md`:**
  - An event's time is judged by its zone, not its instant. It is accepted only in a zone at
    offset zero at every instant (`utcoffset(None) == 0`), and held as `datetime.UTC`.
  - `subscribe` refuses a type that is not an event, or a subscriber that cannot be called, with
    the package's error, where the subscription is made.
  - `subscribe` returns a `Subscription`:
    - `cancel()` ends it from the next event, as a subscribe takes effect;
    - a second `cancel()` does nothing;
    - it is a context manager;
    - the bus drops a cancelled subscriber.
  - Verified against `src/patchbay/events.py`, `tests/unit/test_events.py` (the London cases,
    `test_a_bad_subscription_is_refused_where_it_is_made`,
    `test_a_cancel_during_a_publish_takes_effect_from_the_next_event`,
    `test_a_cancelled_subscriber_is_no_longer_held_by_the_bus`) and probes `findings.py` 2 and 9,
    `footing.py` C.
- **R4, #21 proposal 4, `base/python/testing.md`:**
  - Contract tests are plain functions `<property>(instrument, bus)` with no `test_` prefix, so
    pytest never collects one an adapter imports. Each docstring is an imperative "Check that …",
    as D401 asks once the prefix goes.
  - A bound is probed one float past it (`math.nextafter`), and a bound with no finite float
    beyond it gets no candidate. A reference fake widened to the largest bounds passes every
    contract test.
  - The suite holds a patch refused part way (its bad entry last in key order) and a render no
    instrument could produce.
  - Verified against `src/patchbay/testing/contract_tests.py`,
    `tests/unit/testing/test_contract_tests.py` (`_LoadsUntilARefusal`, `_RendersAnyLength`,
    `test_a_correct_instrument_with_the_widest_bounds_passes`,
    `test_the_contract_tests_are_never_collected_by_pytest`) and `verification/mutations.txt`.
- **R7, #21 proposal 7, `base/python/toolchain.md` "Dependencies":** a package the code imports
  directly is declared in `[project] dependencies` as a range, even when another dependency brings
  it in (`pydantic-core>=2.50.4,<3`). The example names patchbay's three. Verified against
  `pyproject.toml`, `src/patchbay/errors.py` and `verification/uv-lock-diff.txt`.
- **R8, #21 proposal 8, `base/python/toolchain.md` "ruff" and "mypy":**
  - The case "a third party's signature overridden whole (PLR0913)" is withdrawn: such a method
    is wrapped, not restated (R1).
  - `src/` keeps four suppressions: BLE001 on the bus's catch, and three coded `type: ignore`s,
    on the base-init marker and the two `__hash__ = None`.
  - PLR2004 and D401, which this revision's tree tripped, were fixed in the code, as the rule
    says.
  - Verified against `src/patchbay/models.py`, `src/patchbay/events.py` and the gate run.

Presented to the owner on 2026-11-07 with AskUserQuestion, multi-select, in two questions (R1–R3,
then R4, R7 and R8), each ending with "None of these", beside a third asking how they go
upstream. All six were approved. The owner chose to edit #21 in place, as the PR 9 revision did
with #20, rather than file a second issue for one pull request's work. #21's body gains a
"Revised 2026-11-07 after fromtheoutfit/patchbay#11's review" paragraph, and proposals 1, 2, 3,
4, 7 and 8 are rewritten so it reads true on its own, each marked *(Revised.)* with its new
verification pointers. Its "Depends on" names the revision's commit, once pushed. Proposals 5
and 6 are unchanged. No AI attribution. Read back from GitHub after the edit, identical but for
the final newline `gh` drops (2026-11-07T19:53:23Z).

Each: proposed, not applied; approved by the owner on 2026-11-07 and written into
fromtheoutfit/patchbay-standards#21 in place.

Proposals sent upstream: fromtheoutfit/patchbay-standards#21

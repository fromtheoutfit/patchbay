# Instrument.get returns the value the parameter holds nearest the one given — Shaping Notes

Shaped 2026-11-11 in plan mode with this repository's customized `/agent-os:shape-spec`. The owner
answered the Step 1–5 questions and three wording questions, adding two changes to the wording
before it was written.

## Core Architecture (Non-Negotiable)

- `base/python/toolchain`, `base/python/layout`, `base/python/typing`, `base/python/models` and
  `base/python/errors` — included without asking (Step 5a); their full text in `standards.md`.

## Scope

Issue #18, "Instrument.get returns the nearest value the parameter holds: say so in the protocol":
a documentation change to the protocol, verified against the contract tests it describes. An
instrument of finite resolution cannot give back an arbitrary float it was set to; the contract
tests already rely only on what holds exactly, setting every parameter at a bound. No tolerance
field, no change to a contract test, no gate file. CHANGELOG entry, gate green,
`verification/gate-run.txt`. The version stays 0.0.1. No stage, commit, push or PR by an agent.

## Shaping answers

- **Step 1, scope:** issue #18 as is: the docstrings of `Instrument.get` and `Instrument.set`, the
  secondary docstrings chosen below and a CHANGELOG entry, in a new spec folder on the issue's
  branch.
- **Step 2, visuals:** none.
- **Step 3, references:** `references.md`, patchbay-vital among them, read-only.
- **Step 4, product context:** aligned, no change. `agent-os/product/mission.md`: "a script written
  against one instrument reads the same against the next", which is what the wording gives a
  caller; and "core grows only when a second adapter needs the same thing", which this does not
  touch, adding no field and no test.
- **Step 5, standards:** the core five, and `testing/tests`, `process/verification-gate`,
  `process/standards-retrospective`, `process/ownership` and `python/events`. Snapshot at `e31f7db`
  in `standards.md`.

## Decisions

1. **The scope is issue #18** (`gh issue view 18`), whose "Proposed wording" is the starting point
   and whose rules are kept: documentation only, verified against the contract tests it describes,
   no tolerance field, no change to a contract test, no gate file, the version 0.0.1. Every
   departure from the issue's text below is the owner's.
2. **`Instrument.get`, three departures from the issue's sentence.**
   - The colon becomes a sentence break: `select = ["ALL"]` holds D205 and D400, a summary line of
     its own ending in a period.
   - "the nearest value the parameter holds to the one given" becomes "the value the parameter holds
     nearest the one given, **as the instrument measures it**". The stricter claim, nearest in the
     `Quantity`'s unit, was not made, because no evidence in the issue supports it: patchbay-vital's
     probe 4 shows bounds recovered (P0), every held value exact (P1, P1', P3, P4) and no arbitrary
     display value exact (P2), and nothing measures nearness. patchbay-vital inverts the display
     curve and rounds to float32 on the normalized scale, affine to the preset's
     (`NormalizedScale.to_normalized`, `round_to_float32`), so on a curved parameter the held value
     whose display is nearest may be the other neighbour.
   - "; at a tie, either of the two" is added. On a parameter that takes whole numbers on a
     continuous range, 3.5 has two nearest values; patchbay-vital's indexed scales round a half away
     from zero (`_round_half_away`), and their grid lands on halves (`parameters.py:65-67`).
3. **`Instrument.set`** takes the issue's phrase, "The instrument may hold the nearest value it can
   to the one given (see `get`)", its nearness `get`'s; and says which value `ParameterChanged`
   carries as `new`: the value the parameter holds after the set, the one `get` returns. That
   agrees with `ParameterChanged`'s "the value it has now" (`events.py:93`), with
   `set_emits_parameter_changed_once` (`new` equal to the bound given) and with the fake, which
   publishes the value it stores.
4. **`contracts.py`'s module docstring gains no sentence.** It says what holds across the methods
   (failures, refusals, events); what `set` takes and `get` gives back are theirs to say, and
   `patch()`'s "which `load_patch` takes back unchanged" already covers held values through a patch.
5. **`contract_tests.py`'s module docstring: its reason for the bounds, alone.** "so an instrument
   that stores what it is given gets back exactly what it was given" read true but gave the reason
   from before #18; it becomes "which every instrument holds exactly, whatever its resolution
   (`Instrument.get`)", the promise `get` now makes at a bound. **No contract test's body, name or
   order changed**: `verification/contract-tests-diff.txt` is one hunk, inside the module
   docstring. `base/testing/tests.md`'s same reason goes to the retrospective as a base proposal,
   not an edit here.
6. **`fake.py`'s module docstring gains one sentence**: it holds every value a parameter takes, so
   `get` returns exactly what `set` was given, the exact case of `get`'s wording.
7. **Left as they read, each true after the change:** `README.md` (lines 13-14 and 24-26 name the
   protocol and the thirteen tests and say nothing of what `get` returns);
   `get_after_set_returns_what_was_set`'s docstring, a contract test, true of the value it gives, a
   bound; `FakeInstrument.get` ("Return the parameter's value") and `.set` ("store it");
   `ParameterChanged`; `load_patch` and `patch()`.
8. **What the suite holds, from the code** (and `verification/probes.txt`, probe a, from a run):
   - `_other_value` returns a bound, always:
     `bound = parameter.maximum if current.value != parameter.maximum else parameter.minimum`.
   - `get_after_set_returns_what_was_set` sets every parameter at `_other_value` and requires
     `got == value`; `set_emits_parameter_changed_once` sets `parameters()[0]` at `_other_value`
     and requires the event's `(id, old, new)` to be `(parameter.id, old, new)`, `new` the bound.
     These two hold the bound clause.
   - `patch_round_trips_through_load_patch` sets `parameters()[0]` at a bound, loads the earlier
     `patch()` back and requires `after == patch`: held values come back unchanged, through a
     patch, not `get` and `set`.
   - Every other value is refused: a wrong unit (`Quantity(value=0.0, unit=wrong)`), an unknown id
     (`parameter.default`), `_out_of_range` (the next float past each bound, and `minimum + 0.5` for
     a choice or a boolean alone), and the refused patches.
   - So no contract test sets a value between a continuous parameter's bounds or sets a value `get`
     returned: "at any value `get` has returned" and nearness are promises the suite does not hold,
     the first evidenced by patchbay-vital's probe 4.
9. **The wording holds for a parameter that takes whole numbers on a continuous range**
   (`verification/probes.txt`, probe b, a fake with such a parameter passing all thirteen contract
   tests). Its bounds are whole and held, so `get` gives each back exactly and
   `get_after_set_returns_what_was_set` passes; a bound it did not hold would fail that test, so the
   wording and the test agree. 3.4 is taken (`Parameter.check`, `models.py:205`: a continuous value
   need not be whole) and held as 3; 3.5 is held as either neighbour, the tie clause; a value `get`
   returned comes back as itself. The suite gives no continuous parameter a half, so nothing in it
   changes.

## Context

- **Visuals:** None.
- **References:** `references.md`.
- **Product alignment:** `mission.md`, as Step 4 says; no change to `agent-os/product/`.

## Standards Applied

**Core (always applied):**
- `base/python/toolchain`, `base/python/layout`, `base/python/typing`, `base/python/models`,
  `base/python/errors` — Step 5a

**Feature-specific:**
- `testing/tests` — "The contract suite": values set at a parameter's bounds, the reason this spec
  changes in `contract_tests.py` and proposes upstream
- `process/verification-gate` — the gate, its transcript
- `process/standards-retrospective` — gate step 9 and the route of a base proposal
- `process/ownership` — no stage, commit, push or PR by an agent
- `python/events` — `ParameterChanged`'s `new`, checked as reading true

## Verification Gate

Spec is not complete until `scripts/gate.sh` passes — `bash -n` on every shell script under
`scripts/` as git lists them, with no tracked file a step reads that a `.gitignore` ignores;
`uv sync --locked`, then `uv run --locked ruff format --check .`, `uv run --locked ruff check .`,
`uv run --locked mypy` and `uv run --locked pytest` under `pyproject.toml`'s `[tool.*]` rule set and
`uv.lock`'s pins; and `scripts/sync-standards.sh --check` against `../patchbay-standards` at the
commit in `agent-os/standards/base/.version` — and the three judgment steps are recorded, in this
order: Docs, Version, then the standards retrospective below.

**Results (2026-11-11):** exit 0 on branch
`feature/18-instrumentget-returns-the-nearest-value-the-parameter-holds-say-so-in-the-protocol`,
`verification/gate-run.txt`, run after the last change to a file a gate step reads; 276 tests
passed, the thirteen contract tests among them, unchanged. No gate file changed, so no negative test
was rerun. `verification/contract-tests-diff.txt`: one hunk in `contract_tests.py`, lines 19-20 of
its module docstring. `verification/probes.txt`: probe a, every value the thirteen contract tests
give the fake, each accepted `set` at a bound (0 elsewhere) and none of a value `get` returned;
probe b, a fake with a whole-number continuous parameter passing all thirteen, 3.4 held as 3.0, 3.5
and 2.5 as 4.0 and 3.0, a bound and `set(get())` as themselves, and each `ParameterChanged.new` the
value `get` then returns.

**Docs (step 7):** checked and reads true after the change:
- `src/patchbay/contracts.py`: the module docstring, unchanged (Decision 4), and `get` and `set`;
- `src/patchbay/testing/contract_tests.py`: the module docstring; `get_after_set_returns_what_was_set`'s
  docstring, true of the bound it gives;
- `src/patchbay/testing/fake.py`: the module docstring, and `get`, `set` and `load_patch`, which
  store the value given;
- `src/patchbay/events.py:93`, `ParameterChanged`: "the value it has now", which `set` now names;
- `README.md` (lines 13-14 and 24-26) and `CLAUDE.md`: nothing on what `get` returns;
- the standards that name the three files: `base/python/errors.md`, `layout.md`, `models.md`,
  `toolchain.md` and `typing.md` cite them for what this change leaves alone;
  `base/testing/tests.md`'s "The contract suite" gives the reason for the bounds this change
  corrects in `contract_tests.py`, so it reads true and stale, the retrospective's proposal below.

**Version (step 8):** the eleventh spec's entry at the top of `### Changed` in `[Unreleased]`,
`CHANGELOG.md`. The version stays 0.0.1.

## Standards Retrospective

Step 9, always last. Answered from the shipped diff; there are no project standards in this
repository, so nothing is edited here, `index.yml` is unchanged, and the one change is a base
proposal.

1. **A pattern no standard covers:** none beyond question 2's. The pattern this spec writes down,
   that the suite sets only values every instrument holds exactly, is "The contract suite"'s
   already; only its reason was stale.
2. **A standard wrong or stale:** `base/testing/tests.md`, "The contract suite", fourth bullet:
   "Values are set at a parameter's bounds, so an instrument that stores what it is given gets back
   exactly that" gives the reason from before #18, as `contract_tests.py`'s module docstring did.
   Below.
3. **A deliberate deviation:** none.
4. **A pointer moved:** none. `_other_value`, `_out_of_range`, the thirteen contract tests and
   `test_contract` are where the standards say.

- **Checked, no proposal:** `base/python/events.md` names `ParameterChanged` only for its name
  (line 26) and for `subscribe`'s overloads (line 98), and has no sentence on what `new` carries;
  "the value it has now" is `src/patchbay/events.py:93`, not the standard's, and it reads true
  against `set`'s new docstring, "The event's `new` is the value the parameter holds after the set,
  the one `get` returns" (`src/patchbay/contracts.py:59-60`). Recorded in the issue below, at the
  owner's asking.

Proposals sent upstream: fromtheoutfit/patchbay-standards#37

### Standards retrospective (proposed, base)

- `base/testing/tests.md`, "The contract suite", fourth bullet — "Values are set at a parameter's
  bounds, so an instrument that stores what it is given gets back exactly that" becomes "Values are
  set at a parameter's bounds, which every instrument holds exactly whatever its resolution, as the
  protocol's `get` promises, so no contract test sets a value between a continuous parameter's
  bounds or relies on an arbitrary value coming back as itself"; the rest of the bullet stays.
  Verified against `src/patchbay/contracts.py` (`Instrument.get`),
  `src/patchbay/testing/contract_tests.py` (its module docstring, `_other_value`, `_out_of_range`),
  `tests/unit/testing/test_contract_tests.py` (`test_contract`,
  `test_each_contract_test_catches_its_broken_fake[get_after_set_returns_what_was_set]`) and this
  spec's `verification/probes.txt`, probes a and b. Proposed, not applied; filed as
  fromtheoutfit/patchbay-standards#37.

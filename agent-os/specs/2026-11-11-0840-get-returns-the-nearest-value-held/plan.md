# Issue #18: `Instrument.get` returns the value the parameter holds nearest the one given

## Context

`Instrument.get` says only that it returns "the parameter's value". An instrument with finite
resolution, such as Vital, which holds every value as a float32 and converts its display through
curves, cannot give back an arbitrary float it was set to. It gives back a value it holds. The
contract tests already rely only on what holds exactly: they set every parameter at a bound.
Issue #18 asks for the protocol to say this, so a caller does not expect an arbitrary value back
from `get` after `set`. No tolerance field and no change to a contract test. This is a
documentation change to the protocol, checked against the contract tests it describes. It has a
CHANGELOG entry, the version stays 0.0.1, the gate must be green, and an agent makes no stage,
commit, push or PR.

Shaped in plan mode. The owner answered Steps 1–5 and the wording questions. This is the eleventh
spec, on branch
`feature/18-instrumentget-returns-the-nearest-value-the-parameter-holds-say-so-in-the-protocol`.

## Decisions (the owner's)

1. **Scope is issue #18** (`gh issue view 18`): the `get` and `set` docstrings in
   `src/patchbay/contracts.py`, plus the two secondary docstrings below and a CHANGELOG entry. No
   tolerance field, no contract test's body, name or order, no gate file. Version 0.0.1.
2. **`get` changes from the issue's text in three ways:**
   - The issue's colon becomes a sentence break, because `select = ["ALL"]` brings in D205 and
     D400.
   - "The nearest value the parameter holds to the one given" becomes "the value the parameter
     holds nearest the one given, as the instrument measures it". The stricter claim, nearest in
     the `Quantity`'s unit, is not made because nothing in the issue's evidence supports it.
     Probe 4 P2 shows only that arbitrary display values don't come back exactly. patchbay-vital
     inverts the display curve, then rounds to float32 on its normalized scale, which is affine
     to its preset scale (`NormalizedScale.to_normalized`, `round_to_float32`). On a curved
     parameter, the held value whose display is nearest may therefore be the other neighbour.
   - "; at a tie, either of the two" is added. On a whole-number continuous parameter, 3.5 has
     two nearest values. patchbay-vital's indexed scales (`_round_half_away`) do land on halves
     (`parameters.py:65-67`).
3. **`set`:** the issue's phrase, plus which value `ParameterChanged` carries as `new`: the value
   held after the set, the one `get` returns. This agrees with `events.py:93`'s "the value it has
   now", and with the fake, which publishes `new=value`, the value it stores.
4. **`contracts.py` module docstring:** no sentence added.
5. **`contract_tests.py` module docstring, lines 19–21:** only the reason for setting values at
   the bounds changes, and it cites `Instrument.get`. No contract test's body, name or order
   changes; `verification/contract-tests-diff.txt` shows this. The same reason given in
   `base/testing/tests.md` goes to the retrospective as a base proposal, not as an edit here.
6. **`fake.py` module docstring:** one sentence, saying the fake holds every value exactly.
7. **Left as they read, all still true:**
   - `README.md:13-14, 24-26`
   - `get_after_set_returns_what_was_set`'s docstring (a contract test)
   - `FakeInstrument.get` and `.set`
   - `ParameterChanged`
   - `load_patch` and `patch()` (`patch()`'s "which `load_patch` takes back unchanged" is the
     patch analogue of "at any value `get` has returned")
8. **What the suite holds and what the protocol only promises,** from the code:
   - Held by the suite: the bound clause, by `get_after_set_returns_what_was_set` (every
     parameter at `_other_value`, a bound, `got == value`) and by
     `set_emits_parameter_changed_once` (`new` equals the bound given).
   - Not held by any contract test: "at any value `get` has returned" (Vital's probe 4 P1, P1',
     P3 and P4 support it) and nearness.
   - The patch analogue is held by `patch_round_trips_through_load_patch`.
   - The other values the suite gives are refused: wrong unit, unknown id, `_out_of_range`, and
     the refused patches.
9. **A parameter that takes whole numbers on a continuous range:** the wording holds.
   - Its bounds are whole and held, so they come back exactly and `get_after_set` passes. A bound
     that isn't held fails that test, so the wording and the test agree.
   - 3.4 is accepted by `Parameter.check` (`models.py:205`) and held as 3.
   - 3.5 is held as 3 or 4: the tie clause.
   - The suite never gives a continuous parameter a half (`minimum + 0.5` is used for choice and
     boolean only).

## Task 1: Save spec documentation

Create `agent-os/specs/2026-11-11-HHMM-get-returns-the-nearest-value-held/`, with HHMM taken from
the clock at creation:

- **plan.md:** this plan.
- **shape.md:**
  - Core Architecture
  - Scope
  - Shaping answers: Step 1 (scope: issue #18 as is), Step 2 (visuals: none), Step 3
    (references: as below), Step 4 (product: aligned with `mission.md`'s "reads the same against
    the next" and "core grows only when a second adapter needs the same thing"; no field added),
    Step 5 (the core five plus `testing/tests`, `process/verification-gate`,
    `process/standards-retrospective`, `process/ownership` and `python/events`, snapshot at
    `e31f7db`)
  - Decisions 1–9 above. The first cites issue #18; the second records why the stricter claim was
    not made.
  - Context
  - Standards Applied
  - Verification Gate and Standards Retrospective, filled in at the end
- **standards.md:** the full text of `base/python/{toolchain,layout,typing,models,errors}`,
  `base/testing/tests`, `base/process/{verification-gate,standards-retrospective,ownership}` and
  `base/python/events`, as they read at `e31f7db`.
- **references.md:**
  - `src/patchbay/testing/contract_tests.py`: `_other_value`,
    `get_after_set_returns_what_was_set`, `set_emits_parameter_changed_once`,
    `patch_round_trips_through_load_patch`, `_out_of_range`
  - `src/patchbay/models.py`: `Parameter.check` (takes vs holds)
  - `src/patchbay/events.py`: `ParameterChanged`
  - `../patchbay-vital`, read-only, on the issue's branch: `src/patchbay_vital/parameters.py`
    (`_round_half_away`, `NormalizedScale`, `to_preset`) and `src/patchbay_vital/census.py:22-24`
    (an indexed scale mapped as continuous)
  - Probe 4 in the patchbay-vital host spec's `verification/probes.txt`
- No `visuals/`.

## Task 2: `src/patchbay/contracts.py`: `get` and `set` docstrings, exactly

```python
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
```

The module docstring is unchanged.

## Task 3: `src/patchbay/testing/contract_tests.py`: the module docstring's rationale only

Lines 18–21 become:

```
Each test works out what it expects from the instrument's parameters and the contract alone,
never from an implementation's code. Values are set at a parameter's bounds, which every
instrument holds exactly, whatever its resolution (`Instrument.get`), and refused one float past
them, so a check with any slack is caught.
```

Then `git diff src/patchbay/testing/contract_tests.py > <spec>/verification/contract-tests-diff.txt`.
The one hunk lies inside the module docstring.

## Task 4: `src/patchbay/testing/fake.py`: the module docstring, one sentence

Line 7 becomes two lines:

```
stored, reported and patched like any other, and change nothing in the sound. It holds every
value a parameter takes, so `get` returns exactly what `set` was given.
```

## Task 5: Probes, written to `verification/probes.txt` with each script's text and output

The scripts live in the scratchpad and run as `uv run --locked python <scratchpad>/<probe>.py` from
the repository root. Nothing is added to `tests/`.

- **a. Every value the contract tests give:** a `FakeInstrument` subclass that records each
  `set` and `load_patch` call. All 13 `CONTRACT_TESTS` run against it, and the probe prints, per
  test, each parameter and value, whether it was accepted or refused, and whether an accepted value
  is a bound. Expected: every accepted `set` is at a bound, and no test sets a value `get` returned
  or a value strictly between a continuous parameter's bounds.
- **b. Whole numbers on a continuous range:** a `FakeInstrument` subclass with an extra
  `voices` parameter (continuous, `Unit.none`, 1 to 16). Its `set` runs `Parameter.check` first,
  then rounds half away from zero. Expected: all 13 `CONTRACT_TESTS` pass; `set` 3.4 gives `get`
  3.0, 3.5 gives 4.0, 16 gives 16.0, and `set(get())` comes back unchanged.

## Task 6: `CHANGELOG.md`

Add an entry at the top of `[Unreleased]` → `### Changed`:

- **The spec:** "Eleventh spec, `agent-os/specs/…/` (issue #18): `Instrument.get` says what it
  returns after `set`…".
- **The three files:**
  - `contracts.py`: `get` and `set`
  - `contract_tests.py`: the module docstring's rationale; no contract test's body, name or order
    changed
  - `fake.py`: one sentence
- **The close:** documentation only, no field, contract test or gate file; the version stays
  0.0.1.

## Task 7 (final): Verification gate

1–6. `scripts/gate.sh` must exit 0. Its output goes to `verification/gate-run.txt`, headed
`Gate run 2026-11-11 on branch feature/18-…` and then `$ scripts/gate.sh`. Any failure is fixed
at its cause and the gate rerun. No gate file changes, so no negative tests are rerun.

7. **Docs:** check that these read true, and record the check in `shape.md`:
   - `README.md`
   - `CLAUDE.md`
   - the module docstrings of the three files changed
   - `events.py:93`
   - `base/testing/tests.md`, which names `contract_tests.py`
8. **Version:** the `[Unreleased]` entry; 0.0.1, no bump.
9. **Standards retrospective,** from the shipped diff:
   - There are no project standards, so nothing is edited and `index.yml` is unchanged.
   - Expected base proposal: `base/testing/tests.md`, "The contract suite", 4th bullet. The reason
     for using bounds becomes "a bound is a value every instrument holds exactly whatever its
     resolution, as the protocol's `get` promises". It is checked against `contracts.py`
     (`Instrument.get`), `contract_tests.py` (its module docstring and `_other_value`),
     `test_contract[get_after_set_returns_what_was_set]` and probe b.
   - Each proposal goes under `### Standards retrospective (proposed, base)`.
   - **Present-and-file:** present each proposal with a multi-select AskUserQuestion, with a "None
     of these" option. File the approved ones as one issue with
     `gh issue create --repo fromtheoutfit/patchbay-standards`, with no AI attribution, and write
     its number beside each. Mark each declined one `declined by owner, 2026-11-11`. Record the
     `Proposals sent upstream:` line.

Then print `git status --short` and stop. No stage, commit, push or PR.

## Verification

- The gate is green: `verification/gate-run.txt`, exit 0, with the date and branch.
- `verification/contract-tests-diff.txt`: one hunk, inside the module docstring.
- `verification/probes.txt` a and b, as expected above.
- `git status --short` shows only these files:
  - modified: `src/patchbay/contracts.py`, `src/patchbay/testing/contract_tests.py`,
    `src/patchbay/testing/fake.py`, `CHANGELOG.md`
  - new: the spec folder

# Revision of issue #18's spec after the first review of PR 19

## Context

The owner reviewed PR 19 at `6506e1d` (the comment of 2026-11-11 14:06 UTC) and found 21 problems.
The main one is that `Instrument.get`'s "nearest" promise is not met by patchbay-vital, the
instrument the issue's evidence comes from. I reproduced the patchbay-vital claims read-only at
`84b5ae7`:

- **`beats_per_minute`, a linear parameter:** given 216.85141355537831, it holds 216.8514347
  (2.1e-5 away), while 216.8514061 (7.5e-6 away) is also held.
- **Linear parameters in general:** 8,236 of 140,800 sampled values (5.8%) are held at a value
  other than the nearest. The cause is two roundings, `DisplayCurve.to_preset` then
  `NormalizedScale.to_normalized`.
- **Out of bounds:** `flanger_dry_wet`'s shipped preset 0.7072 displays as 141.44 against its
  bounds of [0, 100].
- **Volume's floor, powers of two as normalized values:** none of the 107 changes in display, but
  91 of 107 move the stored value.
- **Volume's floor, powers of two as stored presets:** at 2^-43 and 2^-45, `set(get())` gives back
  a display value one double ulp away.

This revision answers all 21 findings in a new spec folder on the same branch, so PR 19 carries
it. The reviewed folder (`2026-11-11-0840-…`) stays as its record. It changes docstrings, one
test module, the CHANGELOG, issue #18 and fromtheoutfit/patchbay-standards#37. It does not
change a gate file, or any contract test's body, name or order. The version stays 0.0.1. An agent
makes no stage, commit, push or PR.

## Decisions for shape.md (the owner's answers, 2026-11-11)

1. **Scope:** all 21 findings, in a new folder, `agent-os/specs/2026-11-11-0935-get-revision-after-pr-19-review/`.
   Each patchbay-vital claim is reproduced at `84b5ae7` and each core one at `6506e1d`, in
   `verification/probes.txt`. Visuals: none. Product: aligned with `mission.md`, no change.
   Standards: the core five, plus `testing/tests`, `process/verification-gate`,
   `process/standards-retrospective`, `process/ownership` and `python/events`.
   - Nothing in `models.md` is changed or newly relied on, so finding 20 is not noted under it in
     `standards.md`.
2. **Findings 1 and 6: neither "nearest" nor "next to the given" is claimed.**
   - `get` promises a value the parameter holds, which is the value given itself at a bound and at
     any value `get` has returned for it that `set` takes.
   - **What claiming either would need:**
     - For "next to the given": every sampled value, on every curve, landing on one of the two
       held values either side of the one given, held by a test. The probe's 165,600 of 165,600
       is a sample, not a test.
     - For "nearest": the same, but landing on the nearer of the two. 5.8% of sampled values on
       linear parameters do not.
   - The tie clause goes with "nearest". That settles findings 14 and 19 for the wording; the
     record is still corrected.
3. **Findings 2 and 7:** the clause is limited to values "that `set` takes", and `get` promises
   nothing about its range.
   - **A note for patchbay-vital #8, not a change here:** `Instrument.patch` promises a state
     "which `load_patch` takes back unchanged". If `get` returns a value outside the bounds, that
     value lands in `patch().values`, and a `load_patch` that checks each value with
     `Parameter.check` would refuse the instrument's own patch. Such an adapter must either keep
     out-of-range values out of `values` (carried in `opaque`) or accept them on load. The limited
     clause in `get` leaves that choice to the adapter.
4. **Findings 3, 5 and 8: probe b becomes a unit test.**
   - It sits in `tests/unit/testing/test_contract_tests.py`, beside `_WideRange`, under the
     standard's "A correct implementation at the edges passes every contract test". The
     whole-number fake lives in the test module and is not shipped in `patchbay.testing`.
   - Three more tests: a value between two whole numbers is held as a value other than the one
     given; `set(get())` at that interior value comes back exactly; `ParameterChanged.new` is the
     value held. No tie result is asserted.
   - The `new` test is the first anywhere to tell the value held from the value given.
5. **Finding 2, the floor:** no sentence in the protocol. The patchbay-vital draft states the
   consequence for #8: with the loaded `VitalPreset` as the source of truth, `set(get())` at
   volume's floor would change the stored value, and so `patch()`, though `get` is unchanged.
   Through the normalized path, at the stored presets 2^-43 and 2^-45, `get` would not even come
   back unchanged. #8 decides whether `VitalInstrument.set` keeps the stored value when the
   display value given is the one it already shows.
6. **Wording.**
   - Finding 9: the `contracts.py` module docstring, with the owner's clause.
   - Findings 4, 11 and 16: the `contract_tests.py` docstrings.
   - Finding 20: one sentence in `Parameter`'s docstring.
7. **Outward edits.**
   - **Issue #18:** retitled to "Instrument.get returns a value the parameter holds: say so in the
     protocol", with a "Revised 2026-11-11" paragraph added and the proposed wording kept as it was
     proposed.
   - **fromtheoutfit/patchbay-standards#37:** revised in place with a "Revised 2026-11-11"
     paragraph, its numbers kept, because its text says "nearest". This happens after the owner
     approves the retrospective's proposals.
   - **The patchbay-vital issue** (the three notes above): presented, not filed.
8. **This morning's texts, re-checked without "nearest":**
   - `fake.py`'s sentence still reads true and is unchanged.
   - The `contract_tests.py` module docstring is reworded anyway.
   - #37 says "nearest", so it is revised.
9. **Corrections to the reviewed record (findings 12, 13, 17, 19, 21) are made in the new folder.**
   - Decision 3 claimed agreement with a test that cannot tell held from given.
   - Decision 8 left `new` out.
   - `set`'s "to the one given" was a departure from the issue that was never recorded.
   - The tie evidence was grid halves, which never reach `set`.
   - `references.md` had the wrong line range for `to_preset` and omitted
     `DisplayCurve.to_preset`.

## Dispositions

| # | Finding | Answer |
|---|---|---|
| 1 | "as the instrument measures it" doesn't qualify "nearest"; linear parameters miss too | Decision 2; probes V1–V3 |
| 2 | The floor isn't shown; out-of-bounds presets; `set(get())` moves the stored value | `test_a_value_the_parameter_holds_comes_back_exactly` cited; probes V4–V5; Decisions 3 and 5 |
| 3 | The `new` test only sets a bound | Decision 4: the `new` test |
| 4 | The `contract_tests.py` docstring reads as observed, not promised; the CHANGELOG repeats it | "which `Instrument.get` promises…"; the CHANGELOG follows |
| 5 | Probe b only in `verification/`; it pins a tie rule | Decision 4 |
| 6 | "nearest" not met (`beats_per_minute`) | Decision 2 |
| 7 | `get` can return a value out of range | Decision 3 |
| 8 | Probe b's `set(get())` runs only at a bound | Decision 4: `set(get())` after 3.4; probe C2 shows the old probe couldn't tell |
| 9 | The module docstring overclaims | Reworded |
| 10 | The retrospective missed `tests.md`'s "The suite holds the protocol's promises" | Proposal; #37 revised |
| 11 | The `get_after_set…` docstring makes the withdrawn promise | "set at a bound" |
| 12 | Decision 3 claimed more than the suite shows; Decision 8 left out `new` | Decision 9 |
| 13 | "to the one given" not recorded | Decision 9; `set`'s sentence rewritten |
| 14 | "the two" has no referent | Moot: the tie clause goes |
| 15 | No "for it" | Added |
| 16 | "refused one float past them" is ambiguous | Its own sentence |
| 17 | Bare filenames in `probes.txt` | Absolute paths |
| 18 | Probe a's check never fires | Positive control, C1 |
| 19 | The tie evidence is wrong | Decision 9 |
| 20 | `Parameter` doesn't say bounds are held exactly | One sentence; Docs checks `models.py` |
| 21 | Wrong reference line range; `DisplayCurve.to_preset` missing | A new `references.md` |

## Task 1: Save spec documentation

In the new folder:

- **`plan.md`:** this plan.
- **`shape.md`:** the shaping answers; Decisions 1–9; this table summarized; the patchbay-vital
  draft under "For patchbay-vital #8 (drafted, not filed)".
- **`standards.md`:** the full text of the 10 standards at `e31f7db`, built as before.
- **`references.md`:**
  - the PR 15 revision spec
  - `_WideRange` and `test_a_correct_instrument_with_the_widest_bounds_passes`
  - patchbay-vital at `84b5ae7`: `DisplayCurve.to_preset` (`parameters.py:169-171`),
    `MappedParameter.to_preset` (234-250), `NormalizedScale.to_normalized` (105-111),
    `host.py:361-377` (`get` and `set` through `raw_value`), and in `tests/unit/test_parameters.py`
    `test_a_value_the_parameter_holds_comes_back_exactly` and
    `test_where_volume_s_offset_absorbs_a_preset`
  - the patchbay-vital host spec's probe 4 and its Decision 6
  - the comment on fromtheoutfit/patchbay-vital#8

## Task 2: Probes, before any fix (`verification/probes.txt`)

The scripts live in the scratchpad, and every `$` line gives the absolute path.

- **patchbay-vital cases** run as
  `PYTHONDONTWRITEBYTECODE=1 ../patchbay-vital/.venv/bin/python -B <script>`, so nothing in
  patchbay-vital is written:
  - **V1:** `beats_per_minute`, with the three float32 normalized neighbours and the preset after
    each rounding, which shows the double rounding.
  - **V2:** linear parameters, 400 values each (seed 1): 8,236 of 140,800.
  - **V3:** adjacency over every curve (seed 2), 165,600 of 165,600, labelled as a sample.
  - **V4:** `flanger_dry_wet`'s 0.7072 displays as 141.44 against [0, 100].
  - **V5:** volume's floor, both readings. As normalized values: 0 display misses, 91 of 107
    moved. As stored presets: 2^-43 and 2^-45 miss.
- **Core cases** run as `uv run --locked python <script>`, against a worktree-free
  `git show 6506e1d:` copy where the case is about the old record:
  - **C1:** probe a with a positive control. A sequence that sets a value `get` returned must fire
    the check.
  - **C2:** the old probe b's final line, run against a fake that holds bounds exactly but moves an
    interior held value. It prints the same line.

## Task 3: `src/patchbay/contracts.py`

Lines 3–6 of the module docstring become:

```
An adapter's instrument implements `Instrument` structurally; it inherits nothing from here. mypy
holds an implementation to the signatures, and the contract tests in `patchbay.testing` hold it
to the behaviour each names in its docstring; none sets a parameter away from its bounds, so what
`get` returns there rests on `get`'s and `set`'s own words and on no contract test.
`isinstance(x, Instrument)` asks only whether `x` has every member, since that is all a
runtime-checkable protocol can ask; `issubclass` is refused, `name` being a data member.
```

`get` and `set` become:

```python
        """Return the parameter's value, the one it holds.

        After `set`, that is a value the parameter holds, not necessarily the one given: the value
        given itself at a bound, and at any value `get` has returned for it that `set` takes.
        ParameterNotFoundError when there is no such id.
        """
```

```python
        """Set the parameter, then publish ParameterChanged.

        The parameter may then hold a value other than the one given (see `get`). The event's
        `new` is the value the parameter holds after the set, the one `get` returns.
        ParameterNotFoundError, UnitMismatchError or ValueOutOfRangeError when the id, the unit or
        the value is not one the instrument takes; a refused value changes nothing and publishes
        nothing.
        """
```

## Task 4: `src/patchbay/testing/contract_tests.py`, docstrings only

Lines 18–21 of the module docstring become:

```
Each test works out what it expects from the instrument's parameters and the contract alone,
never from an implementation's code. Values are set at a parameter's bounds, which
`Instrument.get` promises every instrument holds exactly, whatever its resolution. A value one
float past a bound is set too and must be refused, so a check with any slack is caught.
```

The `get_after_set_returns_what_was_set` docstring becomes "Check that, for every parameter set at
a bound, `get` returns the value `set` was given." Then
`git diff 6506e1d -- src/patchbay/testing/contract_tests.py` goes to
`verification/contract-tests-diff.txt`. Its hunks lie only inside docstrings.

## Task 5: `src/patchbay/models.py`, `Parameter`'s docstring

```
    A continuous parameter takes any value in `[minimum, maximum]` in its unit. A choice takes the
    index of one of its `choices`, a boolean 0 or 1, each as a whole number in `Unit.none`. The
    instrument holds each bound exactly, as `Instrument.get` promises.
```

## Task 6: `tests/unit/testing/test_contract_tests.py`

A new section after the widest-bounds test, "a correct instrument of finite resolution":

- **`_VOICES`:** a continuous `Parameter` in `Unit.none`, from 1 to 16, default 1.
- **`_HoldsWholeNumbers(FakeInstrument)`:** `parameters()` returns `(*PARAMETERS, _VOICES)`.
  - `set` runs `_VOICES.check(value)` first, then passes `round(value.value)` on to `super().set`.
  - `load_patch` refuses, with `PatchRejectedError`, a patch whose `voices` value is not whole.
  - Its docstring says it is a correct instrument of finite resolution by `Instrument.get`, and
    that it lives here, not in `patchbay.testing`.
- **`test_a_correct_instrument_of_finite_resolution_passes`:** parametrized over `CONTRACT_TESTS`.
- **`test_the_whole_number_fake_holds_a_value_other_than_the_one_given`:** 3.4 is held as 3.0.
- **`test_the_whole_number_fake_gives_back_a_value_get_returned`:** `set(get())` after 3.4 gives
  back the same value.
- **`test_the_whole_number_fake_publishes_the_value_held_as_new`:** the `ParameterChanged` events'
  `new` values equal `[get()]`, which is not the value given.
- **The module docstring** gains a sentence: a fake holding whole numbers only passes every
  contract test, so none fails an instrument of finite resolution.

`src/patchbay/testing/fake.py` is unchanged; it reads true.

## Task 7: `CHANGELOG.md`

- **A new entry at the top of `### Changed`:** "Twelfth spec, `agent-os/specs/…/`, the revision
  after the owner's review of PR 19: twenty-one findings, each with its disposition in the spec's
  `plan.md`…", followed by bullets for `contracts.py`, `models.py`, `contract_tests.py` and the
  test module. The version stays 0.0.1.
- **The eleventh entry:** where it is superseded it points to the twelfth ("the twelfth spec,
  above, drops 'nearest'", as the ninth entry points to the tenth), and its observed-form sentence
  becomes the promise.

## Task 8 (final): Verification gate

1–6. `scripts/gate.sh` must exit 0, with `verification/gate-run.txt` headed by the date and the
branch. No gate file changes, so no negative tests are rerun.

7. **Docs:** check and record that these read true:
   - `contracts.py`, `contract_tests.py`, `fake.py`, `models.py` and the test module's docstrings
   - `events.py:93`
   - `README.md` and `CLAUDE.md`
   - every standard that names these files

   `contracts.py`'s "none sets a parameter away from its bounds" reads true: the calls past a
   bound are refused, and a refused value changes nothing.
8. **Version:** the `[Unreleased]` entry; 0.0.1.
9. **Retrospective,** from the shipped diff. The expected base proposals, all for #37:
   - **`base/testing/tests.md`, "The suite holds the protocol's promises":** stale; limit it to the
     promises the suite can check (finding 10).
   - **`base/testing/tests.md`, "A correct implementation at the edges passes every contract
     test":** name the finite-resolution fake.
   - **`base/testing/tests.md` or `base/python/events.md`:** name the `new` case, if the diff
     shows they should.

   Then **present-and-file:** present the proposals with a multi-select AskUserQuestion. Revise #37
   in place with "Revised 2026-11-11": the approved proposals, `get`'s wording without "nearest",
   line citations refreshed at the new head, and probe b replaced by the tests. Record the
   `Proposals sent upstream:` line.

Then:

1. **Issue #18:** retitle it and append the "Revised 2026-11-11" paragraph, with no attribution.
2. **The patchbay-vital issue:** present the draft for #8 (double rounding, out-of-range values in
   `patch()`, the floor). Do not file it.
3. Print `git status --short` and stop. No stage, commit, push or PR. PR 19's title and body follow
   after your push, on request.

## Verification

- The gate is green: `verification/gate-run.txt`, exit 0.
- `contract-tests-diff.txt` touches only docstrings.
- The four new tests pass, and `test_a_correct_instrument_of_finite_resolution_passes` runs all 13.
- `probes.txt` V1–V5 match the numbers above, and C1's control fires.
- `git status --short` shows only these files:
  - modified: `CHANGELOG.md`, `src/patchbay/contracts.py`, `src/patchbay/models.py`,
    `src/patchbay/testing/contract_tests.py`, `tests/unit/testing/test_contract_tests.py`
  - new: the spec folder

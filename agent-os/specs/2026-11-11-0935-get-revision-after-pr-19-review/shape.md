# Revision of issue #18's spec after the first review of PR 19 — Shaping Notes

Shaped 2026-11-11 in plan mode with this repository's customized `/agent-os:shape-spec`. The owner
answered the Step 1–5 questions, three design decisions and four wording questions, adding notes
to each that are recorded below as the owner gave them.

## Core Architecture (Non-Negotiable)

- `base/python/toolchain`, `base/python/layout`, `base/python/typing`, `base/python/models` and
  `base/python/errors` — included without asking (Step 5a); their full text in `standards.md`.

## Scope

The owner's review of PR 19 at `6506e1d`, the comment of 2026-11-11 14:06 UTC: 21 findings on the
spec of issue #18 (`agent-os/specs/2026-11-11-0840-get-returns-the-nearest-value-held/`), each
answered in `plan.md`'s dispositions table, numbered in the review's order. Its main finding:
`Instrument.get`'s "nearest" is not met by patchbay-vital, the instrument the issue's evidence comes
from. A new spec folder on the same branch, so PR 19 carries it; the reviewed folder stays its
record. No gate file and no contract test's body, name or order changes. CHANGELOG entry, gate
green, `verification/gate-run.txt`. The version stays 0.0.1. No stage, commit, push or PR by an
agent.

## Shaping answers

- **Step 1, scope:** all 21, in a new folder, as after the reviews of PRs 3, 4, 9, 11 and 15; each
  patchbay-vital claim reproduced at its `84b5ae7` and each core one at `6506e1d`.
- **Step 2, visuals:** none.
- **Step 3, references:** `references.md`; patchbay-vital read-only, run under its own interpreter
  with `-B`, so nothing there is written.
- **Step 4, product context:** aligned, no change: dropping "nearest" changes what a caller may rely
  on, toward what every instrument meets, and adds no field or test to the protocol.
- **Step 5, standards:** the core five, and `testing/tests`, `process/verification-gate`,
  `process/standards-retrospective`, `process/ownership` and `python/events`, snapshot at `e31f7db`.
  This revision changes no sentence of `base/python/models.md` and newly relies on none, so finding
  20 is not noted under it in `standards.md`.

## Decisions

1. **The scope is the review of PR 19 at `6506e1d`, all 21 findings**, each reproduced or probed
   before it is fixed (`verification/probes.txt`, V1–V5 and C1–C2, run at `6506e1d` before any
   edit). Issue #18 stays the spec's issue; every departure from its text below is the owner's.
2. **Findings 1 and 6: neither "nearest" nor "next to the given" is claimed.** `get` promises a
   value the parameter holds, not necessarily the one given: the value given itself at a bound, and
   at any value `get` has returned for it that `set` takes.
   - The evidence against "nearest": on `beats_per_minute`, a linear parameter, given
     216.85141355537831, patchbay-vital holds 216.8514347076416 (2.1e-5 away) where
     216.8514060974121 (7.5e-6 away) is also held (V1); 8,236 of 140,800 sampled values on linear
     parameters (5.8%) are held at a value other than the nearest one held (V2). The cause is
     rounding twice: the curve inverted and rounded to a float32 preset value
     (`DisplayCurve.to_preset`), then that rounded to a float32 normalized value
     (`NormalizedScale.to_normalized`), which the plugin's `fma32` takes to a preset value other
     than the first. The reviewed spec's Decision 2 put the miss on curved parameters alone; it is
     on linear ones too.
   - What claiming either would need. "Next to the given": every sampled value on every curve
     landing on one of the two held values either side of the one given, held by a test; V3's
     165,600 of 165,600 is a sample in a probe, not a test, and no test in either repository holds
     it. "Nearest": the same, landing on the nearer of the two, which 5.8% of sampled values on
     linear parameters do not.
   - The tie clause goes with "nearest", so "the two" (finding 14) has nothing left to refer to,
     and the tie evidence (finding 19) supports nothing in the wording.
3. **Findings 2 and 7: the clause is limited to values "that `set` takes"; `get` promises nothing of
   its range.** `flanger_dry_wet`'s shipped preset 0.7072 displays as 141.44 against [0, 100] (V4),
   so a `get` reading a loaded preset returns a value `set` refuses. Promising an in-range `get`
   would have patchbay-vital clamp or widen its bounds; the limited clause leaves it as it is.
   - **Note for patchbay-vital #8, not a change here** (the owner's): `Instrument.patch` promises a
     state "which `load_patch` takes back unchanged". An instrument whose `get` can return a value
     outside the parameter's bounds would put that value in `patch().values`, and a `load_patch`
     that checks each value with `Parameter.check` would refuse its own patch. So an adapter that
     reports out-of-range values must either keep them out of `values` (carried in `opaque`) or
     accept them on load; the limited clause in `get` leaves that choice to the adapter.
4. **Findings 3, 5 and 8: probe b becomes tests**, in `tests/unit/testing/test_contract_tests.py`.
   The whole-number fake, `_HoldsWholeNumbers`, is a correct implementation of the protocol as now
   worded, so the test that it passes all thirteen contract tests,
   `test_a_correct_instrument_of_finite_resolution_passes`, sits beside `_WideRange`'s, under
   `base/testing/tests.md`'s "A correct implementation at the edges passes every contract test". The
   fake lives in the test module and is not shipped in `patchbay.testing`.
   - Three more tests hold what the fake is and does: a value between two whole numbers is held as
     one of them, not the value given (so the first test is not vacuous); `set(get())` at that
     interior value comes back exactly (finding 8: the reviewed probe ran it only at 16.0, a bound,
     and C2 shows a fake that moves interior values printed the same lines); and
     `ParameterChanged.new` is the value held, not the value given (finding 3).
   - No tie result is asserted: `round` is used, and 3.4 is no tie. The reviewed probe's 2.5 -> 3
     pinned one rule (finding 5).
   - The `new` test is the first anywhere that tells the value held from the value given in
     `ParameterChanged`: `set_emits_parameter_changed_once` sets a bound, where the two agree.
5. **Finding 2, the floor: no sentence in the protocol.** `get`'s clause promises what `get`
   returns, nothing about the rest of the instrument's state. Powers of two from 2**-149 to 2**-43
   as the normalized value the plugin reports: none changes in display through `set(get())`, and 91
   of 107 move the stored preset value (V5 a). As the stored preset value a loaded preset holds, set
   through the normalized path: at 2**-43 and 2**-45 the display comes back one double ulp away (V5
   b), so a `get` reading the loaded preset would not meet the clause there through that path. The
   evidence the reviewed spec omitted is cited now: patchbay-vital's
   `test_a_value_the_parameter_holds_comes_back_exactly` and
   `test_where_volume_s_offset_absorbs_a_preset`, and its host spec's Decision 6, which its
   retrospective corrected at `volume`'s floor.
6. **The wording, each the owner's:**
   - `contracts.py`'s module docstring (finding 9): "...hold it to the behaviour each names in its
     docstring; none sets a parameter away from its bounds, so what `get` returns there rests on
     `get`'s and `set`'s own words and on no contract test."
   - `get` (findings 1, 6, 7, 15): "After `set`, that is a value the parameter holds, not
     necessarily the one given: the value given itself at a bound, and at any value `get` has
     returned for it that `set` takes." `set`: "The parameter may then hold a value other than the
     one given (see `get`)", in place of the issue's "the instrument may hold the nearest value it
     can (see `get`)".
   - `contract_tests.py` (findings 4, 11, 16): "Values are set at a parameter's bounds, which
     `Instrument.get` promises every instrument holds exactly, whatever its resolution. A value one
     float past a bound is set too and must be refused, so a check with any slack is caught."
     `get_after_set_returns_what_was_set`: "Check that, for every parameter set at a bound, `get`
     returns the value `set` was given." Docstrings only: `verification/contract-tests-diff.txt` is
     two hunks against `6506e1d`, the module docstring and that one line.
   - `Parameter` (finding 20): "The instrument holds each bound exactly, as `Instrument.get`
     promises."
7. **Outward edits.** Issue #18 is retitled "Instrument.get returns a value the parameter holds: say
   so in the protocol" and its body gains a "Revised 2026-11-11" paragraph, its proposed wording
   kept as proposed. fromtheoutfit/patchbay-standards#37, which says "nearest", is revised in place
   with a "Revised 2026-11-11" paragraph after the owner approves this retrospective's proposals,
   its numbers kept. The patchbay-vital issue below is presented, not filed.
8. **This morning's texts re-checked without "nearest"**: `fake.py`'s sentence ("It holds every
   value a parameter takes, so `get` returns exactly what `set` was given") reads true and is
   unchanged; `contract_tests.py`'s module docstring is reworded by Decision 6; #37 says "nearest"
   and is revised by Decision 7.
9. **The reviewed record, corrected here; its folder stays as recorded.**
   - Its Decision 3 claimed agreement with `set_emits_parameter_changed_once`, which sets only a
     bound and cannot tell `new` the value held from the value given (finding 12); its Decision 8
     left `new` away from a bound out of the promises the suite does not hold. Decision 4 here adds
     the test that does.
   - Its Decision 3 quoted "The instrument may hold the nearest value it can to the one given" as
     the issue's phrase; "to the one given" was a departure not recorded (finding 13). The sentence
     is rewritten here.
   - Its tie evidence, `parameters.py:65-67`, is the normalized-to-preset grid landing on halves,
     which never reaches `Instrument.set`: `Parameter.check` refuses 0.5 for a boolean (finding 19).
   - Its `references.md` started `to_preset` inside its docstring (the method is at 234) and left
     out `DisplayCurve.to_preset` (169-171), the first rounding (finding 21); `references.md` here
     has both.
   - Its probes gave bare file names on `$` lines (finding 17) and probe a's check had no control
     (finding 18, C1 here: the control fires, the thirteen contract tests never do).

## For patchbay-vital #8 (drafted, not filed)

The owner asked for this issue to be presented, not filed. Its text:

> **Title:** What VitalInstrument holds after a set: three findings from core's review of PR 19
>
> Three findings from core's review of fromtheoutfit/patchbay#19, the spec of
> fromtheoutfit/patchbay#18, for #8 to decide. Core's `Instrument.get` now promises, after `set`, a
> value the parameter holds, not necessarily the one given: the value given itself at a bound, and
> at any value `get` has returned for it that `set` takes. It no longer says "nearest". Evidence:
> fromtheoutfit/patchbay, branch
> `feature/18-instrumentget-returns-the-nearest-value-the-parameter-holds-say-so-in-the-protocol`,
> `agent-os/specs/2026-11-11-0935-get-revision-after-pr-19-review/verification/probes.txt`, run
> against this repository at `84b5ae7`.
>
> 1. **The path a set takes rounds twice.** A displayed value is inverted through the curve and
>    rounded to a float32 preset value (`DisplayCurve.to_preset`, `parameters.py:169-171`), then
>    that is rounded to a float32 normalized value (`NormalizedScale.to_normalized`), and the
>    plugin's `fma32` takes it to a preset value other than the first. 8,236 of 140,800 sampled
>    values on linear parameters (5.8%) are held at a value other than the nearest one held:
>    `beats_per_minute`, given 216.85141355537831, holds 216.8514347076416 where 216.8514060974121
>    is nearer in display, preset and normalized terms. Core's wording allows this. #8 decides
>    whether `VitalInstrument.set` should pick the nearer neighbour.
> 2. **Out-of-range values and `patch()`.** `flanger_dry_wet`'s shipped preset 0.7072 displays as
>    141.44 against [0, 100]. `Instrument.patch` promises a state "which `load_patch` takes back
>    unchanged": an instrument whose `get` can return a value outside the parameter's bounds would
>    put that value in `patch().values`, and a `load_patch` that checks each value with
>    `Parameter.check` would refuse its own patch. So an adapter that reports out-of-range values
>    must either keep them out of `values` (carried in `opaque`) or accept them on load; core's
>    limited clause in `get` leaves that choice to the adapter.
> 3. **`set(get())` at volume's floor.** With the loaded `VitalPreset` as the source of truth,
>    `set(get())` at volume's floor would change the model's stored value and so `patch()`, though
>    `get` is unchanged: 91 of 107 powers of two from 2**-149 to 2**-43, as normalized values, move
>    the stored preset value. As stored preset values set back through the normalized path, 2**-43
>    and 2**-45 come back one double ulp away in display, which core's clause does not allow. #8
>    decides whether `VitalInstrument.set` keeps the stored value when the display value given is
>    the one it already shows.

## Context

- **Visuals:** None.
- **References:** `references.md`.
- **Product alignment:** `mission.md`, as Step 4 says; no change to `agent-os/product/`.

## Standards Applied

**Core (always applied):**
- `base/python/toolchain`, `base/python/layout`, `base/python/typing`, `base/python/models`,
  `base/python/errors` — Step 5a

**Feature-specific:**
- `testing/tests` — "The contract suite": the bounds reason, "The suite holds the protocol's
  promises" (finding 10) and "A correct implementation at the edges passes every contract test",
  which the new fake joins
- `process/verification-gate` — the gate, its transcript
- `process/standards-retrospective` — gate step 9; #37 revised in place
- `process/ownership` — no stage, commit, push or PR by an agent
- `python/events` — `ParameterChanged`'s `new`, which a test now tells from the value given

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
`verification/gate-run.txt`, run after the last change to a file a gate step reads; 292 tests
passed, the 276 before this revision, `test_a_correct_instrument_of_finite_resolution_passes` once
per contract test, and the three tests of the whole-number fake. No gate file changed, so no
negative test was rerun. `verification/contract-tests-diff.txt`: two hunks against `6506e1d`, both
docstrings. `verification/probes.txt`: V1–V5 and C1–C2, run at `6506e1d` before any edit, each
matching `plan.md`'s numbers; patchbay-vital's tree unchanged after them.

**Docs (step 7):** checked and reads true after the change:
- `src/patchbay/contracts.py`: the module docstring, `get` and `set`. "none sets a parameter away
  from its bounds" reads true of `set` calls: every accepted set in the suite is at a bound (the
  reviewed spec's probe a, and C1 here), and the calls past a bound are refused, which changes
  nothing. Two contract tests load `patch()`'s own values, a parameter's default among them,
  through `load_patch`; that is `load_patch` taking back what `patch()` gave, which `patch()`
  promises, not a set, and what they check is `patch()`, not `get`.
- `src/patchbay/models.py`: `Parameter`'s docstring; the module docstring, unchanged, says nothing
  of what is held.
- `src/patchbay/testing/contract_tests.py`: the module docstring and
  `get_after_set_returns_what_was_set`'s; the other twelve tests' docstrings say nothing of a value
  away from a bound.
- `src/patchbay/testing/fake.py`: unchanged, and true (Decision 8).
- `tests/unit/testing/test_contract_tests.py`: the module docstring's new clause, and each new
  test's docstring against its body.
- `src/patchbay/events.py:93`: "the value it has now", which `set` names and a test now holds.
- `README.md` (lines 13-14 and 24-26) and `CLAUDE.md`: nothing on what `get` returns.
- No "nearest" is left in `src/`, `tests/`, `README.md`, `CLAUDE.md` or `agent-os/standards/`.
- The standards that name the changed files: `base/testing/tests.md`'s "The contract suite" (the
  bounds reason, "The suite holds the protocol's promises", "A correct implementation at the edges
  passes every contract test") is the retrospective's below; `base/python/errors.md`, `layout.md`,
  `models.md`, `toolchain.md` and `typing.md` cite these files for what this change leaves alone.

**Version (step 8):** the twelfth spec's entry at the top of `### Changed` in `[Unreleased]`,
`CHANGELOG.md`, and the eleventh's pointing to it where superseded. The version stays 0.0.1.

## Standards Retrospective

Step 9, always last. Answered from the shipped diff; there are no project standards in this
repository, so nothing is edited here, `index.yml` is unchanged, and every change is a base
proposal, all for fromtheoutfit/patchbay-standards#37, revised in place.

1. **A pattern no standard covers:** a correct instrument of finite resolution beside the one at
   the widest bounds, and tests of that fake telling apart what a contract test at a bound cannot:
   a value held other than the one given, a value `get` returned coming back, and
   `ParameterChanged`'s `new` the value held. Proposal 3 below.
2. **A standard wrong or stale:** `base/testing/tests.md`'s bounds reason (#37's proposal 1, kept,
   its evidence now the test rather than a probe), and its "The suite holds the protocol's
   promises, a refusal's among them" (finding 10), which the protocol now outruns. Proposal 2 below.
   `base/python/events.md` checked again: it says nothing of what an event's payload carries, so
   the `new` case is `tests.md`'s, and no proposal.
3. **A deliberate deviation:** none.
4. **A pointer moved:** none; `_WideRange`, `test_a_correct_instrument_with_the_widest_bounds_passes`,
   `_other_value`, `_out_of_range` and `test_contract` are where the standards say.

Proposals sent upstream: fromtheoutfit/patchbay-standards#37, revised in place.

#37 was revised on 2026-11-11 with a "Revised 2026-11-11" paragraph that says which of its texts
changed and why (the review of PR 19: "nearest" was not evidenced), its proposal 1 kept as filed
with its evidence now a test, proposals 2 and 3 added, and its title widened to name all three; each
citation checked against this branch's working tree before the edit. The standard itself is written
from the merged code, not from the issue's text, as the owner asked. Issue #18 was retitled "Instrument.get
returns a value the parameter holds: say so in the protocol" and its body gained a "Revised
2026-11-11" section, its proposed wording kept as proposed (Decision 7).

### Standards retrospective (proposed, base)

- `base/testing/tests.md`, "The contract suite", fourth bullet — #37's proposal 1, kept as filed:
  "Values are set at a parameter's bounds, which every instrument holds exactly whatever its
  resolution, as the protocol's `get` promises, so no contract test sets a value between a
  continuous parameter's bounds or relies on an arbitrary value coming back as itself". Verified
  now against `src/patchbay/contracts.py` (`Instrument.get`), `src/patchbay/testing/contract_tests.py`
  (its module docstring, `_other_value`, `_out_of_range`) and `tests/unit/testing/test_contract_tests.py`
  (`test_a_correct_instrument_of_finite_resolution_passes`). Filed as
  fromtheoutfit/patchbay-standards#37; its text revised in place, 2026-11-11.
- `base/testing/tests.md`, "The suite holds the protocol's promises, a refusal's among them" — the
  lead becomes "The suite holds the protocol's promises it can check, a refusal's among them, and
  the protocol says which it cannot", with: patchbay's suite sets no parameter away from its
  bounds, so what `get` returns there, and what `ParameterChanged` carries as `new`, rest on the
  protocol's words alone, as its module docstring says. Verified against `src/patchbay/contracts.py`
  (the module docstring, `get`, `set`) and `src/patchbay/testing/contract_tests.py`, and
  `verification/probes.txt` C1. Proposed, not applied; filed as fromtheoutfit/patchbay-standards#37, number 2.
- `base/testing/tests.md`, "A correct implementation at the edges passes every contract test" —
  adds one of finite resolution: patchbay's fake with a continuous parameter holding whole numbers
  only, kept in the test module and not shipped, passes every contract test; tests of that fake
  show it holds a value other than the one given, gives back a value `get` returned, and publishes
  the value held as `ParameterChanged`'s `new`, which a contract test setting a bound cannot tell
  from the value given. Verified against `tests/unit/testing/test_contract_tests.py`
  (`_HoldsWholeNumbers`, `test_a_correct_instrument_of_finite_resolution_passes`,
  `test_the_whole_number_fake_holds_a_value_other_than_the_one_given`,
  `test_the_whole_number_fake_gives_back_a_value_get_returned`,
  `test_the_whole_number_fake_publishes_the_value_held_as_new`). Proposed, not applied; filed as
  fromtheoutfit/patchbay-standards#37, number 3.

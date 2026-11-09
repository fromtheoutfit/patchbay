# Gate spec after the sync to e31f7db, and Event.at's offset — Shaping Notes

Shaped 2026-11-09 in plan mode with this repository's customized `/agent-os:shape-spec`. The owner
answered the Step 1–5 questions and three design questions.

## Core Architecture (Non-Negotiable)

- `base/python/toolchain`, `base/python/layout`, `base/python/typing`, `base/python/models` and
  `base/python/errors` — included without asking, at the owner's word, ahead of item 10 adding the
  last four to Step 5a; their full text in `standards.md`.

## Scope

Issue #12 as it stands, the work the base standards at `e31f7db` ask of this repository's gate files
after the sync `4b1b3e2`, items 1 to 11 in order with the gate green after each; then issue #13,
`Event.at`'s offset at its own instant. A gate spec: `scripts/gate.sh`, the harness and the gate
task's wording change, each changed step with its negative test and each new guard with its
mutation. CHANGELOG entry, gate green, `verification/gate-run.txt`. No stage, commit or push by an
agent.

## Shaping answers

- **Step 1, scope:** #12's items 1 to 11 in order, then #13, one spec folder on this branch.
- **Step 2, visuals:** none.
- **Step 3, references:** `references.md`.
- **Step 4, product context:** the `base/python/models.md` citation on `tech-stack.md`'s pydantic
  line, as item 11 asks; nothing else.
- **Step 5, standards:** the core five, and `process/verification-gate`, `process/standards-sync`,
  `process/standards-retrospective`, `process/ownership`, `python/events`, `testing/tests`. Snapshot
  at `e31f7db` in `standards.md`.

## Decisions

1. **#12 and #13 are one spec, for one PR, at the owner's call.** #12 edits no events file. The two
   meet at `base/python/events.md`: #12's item 11 reads it against the tree the sync landed on, and
   #13 makes one sentence of it stale, its new text proposed in this spec's retrospective. This
   spec's feature is the gate; #13 changes no gate file, and no gate file changes because of it.
   Order: items 1 to 11, then #13.
2. **Item 1: the sync's entry is written now, and says it is late.** The sync's commit `4b1b3e2`
   (PR #14) merged without a `CHANGELOG.md` entry, so it cannot carry one as item 1 says.
   `sync base standards: 11ceffd -> e31f7db` goes under `[Unreleased]` naming that, and the header
   is reworded to the rule every later sync follows.
3. **Item 8: step 5 refuses what pytest reads, not only `.py` files.** The rule the issue cites asks
   the step to refuse any file git ignores there that the tool would read. Source at 9.2.0 names the
   four root files read ahead of `pyproject.toml` and the doctest glob `test*.txt`; the probe in
   `verification/probes.txt` decides which are refused.
4. **Item 9: `upper` and `upper_run` are taken**, resolving `<CASE>/PATCHBAY` in this repository's
   layout, so the two harnesses stay parallel.
5. **`only` stays step 6's.** A new `named <path>...` holds the entries `fail_list` indents eight
   spaces, which is what the sibling's `only` does; here `only` reads step 6's two-space drift
   report.
6. **Stale cases found while shaping and at the baseline run.** The harness was last run before the
   contracts spec and the sync, and the issue does not name these:
   - r's shims ` -- . ` and ` --ignored ` match step 1's new refusal first, and become
     ` --exclude-standard -- . ` and ` --others --ignored `;
   - p's `holds 'Success: no issues found in 3 source files'` rested on the tree's size (19 now),
     and stops counting;
   - q's scratch conftest deselected on `"broken"`, which now matches 14 contract tests too; it
     names `test_broken_assertion`, and `holds '1 deselected'` stays exact.
7. **`gate-run.txt` stays the last thing done.** The owner's order is gate green, `gate-run.txt`,
   present-and-file. Filing writes the issue number into `shape.md`, an edit after the run, so the
   gate is rerun and the transcript overwritten once that is written.

## Context

- **Visuals:** None.
- **References:** `references.md`.
- **Product alignment:** `agent-os/product/tech-stack.md`, the `models.md` citation.

## Standards Applied

**Core (always applied):**
- `base/python/toolchain`, `base/python/layout`, `base/python/typing`, `base/python/models`,
  `base/python/errors` — Step 5a

**Feature-specific:**
- `process/verification-gate` — the shape of the gate, the skeleton and the negative-test rules
- `process/standards-sync` — item 1's CHANGELOG entry and the harness's fixture
- `process/standards-retrospective` — gate step 9, the probe rule and the route of a base proposal
- `process/ownership` — no stage, commit or push by an agent
- `python/events` — #13's rule
- `testing/tests` — #13's test

## Verification Gate

Spec is not complete until `scripts/gate.sh` passes — `bash -n` on every shell script under
`scripts/` as git lists them, with no tracked file a `.gitignore` ignores; `uv sync --locked`, then
`uv run --locked ruff format --check .`, `uv run --locked ruff check .`, `uv run --locked mypy` and
`uv run --locked pytest` under `pyproject.toml`'s `[tool.*]` rule set and `uv.lock`'s pins; and
`scripts/sync-standards.sh --check` against `../patchbay-standards` at the commit in
`agent-os/standards/base/.version` — and the three judgment steps are recorded, in this order: Docs,
Version, then the standards retrospective below.

**Results (2026-11-09):** exit 0 on branch
`task/12-gate-spec-3-take-patchbay-standards-17-19-20-and-21-after-the-sync-that-brings-them-in`,
`verification/gate-run.txt`, the last thing done before hand-over. The gate was run and green at
five points while working, not after every item as asked: after item 1, after items 2 to 5 together,
after item 7 (item 6 records a transcript and changes no tree file), after items 8 to 10 together,
and after item 11 and #13 together. The whole harness was rerun after the last edit `mk` copies, one run per transcript:
`verification/gate-negative-tests.txt`, 98 runs, 0 unexpected; `verification/ci-negative-test.txt`
(j), 3 runs, 0 unexpected. The harness had 3 unexpected at the baseline run on this branch before any
edit: g's upper-case run (item 5), and p's file count and q's scratch conftest (Decision 6).
`verification/guard-mutations.txt`: 15 mutations, each as required. M14 is the one that must pass: it
removes `named` from M7, and passing shows `named` alone is what caught M7, the proof an assertion
gets. `verification/gate-sh-diff.txt`: the hunks against the sibling's `gate.sh` at `e31f7db` are
step lists, pins, paths and the refusal's pathspec alone. `verification/probes.txt`: section 1
decides item 8 (all four root names and `test*.txt` read; `tox.ini`, `setup.cfg` and a `pytest.ini`
under `tests/` not the config); section 2 is probe r before and after #13, only the zone #13 names
changing its answer.

**Docs (step 7):** checked and reads true after the change:
- `README.md` (the step list's 1 and 5, the paragraph on what the steps read);
- `CLAUDE.md` (the gate sentence);
- `.claude/commands/agent-os/shape-spec.md` (Step 5a, Step 5b's note and prompt, the gate task and its
  template lines);
- the headers of `scripts/gate.sh` and `scripts/gate-negative-tests.sh`, and the docstring and comment
  of `src/patchbay/events.py`;
- `agent-os/product/tech-stack.md` (the `models.md` citation);
- `CHANGELOG.md`'s header.

Item 11: `base/python/layout.md`, `typing.md`, `models.md`, `errors.md`, `events.md`,
`base/testing/tests.md` and "Dependencies", "ruff" and "mypy" of `base/python/toolchain.md`, read
against the tree the sync landed on, before #13. Every test and file they name exists (88 test names;
the one absent path, `src/patchbay_core/__init__.py`, is toolchain's example of what uv_build would
look for). Their counts hold: six entries in the ruff ignore list, four suppressions in `src/`, six
coded ignores in the tests, one `conftest.py`, no `TypeVar`, `ParamSpec`, `Generic` or `TypeAlias`, no
future import, every model's class line frozen, the import direction. No rule read false against that
tree. What this spec's own changes make stale is below.

**Version (step 8):** the ninth spec's entry and the sync's late entry under `### Changed` in
`[Unreleased]`, `CHANGELOG.md`. The version stays 0.0.1.

## Standards Retrospective

Step 9, always last. Answered from the shipped diff; there are no project standards in this
repository, so every change is a base proposal.

1. **A pattern no standard covers:** none. `named`, `shim`, `upper` and `upper_run` follow the
   sibling's harness.
2. **A standard wrong or stale:** two, both from this spec's own changes (below). `index.yml`'s
   `python/events` description goes with the first.
3. **A deliberate deviation:** one, below.
4. **A pointer moved:** none. Every test and file the standards name is still there.

- **Deviation, not a standard change:** the sync's commit `4b1b3e2` carried no `CHANGELOG.md` entry, as
  `base/process/standards-sync.md` asks, and this spec wrote it late (Decision 2). One-off; the rule
  stands, and `CHANGELOG.md`'s header now says it.

Proposals sent upstream: fromtheoutfit/patchbay-standards#27.

### Standards retrospective (proposed, base)

- `base/python/events.md`, "An event is stamped with the UTC time it was built" — a time given for
  `at` is accepted only where the zone's answer for no particular instant and its offset at that time
  are both zero, and the sentence saying a `tzinfo` answering zero for no instant and another offset
  at a real one "is accepted, and converted at that instant's offset" says it is refused; the
  `python/events` description in the root `index.yml` follows. Verified against `src/patchbay/events.py`
  (`_in_utc`), `tests/unit/test_events.py` (`test_an_event_s_time_is_refused_unless_utc`, its case
  "zero for no instant, an hour east at this one") and this spec's `verification/probes.txt` section
  2. Proposed, not applied; filed as fromtheoutfit/patchbay-standards#27.
- `base/python/toolchain.md`, "The gate's tool steps" — the pytest step's refusal names what pytest
  reads at the pin: any `.py` or `test*.txt` file git ignores under `tests/`, and an ignored
  `conftest.py`, `pytest.toml`, `.pytest.toml`, `pytest.ini` or `.pytest.ini` at the root; and "so a
  tracked file `.gitignore` matches is read" goes, since the gate's first step now refuses such a file
  before ruff or mypy is given the list, and the citation moves off `3f910d8`. Verified against
  `scripts/gate.sh` steps 1 and 5, tests p and q of `scripts/gate-negative-tests.sh` and this spec's
  `verification/probes.txt` section 1. Proposed, not applied; filed as
  fromtheoutfit/patchbay-standards#27.

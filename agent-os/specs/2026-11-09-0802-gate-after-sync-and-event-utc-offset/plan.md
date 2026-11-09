# Gate spec: take the base standards at e31f7db (#12), and Event.at's offset (#13)

## Context

`4b1b3e2` synced the base standards to `e31f7db`. Those standards change the shared gate skeleton and the harness rules, and add five standards to the Step 5a tier. Issue #12 records the work this repository owes after that sync; this is the gate spec that does it. Issue #13 comes along as a small item: `Event._in_utc` accepts a `tzinfo` that answers zero for no instant and +01:00 at every real one.

Outcome: `scripts/gate.sh` on the sibling's skeleton, differing only in step lists, pins and paths (the refusal's pathspec among them). Every changed step has a negative test, every new guard a mutation, and the whole harness is rerun last. No stage, commit, push or PR by an agent.

Three things the issue does not anticipate, found while shaping:

- **The sync merged without its CHANGELOG entry.** Item 1 says the sync's commit carries one; `4b1b3e2` changed no `CHANGELOG.md`.
- **Test r's shims hit step 1 once the refusal exists.** Both ` -- . ` and ` --ignored ` match the refusal's listing first, so r would fail at step 1 for the wrong reason. They become ` --exclude-standard -- . ` and ` --others --ignored `.
- **Test p's `holds 'Success: no issues found in 3 source files'` is already stale.** The contracts spec grew `src/` and `tests/` to 19 files. The assertion stops resting on the count.

## Decisions for shape.md (owner's answers, 2026-11-09)

1. **#12 and #13 in one spec, for one PR, at the owner's call.** #12 edits no events file. The two meet at `base/python/events.md`: item 11 reads it, and #13 makes one sentence stale and proposes the new text. This spec's feature is the gate; #13 changes no gate file. Order: items 1 to 11, then #13.
2. **Item 1:** the entry is written now, `sync base standards: 11ceffd -> e31f7db`, saying `4b1b3e2` did not carry it. The header is reworded to the rule.
3. **Item 8:** step 5 refuses, when git ignores them, the root config files pytest reads ahead of `pyproject.toml` and `test*.txt` under `tests/`, subject to the probe at the pin. Source at 9.2.0 (`_pytest/config/findpaths.py`, `doctest.py`) names `pytest.toml`, `.pytest.toml`, `pytest.ini`, `.pytest.ini` and the glob `test*.txt`. `tox.ini` and `setup.cfg` come after `pyproject.toml` and are never the config.
4. **Item 9:** take `upper` and `upper_run`, resolving `<CASE>/PATCHBAY` in this repository's layout.
5. **`only` stays step 6's.** A new `named <path>...` holds the entries `fail_list` indents eight spaces, as the sibling's `only` does.
6. **Visuals:** none. **Product:** the `models.md` citation only.

## Tasks

### Task 1: Save spec documentation

Create `agent-os/specs/2026-11-09-{HHMM}-gate-after-sync-and-event-utc-offset/` (`date +%H%M` at execution) with `plan.md`, `shape.md`, `standards.md`, `references.md` and `verification/`.

- `standards.md`: full text at `e31f7db` of the core five (`python/toolchain`, `layout`, `typing`, `models`, `errors`) and `process/verification-gate`, `standards-sync`, `standards-retrospective`, `ownership`, `python/events`, `testing/tests`.
- `references.md`: the sibling's `scripts/gate.sh` and harness at `e31f7db` (w, y, `shim`, `upper`, `upper_run`, `only`); its PR 23 revision's `gate-sh-diff.txt` and `guard-mutations.txt`; its PR 25 revision's probe r; this repository's gate spec `2026-11-07-0711`.

Run `scripts/gate.sh` after each task below that changes a tree file (items 1, 2, 3 to 5, 7, 8, 9, 10, 11, #13), and rerun the harness cases that task touches. Only the final harness run is kept.

### Task 2: Item 1, CHANGELOG

Add the sync entry under `[Unreleased]` and reword the header (`CHANGELOG.md:7-10`).

### Task 3: Item 2, `scripts/gate.sh` skeleton

Take the sibling's hunks from `../patchbay-standards` main (`e31f7db`):

- the root guard's `--is-inside-work-tree`;
- `git_list`, `listed <file> <path...>`, `fail_list`;
- step 1's `mktemp -d`, checked, then its trap;
- the refusal, `git_list "$tmp/ignored" --cached --ignored --exclude-per-directory=.gitignore -- .`;
- the banner and the header sentences; the "needs" line gains `mktemp`.

Steps 2, 4 and 5 read from `"$tmp/..."`, with the sentinels and `ok=` gone and each step's reason kept. Step 5's listing keeps `--exclude-standard`. Before editing, confirm `git ls-files --cached --ignored --exclude-per-directory=.gitignore -- .` is still empty (empty at shaping).

### Task 4: Items 3, 4 and 5, the harness cases

- **Helpers:** `shim` becomes idempotent, as the sibling's, for g and r. Add `named`.
- **p (item 3):**
  - force-added under `.gitignore`: step 1 names it (`named`), and a second such file under one FAIL line;
  - the mypy `--exclude-gitignore` bug case, while still matched, its `holds` no longer counting files;
  - pattern out of `.gitignore`: step 2 names the file, then the typed version, step 4;
  - only `.git/info/exclude`, and only a global excludes file (`GIT_CONFIG_GLOBAL`): step 1 passes and step 2 reads it.
- **g (item 4):**
  - corrupt index fails at the refusal's listing;
  - shim on ` --exclude-standard -- scripts ` keeps that listing covered;
  - a copy under another repository's `.git/` and one in a bare repository fail by name (copied from `go/copy`, which has no `.venv`);
  - a `mktemp` that makes nothing fails step 1 by name.
- **g (item 5):** the upper-case run expects exit 0.
- **r:** the two tightened shims above.

### Task 5: Item 6, `verification/gate-sh-diff.txt`

`diff -u` against the sibling's `gate.sh` at `e31f7db`, with a header classifying the hunks. Allowed: step lists, pins, paths, the refusal's pathspec. Re-recorded after Task 7's edit, so the kept file shows the shipped script. A hunk outside those is fixed, not explained.

### Task 6: Item 7, gate task text and CLAUDE.md

`.claude/commands/agent-os/shape-spec.md` (gate task, its `shape.md` template paragraph) and `CLAUDE.md`'s gate sentence gain step 1's refusal of "a tracked file a `.gitignore` ignores". `README.md` step 1 follows.

### Task 7: Item 8, step 5's refusal

1. **Probe first**, on a scratch export at the pinned pytest, into `verification/probes.txt`, setup shown. Each of the four names with `addopts` deselecting a tracked failing test. Controls that must not take effect: `tox.ini` and `setup.cfg` with the same `addopts`, and a `pytest.ini` under `tests/`. An ignored `tests/unit/test_local.txt` with a failing doctest, and a `local.txt` that is not collected. Where probe and documentation disagree, the source at the pin decides.
2. **`gate.sh`:** the step 5 listing adds the root names the probe confirms, each refused by name with its own reason. An arm for `test*.txt` at any depth under `tests/`.
3. **q:** one case per name the probe confirms and the doctest case, each failing step 5 by name, 6/6 never printed.
4. **Docs:** the gate header, `README.md`, `CLAUDE.md` and the gate task's step 5 text.

### Task 8: Item 9, harness header and `upper`

Header gains the mutation rule and the rerun rule. `upper`/`upper_run` replace g's inline UPC block. `upper_run g 0 pwd` with `holds '<COPY G>/PATCHBAY'` gives the helper an assertion a mutation can trip without history. The usage lines for g, p, q and r are updated.

### Task 9: Item 10, Step 5a

In `shape-spec.md`: the tier's list, one line each; the "not written yet" line goes; Step 5b's prompt line and its note; the template's "Core Architecture" and "Standards Applied, Core" lines. Five standards.

### Task 10: Item 11, read the standards against the tree

Read `layout`, `typing`, `models`, `errors`, `events`, `testing/tests` and toolchain's "Dependencies", "ruff" and "mypy" against the tree, before #13. Add the `base/python/models.md` citation to `agent-os/product/tech-stack.md`'s pydantic line. Findings are recorded in `shape.md`; a false rule is a proposal, never an edit under `base/`.

### Task 11: #13, `Event._in_utc`

1. Add the case beside the London cases in `test_an_event_s_time_is_refused_unless_utc`, a `tzinfo` answering zero for `None` and +01:00 at an instant. Show it red.
2. `src/patchbay/events.py:73`: refuse when `zone.utcoffset(None) != timedelta(0) or at.utcoffset() != timedelta(0)`. Update the comment and the module docstring.
3. Rerun probe r (the sibling's `utc_zone.py`) at the pinned versions into `verification/probes.txt`: every answer as before, but the zone above, now refused.

### Task 12: Guard mutations, `verification/guard-mutations.txt`

After the last edit to the gate's scripts. Each is a fresh copy of the tree as git lists it, outside the repository, with one guard deleted or put back, run through the covering case. Each must come back `UNEXPECTED`, harness exit 1.

| Guard | Case |
|---|---|
| root guard without `--is-inside-work-tree` | g |
| refusal listing's status ignored | g |
| `scripts/` listing's status ignored | g |
| `mktemp` check deleted | g |
| refusal deleted | p |
| refusal reading `--exclude-standard` | p |
| `fail_list` stopping at the first path | p |
| step 2, 4 and 5 listing statuses ignored (one each) | r |
| each new step 5 arm deleted (config, `test*.txt`) | q |
| `upper_run` not entering the upper-case path | g |
| `named` no longer comparing | p |
| p's reworded `holds` given text mypy does not print | p |

### Task 13: Rerun the whole harness

After every edit that `mk` copies. One run per transcript: `scripts/gate-negative-tests.sh > verification/gate-negative-tests.txt`, and `scripts/gate-negative-tests.sh j > verification/ci-negative-test.txt`. Each ends on `N runs, 0 unexpected`.

### Task 14 (FINAL): Verification gate

Run in this order:

1. **CHANGELOG entry** for the spec under `[Unreleased]`.
2. **`scripts/gate.sh`:** steps 1 to 6 green.
3. **`verification/gate-run.txt`**, first line the date and branch.
4. **Step 7, Docs**, recorded in `shape.md`: `README.md`, `CLAUDE.md`, header comments, the standards naming them.
5. **Step 8, Version**, recorded in `shape.md`; the version stays 0.0.1.
6. **Step 9, the retrospective** from the shipped diff, always last. Expected proposals, to be verified against what ships: `base/python/events.md` and its index description (#13), and `base/python/toolchain.md`'s "The gate's tool steps" (step 5's scope, which item 8 changes).
7. **Present and file:** AskUserQuestion, multi-select; the approved ones as one issue on `fromtheoutfit/patchbay-standards`, no attribution; numbers or `declined by owner, <date>` written in `shape.md`; `Proposals sent upstream:` always recorded.
8. **Rerun the gate and overwrite `gate-run.txt`,** since step 7 edits `shape.md` and the standard says an edit after the run is not covered by it. The transcript holds that one run.
9. **Stop and print `git status --short`.** Retrospective edits are listed apart from the feature's.

## Critical files

- `scripts/gate.sh`, `scripts/gate-negative-tests.sh`
- `.claude/commands/agent-os/shape-spec.md`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `agent-os/product/tech-stack.md`
- `src/patchbay/events.py`, `tests/unit/test_events.py`
- Never edited: `agent-os/standards/base/`, the `base:` section of `index.yml`, `scripts/sync-standards.sh`, `.github/workflows/gate.yml`

## Verification

- `scripts/gate.sh` exits 0 after each task and at the end; `gate-run.txt` is the last run.
- `gate-sh-diff.txt` shows only step lists, pins, paths and the refusal's pathspec.
- `gate-negative-tests.txt` and `ci-negative-test.txt` each end on 0 unexpected.
- Every row of the mutation table comes back `UNEXPECTED` with harness exit 1.
- `probes.txt` holds the pytest probe and probe r at the pins.

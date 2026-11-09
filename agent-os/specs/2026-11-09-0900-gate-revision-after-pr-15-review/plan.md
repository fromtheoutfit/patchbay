# Gate revision after the review of PR 15

## Context

The owner's review of PR 15 at `912987a` lists 13 findings. Findings 1 to 4 are the serious ones: the gate can pass when it should fail, because a config file beside `pyproject.toml` can replace the rule set. The rest are `Event.at` validation (5, 6, 8), comments and docs that don't match the code (7, 9, 10, 11), and cleanup (12, 13).

This revision answers all 13 in a new spec folder on the same branch, so PR 15 carries it. The reviewed spec's folder stays its record. It is a gate spec: `scripts/gate.sh`, the harness and `[tool.pytest.ini_options]` change, each changed step with its negative test and each new guard with its mutation. No stage, commit, push or PR by an agent.

## Decisions for shape.md (owner's answers, 2026-11-09)

1. **All 13, in a new folder, each finding reproduced or probed before it is fixed.** Dispositions below.
2. **Findings 1, 2, 4: the tools are told which config to read.** `ruff --config pyproject.toml`, `mypy --config-file pyproject.toml`, `pytest -c pyproject.toml`, subject to the probe, nested `ruff.toml` included. Step 5's list of four names goes.
3. **`-p no:doctest` joins `addopts`.** pytest then reads no `.txt`, and the `test*.txt` arm goes. A later `--doctest-glob` fails loudly.
4. **A root `uv.toml` is refused by name, tracked or not.** uv has no equivalent flag: `--config-file` takes only a `uv.toml`, and `--no-config` would drop `[tool.uv] required-version`.
5. **Finding 3: the claim is corrected, not the code.** The refusal reads the work tree's `.gitignore` files, and CI's clean checkout is the one that counts; a local run with an uncommitted edit can disagree. The gate.sh comment changes and a base proposal corrects the standard's sentence.
6. **Finding 6: the claims soften.** The rule stays: both answers zero, at the time given. A zone whose offset moves answers `None` and is refused every season; a `tzinfo` claiming zero for no instant is taken at its word only for the time given.
7. **patchbay-standards#27 is revised in place** after the owner approves the proposals, with a "Revised" paragraph, its numbers kept, no attribution.
8. **Out of scope:** environment variables (`PYTEST_ADDOPTS`, `UV_*`), and `.pre-commit-config.yaml`'s hooks, which are a convenience and not the gate.

Visuals: none. Product alignment: N/A.

## Dispositions

| # | Finding | Answer |
|---|---|---|
| 1 | Ignored ruff/mypy configs and `uv.toml` replace the rules | Explicit flags; root `uv.toml` refused |
| 2 | Untracked or tracked `pytest.ini` deselects tests | `pytest -c pyproject.toml` |
| 3 | "Only committed `.gitignore` files count" is false | Claim corrected; both directions pinned by cases |
| 4 | Hard-coded pytest names | List and `test*.txt` arm gone |
| 5 | Misbehaving `tzinfo` escapes as a built-in | Refused as `ValueError` from the validator |
| 6 | Season-dependent for a zero-for-`None` zone | Claims softened |
| 7 | Refusal covers files no step reads | Pathspec narrowed to `scripts '*.py' '*.pyi'` |
| 8 | No test for zero for `None`, `None` at an instant | Parametrized case |
| 9 | `CLAUDE.md` "there" points at the wrong thing | Clause moved back beside `scripts/` |
| 10 | Second `### Changed` heading | Entries moved into the existing section |
| 11 | Step 5's listing message says "under tests/" | Message names `tests/` and the root `conftest.py` |
| 12 | Step 4's second listing | Filters step 2's list |
| 13 | Copied fixtures in the harness | Helpers |

## Tasks

### Task 1: Save spec documentation

Create `agent-os/specs/2026-11-09-{HHMM}-gate-revision-after-pr-15-review/` with `plan.md`, `shape.md`, `standards.md`, `references.md` and `verification/`.

- `standards.md`: full text at `e31f7db` of the core five and `process/verification-gate`, `standards-sync`, `standards-retrospective`, `ownership`, `python/events`, `testing/tests`.
- `references.md`: `scripts/gate.sh` and the harness at `912987a`; the sibling's `gate.sh` at `e31f7db`; the review comment; `agent-os/specs/2026-11-07-0711-gate-revision-after-pr-9-review/`.

Run `scripts/gate.sh` after each task below that changes a tree file, and rerun the harness cases it touches. Only the final harness run is kept.

### Task 2: Reproduce and probe, `verification/probes.txt`

On scratch copies at the pins, setup shown:

- Reproduce findings 1, 2, 3 (both directions), 5 and 7 at `912987a`.
- With each flag and without it: `ruff.toml`, `.ruff.toml` and a nested `tests/ruff.toml`; `mypy.ini`, `.mypy.ini` and `setup.cfg`; the four pytest names. Each must change the rules without the flag and not with it.
- `uv.toml` beside `pyproject.toml` overriding `required-version`.
- `-p no:doctest` in `addopts`: an ignored `test_local.txt` is not collected.

Where a flag does not hold, return to the owner before changing the plan.

### Task 3: Findings 9, 10, 11

- `CLAUDE.md`: "(any other file there fails the step)" moves back beside `scripts/`.
- `CHANGELOG.md`: the sync entry and the ninth spec's entry move into the existing `### Changed`; the second heading goes.
- `scripts/gate.sh` step 5's listing failure names `tests/` and the root `conftest.py`; r's pinned text follows.

### Task 4: Findings 1, 2, 4, the rule set is pyproject.toml's

- `gate.sh`: the three flags on the four tool commands. Step 2 refuses a root `uv.toml` by name before `uv sync`. Step 5's listing is `tests conftest.py` again, and its config and `test*.txt` arms go. Header follows.
- `pyproject.toml`: `addopts` gains `-p no:doctest`, with its reason in the comment.
- Harness:
  - New case s: a tracked fault stays failing at its step with each config file present (`ruff.toml`, `.ruff.toml`, nested `tests/ruff.toml`, `mypy.ini`, `.mypy.ini`); `uv.toml` fails step 2 by name.
  - q: the four pytest names no longer refused, the tracked failing test now fails step 5 with pytest's own reason; `pytest.ini` shown ignored, untracked and tracked, with the gate at `912987a` passing where it had the bug. An ignored `test_local.txt` passes, unread.
  - m: expected text follows what `--config` prints.

### Task 5: Findings 7 and 12, listing what the steps read

- Step 1's refusal: `-- scripts '*.py' '*.pyi'`.
- Step 2 lists `'*.py' '*.pyi'`, with its reason reworded; no case filter.
- Step 4 filters `py` by `src/*|tests/*`, with no listing of its own.
- Harness: r loses step 4's case and narrows step 2's shim; a force-added file no step reads passes (finding 7); k gains a root module typed wrong that step 4 never reads.

### Task 6: Finding 3, the claim

`gate.sh`'s header and p's notes say what is read. p gains the reviewer's other direction: an untracked `tests/unit/.gitignore` matching a tracked test fails step 1 naming it, and an uncommitted removal of the pattern passes step 1.

### Task 7: Findings 5, 6, 8, `Event.at`

- `_in_utc` asks the zone and builds its message inside one `try`; anything the zone raises is re-raised as `ValueError` from it, so pydantic refuses it as the package's error.
- Message and docstrings stop claiming "all year" (`src/patchbay/events.py`, `tests/unit/test_events.py:130,142`).
- Tests: red first, for a bare `tzinfo`, one raising at a real instant, one returning `0`, and zero for `None` with `None` at an instant. A zero-for-`None` zone at zero in January shown accepted.

### Task 8: Finding 13, harness fixtures

`returns_any <path>` and `wrong_version <path> <test name>` replace the copied bodies in k, l, p and q.

### Task 9: Docs

`README.md`, `CLAUDE.md`, the gate task and template in `shape-spec.md`, the `pyproject.toml` header (`uv.toml`), and both script headers read true of the above.

### Task 10: `verification/gate-sh-diff.txt`

Against the sibling at `e31f7db`. Hunks are step lists, pins, paths and the refusal's pathspec, and one named deviation: the header's corrected `.gitignore` sentence, until the sync brings the standard's correction.

### Task 11: Mutations, `verification/guard-mutations.txt`

After the last edit to the gate's scripts, on fresh copies, each coming back `UNEXPECTED` with harness exit 1:

| Guard | Case |
|---|---|
| each of `ruff format`, `ruff check`, `mypy`, `pytest` without its flag | s, q |
| `uv.toml` refusal deleted | s |
| `-p no:doctest` removed from `addopts` | q |
| step 4's filter deleted | k |
| refusal pathspec back to `.` | p |
| step 2 and step 5 listing statuses ignored | r |
| `at.utcoffset() not in (None, timedelta(0))` | pytest |
| `_in_utc`'s `try` removed | pytest |

### Task 12: Rerun the whole harness

One run per transcript: `gate-negative-tests.txt` and `ci-negative-test.txt` (j).

### Task 13 (FINAL): Verification gate

1. **CHANGELOG entry** for this spec in the existing `### Changed`.
2. **`scripts/gate.sh`:** steps 1 to 6 green, `verification/gate-run.txt` with date and branch.
3. **Step 7, Docs** and **step 8, Version**, recorded in `shape.md`; the version stays 0.0.1.
4. **Step 9, the retrospective** from the shipped diff. Expected proposals, verified against what ships: `base/process/verification-gate.md` (the `.gitignore` sentence; explicit config flags and the root `uv.toml`), `base/python/toolchain.md` (the tool steps' command lines, the refusal, `addopts`), `base/python/events.md` (softened), `base/python/models.md` (a validator calling a zone's code).
5. **Present and file:** AskUserQuestion, multi-select; the approved ones revise patchbay-standards#27 in place; numbers or `declined by owner, <date>` in `shape.md`; `Proposals sent upstream:` recorded.
6. **Rerun the gate and overwrite `gate-run.txt`,** since step 5 edits `shape.md`.
7. **Stop and print `git status --short`.** Retrospective edits are listed apart.

## Critical files

- `scripts/gate.sh`, `scripts/gate-negative-tests.sh`, `pyproject.toml` (`addopts` and its comment, the header)
- `src/patchbay/events.py`, `tests/unit/test_events.py`
- `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `.claude/commands/agent-os/shape-spec.md`
- Never edited: `agent-os/standards/base/`, the `base:` section of `index.yml`, `scripts/sync-standards.sh`, `.github/workflows/gate.yml`, the reviewed spec's folder

## Verification

- `scripts/gate.sh` exits 0 after each task and at the end; `gate-run.txt` is the last run.
- `probes.txt` reproduces the findings and shows each flag holding.
- `gate-negative-tests.txt` and `ci-negative-test.txt` each end on 0 unexpected.
- Every row of the mutation table comes back `UNEXPECTED`.
- `gate-sh-diff.txt` holds only the allowed hunks and the one named deviation.

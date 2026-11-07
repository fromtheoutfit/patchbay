# Gate revision after the review of PR 9

## Context

The owner's review of PR 9 (head `6adf50e`) found 9 issues in the gate spec of #5–#7. Findings 1,
2 and 5 were reproduced in scratch repos.

- **Correctness:**
  1. An ignored `conftest.py` is still imported despite `--ignore`.
  2. The root guard compares paths as strings, so it fails on macOS when the path is typed in a
     different case.
  3. `exclude_gitignore` makes mypy skip tracked files that `.gitignore` matches, a regression.
  4. mypy misses `.git/info/exclude` in a linked worktree.
  5. `listed` lost `sort -u`, so a conflicted file is listed up to 3 times.
  6. git errors are swallowed in process substitution.
- **Design:**
  7. Three separate ignore mechanisms, each leaking differently.
- **Smaller:**
  8. The harness header promises text on a passing `run`.
  9. The `--ignore` argument list can grow without bound.

This spec fixes all nine in a new spec folder on the same branch, so PR 9 carries the fix. The
PR 3 and PR 4 revisions set that precedent. No stage, commit or push by the agent.

## Shaping answers (owner, 2026-11-07)

- **Scope:** all 9, new folder `agent-os/specs/2026-11-07-<HHMM>-gate-revision-after-pr-9-review/`.
- **Finding 7's design:**
  - ruff and mypy get git's list (`listed`, `*.py`/`*.pyi`) as explicit paths, each checked by
    `present`. `exclude_gitignore` goes.
  - pytest keeps walking `testpaths`, but step 5 first refuses any git-ignored `.py` under
    `tests/`, conftest included and `__pycache__/` aside. It also refuses an ignored root
    `conftest.py`, which pytest loads too. No `--ignore` arguments.
  - This settles 1, 3, 4 and 9.
- **Skeleton (2, 5, 6):** fix here, recorded as a deviation from the sibling until the sync, and
  proposed upstream. `sync-standards.sh:97` (finding 2) is only proposed, since that file is
  synced.
- **Upstream:** #20's body is edited in place so it reads true on its own, with a
  "Revised 2026-11-07" paragraph at the top:
  - withdraw proposal 2;
  - revise proposals 3 and 4 against the revised gate;
  - add the skeleton and sync proposals (findings 2, 5, 6) and the toolchain command-line forms.

  One issue for one PR's work, no attribution, after the owner approves at the retrospective.
- **Visuals:** none.
- **References:** the review comment; the PR 4 revision (its dispositions table); the sibling's
  `gate.sh` and harness at `11ceffd`; the first spec's `verification/`.
- **Product:** no change.
- **Standards:** core `base/python/toolchain`; feature-specific `process/verification-gate`,
  `process/standards-retrospective`, `process/ownership` and `process/standards-sync`, snapshotted
  at `11ceffd`.

## Task 1: Save spec documentation

- **`plan.md`:** this plan, plus a dispositions table (# / finding / disposition).
- **`shape.md`:**
  - First Decision: the review is the scope, answered in a new folder.
  - The answers above.
  - The skeleton deviation.
  - The pytest guard, a pattern no standard covers, decided at shaping.
- **`standards.md`:** the five standards verbatim.
- **`references.md`.**
- **The first spec's `shape.md`:** one pointer line naming this revision.

## Task 2: Probes, before any gate edit (`verification/probes.txt`)

Run on scratch exports of the tree, at the pins, each setup shown before its result:

1. **ruff 0.17.4 given explicit paths:**
   - a force-added file `.gitignore` matches (`src/patchbay/lib/codec.py`) is checked;
   - `tests/**` per-file-ignores still apply;
   - `--` ends the options.
2. **mypy 2.4.1 given explicit files:**
   - module names match the `files = [...]` walk (`patchbay`, `test_version`);
   - a tracked+ignored file is checked.
3. **pytest 9.2.0:**
   - finding 1 reproduced: an ignored `tests/x/conftest.py` raising is imported under `--ignore`;
   - an ignored root `conftest.py` is loaded too;
   - a deselecting conftest turns a failing run into exit 0.
4. **git 2.54:**
   - an index with stages 1–3 for one path lists it 3× through `ls-files --cached`, and once
     after `sort -zu`;
   - `git rev-parse --show-cdup` is empty at the top when the path is typed in another case, while
     `pwd -P` keeps that case (bash 3.2);
   - `git ls-files` fails on a corrupt index;
   - a sentinel record after `sort -zu &&` is absent then, under `pipefail` inherited by the
     process substitution.

If a probe contradicts the design, stop and bring it to the owner.

## Task 3: The skeleton (findings 2, 5, 6) — `scripts/gate.sh`

- **Root guard (2):**
  `cdup=$(git rev-parse --show-cdup 2>/dev/null) && [ -z "$cdup" ] || fail 1/6 "not a git work tree rooted at $root; …"`.
  No path comparison remains.
- **`listed` (5, 6):** `git ls-files -z … -- "$@" | LC_ALL=C sort -zu && printf '\0'`. It is
  unique, and ends in one empty record only when git listed. Readers stop at the empty record and
  fail the step by name without it: "git could not list the files under scripts/ (see above)".
- **Header:** the exit and listing paragraphs say all of the above.

## Task 4: Steps 2–5 read git's list (findings 1, 3, 4, 7, 9) — `scripts/gate.sh`, `pyproject.toml`

- **Step 2:**
  - read `listed .`, keep `*.py`/`*.pyi`, each `present 2/6`, into `py`;
  - fail by name if git lists none;
  - then `uv sync --locked`, then `uv run --locked ruff format --check -- "${py[@]}"`.
- **Step 3:** `uv run --locked ruff check -- "${py[@]}"`.
- **Step 4:** read `listed src tests`, keep `*.py`/`*.pyi`, run `uv run --locked mypy -- "${src[@]}"`.
- **Step 5:**
  - read `git ls-files -z --others --ignored --exclude-standard -- tests conftest.py && printf '\0'`;
  - any `*.py` not under `__pycache__/` fails the step by name: "<path> is a Python file git
    ignores, which pytest would read; remove it or stop ignoring it";
  - then bare `uv run --locked pytest`.
- **`pyproject.toml`:**
  - `[tool.mypy]` loses `exclude_gitignore` and its comment;
  - `files` is noted as what a bare run walks, while the gate passes git's list.

## Task 5: The harness (finding 8 and the cases) — `scripts/gate-negative-tests.sh`

**New helper `times <n> <line>`:** the last run's output holds that exact line exactly n times;
anything else is `UNEXPECTED`.

**Finding 8:** the header says a passing run names its lines through `check` (as j's `replay`
does) or `times`, not `run`.

**g (step 1), new cases:**

- the copy run through its path in another case passes, exit 0. The gate at `6adf50e` fails step 1
  on it (the bug as it was). Skipped by name on a case-sensitive file system.
- a three-way-conflicted `scripts/conflict.sh` (index stages 1–3) passes with
  `times 1 'ok   scripts/conflict.sh'`. At `6adf50e` it shows `times 3`.
- a corrupt `.git/index` fails step 1 with "git could not list…". At `6adf50e` it shows "git lists
  no file".

**Shim `git` on `PATH`:** fails the listing call of step 2 (`-- .`), step 4 (`-- src tests`) or
step 5 (`--ignored`), so each fails its step by name and the step after is never reached.

**p (steps 2–4), rewritten:**

- an ignored `src/patchbay/local_settings.py` passes;
- force-added, step 2 names it, where before the gap passed;
- force-added and clean but for a type error (k's content), step 4 names it;
- **pw**, a linked worktree (`git worktree add`, after one commit): a module ignored only through
  `.git/info/exclude` passes there. The gate at `6adf50e` fails step 4 on it (finding 4).

**q (step 5), rewritten:**

- an ignored failing `tests/unit/test_local.py` is refused by name at step 5;
- an ignored `tests/unit/conftest.py` that deselects a tracked failing test is refused. The gate at
  `6adf50e` passes on it (finding 1, exit 0);
- an ignored root `conftest.py` is refused.

**The rest:** every other case is rerun unchanged.

## Task 6: Docs

- **`README.md`, `CLAUDE.md`, `shape-spec.md`'s gate task:** steps 2–5's wording (git's list to
  ruff and mypy; pytest guarded), and the root guard.
- **`gate.sh` and harness headers:** read against the code.
- **`CHANGELOG.md`:**
  - a Changed entry for this revision;
  - the fifth spec's bullets that name `exclude_gitignore` and `--ignore` rewritten to the tree.
- **PR 9's body:** rewritten to the shipped gate, no attribution.

## Task 7: Rerun everything after the last gate-file edit

- **`verification/gate-negative-tests.txt`:** one run, ending `0 unexpected`, `harness exit=0`.
- **`verification/ci-negative-test.txt`:** j. It records hosted run 42294437943 (`6adf50e`,
  success) as the pre-revision run.
- **`verification/reason-assertion-mutations.txt`:** each mutation must come back `UNEXPECTED`:
  - M1, the root guard back to a string comparison: the case-path run;
  - M2, `sort -z`: `times 1`;
  - M3, the sentinel check removed: the corrupt-index case;
  - M4, step 5's guard removed: the deselecting conftest.
- **`verification/gate-sh-diff.txt`:** against the sibling at `11ceffd`. The header names the
  skeleton hunks (guard, `listed`, the sentinel check) as this spec's deviation, pending upstream.

## Task N (FINAL): Verification gate

1. `scripts/gate.sh`, steps 1–6, green.
2. **Docs (7):** as Task 6, and `base/python/toolchain.md` re-read against the tree.
3. **Version (8):** the `[Unreleased]` entries. No bump.
4. **Retrospective (9):**
   - Find the proposals from the shipped diff: the skeleton (2, 5, 6), `sync-standards.sh:97`,
     the pytest guard form replacing proposal 2, the revised 3 and 4 with the command-line forms,
     and proposal 1's rationale restated (patchbay no longer uses the second form for ruff and
     mypy).
   - Present them to the owner with AskUserQuestion, at most 3 to a question plus "None of these".
   - Edit #20's body in place with the "Revised 2026-11-07" paragraph, no attribution. Mark
     declined ones `declined by owner, <date>`.
   - Record `Proposals sent upstream:`.

**Last act:** `scripts/gate.sh` → `verification/gate-run.txt` (date and branch first, `exit=0`
last). Then print `git status --short`.

## Dispositions

The owner's review of PR 9 (comment of 2026-11-06 on fromtheoutfit/patchbay#9, at `6adf50e`).

| # | Finding | Disposition |
| --- | --- | --- |
| 1 | an ignored `conftest.py` is imported under `--ignore` | step 5 refuses any ignored `.py` under `tests/` and an ignored root `conftest.py`; no `--ignore` (q) |
| 2 | the root guard compares paths as strings | `git rev-parse --show-cdup` empty; skeleton deviation, proposed upstream with `sync-standards.sh:97` (g) |
| 3 | `exclude_gitignore` skips a tracked file `.gitignore` matches | the key goes; ruff and mypy get git's list (p) |
| 4 | mypy misses `info/exclude` in a linked worktree | git decides the list (pw) |
| 5 | `listed` lists a conflicted path up to 3 times | `sort -zu`; skeleton deviation, proposed upstream (g, `times`) |
| 6 | git errors in process substitution are swallowed | `listed` ends in a sentinel record; a reader without it fails by name (g; the shim for steps 2, 4, 5) |
| 7 | three ignore mechanisms, each leaking | git's list to ruff and mypy; pytest guarded by a refusal |
| 8 | the header promises text on a passing `run` | header names `check` and `times`; `times` added |
| 9 | `--ignore` arguments grow without bound | gone with finding 7 |

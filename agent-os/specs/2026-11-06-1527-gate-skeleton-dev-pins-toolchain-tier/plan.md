# Gate spec: skeleton and harness (#5), dev tool pins as gate files (#6), toolchain tier and present-and-file (#7)

## Context

Base pin is `11ceffd` (sync `ae58aac`, PR #8). Three open issues are the "after the sync" work it
asks of this repository's gate files, so one gate spec carries them:

- **#5**: `scripts/gate.sh` takes the shared skeleton from `patchbay-standards` at `11ceffd`, and
  `scripts/gate-negative-tests.sh` takes the harness shape. #5's last section asks whether gate
  steps 2–5 meet the listing rule, step by step.
- **#6**: the dev group's tool pins become gate files.
- **#7**: Step 5a lists `base/python/toolchain`, tech-stack cites it, pre-commit runs `--locked`,
  the `--strict-config` comment is fixed, and the present-and-file step joins the gate task and the
  `shape.md` template.

Branch: `feature/5-gate-spec-2-take-patchbay-standards-pr-11s-gate-skeleton-and-harness-changes`.
No stage, commit, push or PR by the agent.

## Shaping answers (owner, 2026-11-06)

All eight were the recommended option.

- **Scope:** the three parts plus the stale text found against `11ceffd`. That covers #6 item 4
  (`[tool.uv]` comment, README line 47), CLAUDE.md and README routing base changes "as a pull
  request", exit 2 on a failed `cd` and the root guard missing from both, the
  `.pre-commit-config.yaml` header commands, and a CHANGELOG line for the 11ceffd sync.
- **Visuals:** none.
- **References:** the sibling at `11ceffd`:
  - its `scripts/gate.sh`, `scripts/gate-negative-tests.sh`, `shape-spec.md` and `CLAUDE.md`;
  - gate spec 2 (`2026-11-05-2019`, `gate-sh-diff.txt`) and gate spec 3 (`2026-11-06-0721`);
  - the ninth and tenth specs (`1205`, `1244`: present-and-file, `only`, one run per transcript);
  - issues #17 and #19 there;
  - this repo's gate, its harness and the last spec's transcripts.
- **Product:** no product decision changes. The tech-stack introduction cites the standard.
- **Standards:** six in total.
  - Core (Step 5a, the first spec here to use it): `base/python/toolchain`.
  - Feature-specific: `process/verification-gate`, `process/standards-sync`,
    `process/standards-retrospective`, `process/ownership`, `process/standards-index`.
- **Steps 4–5 and the listing rule:**
  - `exclude_gitignore = true` goes in `[tool.mypy]`.
  - Step 5 passes pytest one `--ignore=<path>` for each path git ignores under `tests/`.
  - ruff already honours `.gitignore`, which the probe confirms.
- **Dev pins:** ruff, mypy and pytest are the gate's. hypothesis and pre-commit are the package's.
- **FAIL line:** the sibling's form. Each failing gate run's expected text ends with its
  `FAIL  step N/M: <reason>` line, and `later` holds the run to no later step banner.

## Task 1: Save spec documentation

Create `agent-os/specs/2026-11-06-<HHMM from date>-gate-skeleton-dev-pins-toolchain-tier/`
containing:

- **`plan.md`:** this plan.
- **`shape.md`:**
  - **First Decision:** cites #5, #6 and #7, and says one gate spec carries them. All three are
    "after the sync" work on this repository's gate files, read against the base standards now at
    `11ceffd`.
  - **Core Architecture:** `base/python/toolchain`.
  - **Decisions:** the shaping answers above.
  - **Recorded as a pattern no standard covers yet, approved at shaping:** the pytest `--ignore`
    form of the listing rule. It goes to the retrospective as a proposal.
- **`standards.md`:** the six standards verbatim at `11ceffd`, toolchain first as core.
- **`references.md`:** the references above.
- **`verification/`:** see the tasks below.

## Task 2: Probes (before any gate edit), `verification/probes.txt`

Run on an export of the tree (git's list) in the scratchpad, with the tools at their pins. Per the
retrospective's probe rule, the cases must tell the competing claims apart, and the setup is shown
before any result is read.

1. **ruff 0.17.4.** An ignored `src/patchbay/local_settings.py` (a real `.gitignore` pattern) with
   format, lint and type faults:
   - `ruff check --show-files .` and `ruff format --check .` skip it;
   - `--no-respect-gitignore` sees it;
   - force-added, ruff sees it.
2. **mypy 2.4.1.** The same file:
   - bare `mypy` checks it;
   - `--exclude-gitignore` skips it;
   - a file ignored only through a global excludes file (`GIT_CONFIG_GLOBAL` → `core.excludesFile`)
     is skipped by git but checked by mypy. This records the limit read from
     `modulefinder.find_gitignores`.
3. **pytest 9.2.0.** An ignored `tests/unit/test_local.py`, added to the copy's `.gitignore`, holding
   a failing test:
   - bare `pytest` collects it;
   - `--ignore` from `git ls-files -z --others --ignored --exclude-standard --directory -- tests`
     does not;
   - the `__pycache__/` directories in that list are harmless.
4. **uv 0.13.7, for the `[tool.uv]` comment (#6 item 4).** With `required-version = "==0.1.0"`:
   - `uv sync --locked`, `uv run --locked`, `uv lock` and `uv version` refuse;
   - `uv --version` and `uv self version` run.
5. **pytest `--strict-config`, for the comment (#7).** An unknown key in
   `[tool.pytest.ini_options]` gives exit 4 with the flag, and a warning with exit 0 without it.

If a probe contradicts the plan (for example, ruff does not skip the file), stop and bring it back
to the owner before editing.

## Task 3 (part 1, #5): `scripts/gate.sh`

Take the skeleton from the sibling's `gate.sh` at `11ceffd` word for word:

- **Header:**
  - the exit paragraph, "2 on usage, or when the repository root cannot be entered, each said on
    stderr with no step run";
  - the listing paragraph (rule cited, one `-z` call, root guard, symlink to nothing).
- **The guarded `cd`:**
  `cd "$(dirname "$0")/.." || { echo "gate: cannot enter the repository root, …; not run as the gate" >&2; exit 2; }`.
- **Helpers:** `step`, `fail`, `listed` (`git ls-files -z --cached --others --exclude-standard -- "$@" | LC_ALL=C sort -z`)
  and `present` (a symlink to nothing named as one, else "tracked but missing from the disk").
- **Step 1:**
  - `root=$(pwd -P)`; `top` must equal it, else `fail 1/6 "not a git work tree rooted at $root; the gate lists files with git ls-files"`;
  - `present 1/6 "$f"`;
  - `done < <(listed scripts)`. `-c core.quotePath=false` and the two-call listing go.

Steps 2–5 follow the listing rule:

- **Steps 2–3 (ruff):** unchanged. ruff reads `.gitignore` and is given `.`. The header says so.
- **Step 4 (mypy):** unchanged in the script, since `[tool.mypy] exclude_gitignore = true` does the
  work (below). The banner adds "skipping what .gitignore ignores".
- **Step 5 (pytest):**
  - collect `--ignore=<p>` from
    `git ls-files -z --others --ignored --exclude-standard --directory -- tests` into an array;
  - run `uv run --locked pytest ${ign[@]+"${ign[@]}"}`. That form is safe for an empty array under
    `set -u` on macOS bash 3.2; check which bash `env` finds.
  - The helper stays out of the skeleton, inline in step 5.
- **The header's needs paragraph** names what each step reads.

`pyproject.toml [tool.mypy]` gains `exclude_gitignore = true`. Its comment names the rule, the key,
and the global-excludes limit from probe 2. `[tool.mypy]` is a gate file, and this is the gate spec.

## Task 4 (part 1, #5): `scripts/gate-negative-tests.sh`

Take the sibling's harness shape, keeping this repository's case letters and its `<case>/patchbay`
layout.

**Helpers:**

- `run <case> <status> [<text>] <cmd...>` (a non-zero status requires text), with `says`, `later`,
  `check` and `shown`.
- `only <line>...`, the exclusive check, adapted to step 6. The lines printed under
  `check base standards against`, indented two spaces, must be exactly these, in order: the
  missing/extra/changed entries, then the `index` and `script` lines.

**Fixes:**

- Every setup step in a case ends in `|| die`. This covers `rm .bak`, `rm -rf .git`, `git rm`,
  `git checkout`, `rm notes.txt` and the rest.
- The header's fixture sentence is corrected. A local clone shares the sibling's objects, so it
  holds the pin whichever ref reaches it, and `--check` reads the pin from `.version`
  (standards-sync.md).

**One run per transcript (#19):** the header says each kept transcript holds one run and ends on
its count. An earlier run kept as evidence goes in a file of its own.

**Every failing run names its lines.** The tool's own line naming the file comes first, then the
gate's `FAIL  step N/M: …` last. Exact tool lines are taken from the last spec's transcripts:

- ruff `Would reformat:` (h);
- `F401` (i);
- `no-any-return` (k);
- `FAILED tests/unit/…` (l);
- m's three runs;
- uv's stale-lock line (n) and its version line (o);
- step 6's drift lines (b, c, e, f);
- d's sync refusal, for both its runs.

`only` is held on b, c, e and f.

**New and extended cases:**

- **g (step 1):**
  - a tracked `scripts/dangling.sh` symlink to nothing is named as one;
  - the copy without `.git` inside an outer repository (`go/copy`) is refused at step 1, and no
    file is listed against the outer repository.
  - `scripts/gate.sh` at `92cd215` (main before this spec) is also shown on both. On the nested copy
    it passes step 1 and fails step 6 for the wrong reason. On the symlink it says "missing from
    the disk".
- **u:** the `cd` failure exits 2 saying so, with no banner. It runs as `bash -c "$(cat gate.sh)"`
  with `$0` under a missing directory.
- **p (steps 2–4 listing):**
  - an ignored `src/patchbay/local_settings.py` (unformatted, an unused import, a type error)
    passes the whole gate, exit 0;
  - `ruff check --no-respect-gitignore .` and `mypy --no-exclude-gitignore` in the copy each name
    it;
  - force-added, step 2 fails naming it, and 3/6 is never printed.
- **q (step 5 listing):**
  - the copy's `.gitignore` gains `tests/unit/test_local.py`, a failing test, formatted, lint-clean
    and typed: the gate passes;
  - bare `uv run --locked pytest` names it;
  - force-added, step 5 fails naming it, and 6/6 is never printed.
- **j:** the replay asserts its text, `FAIL  step 1/6: scripts/broken.sh does not parse` then
  `job: FAILED at step 6`.

**`verification/reason-assertion-mutations.txt`:** run on a scratch copy of the tree with the
sibling linked beside it.

- M1, the root guard reverted to bare `rev-parse`: g's nested case comes back `UNEXPECTED`.
- M2, `present`'s symlink branch removed: g's symlink case comes back `UNEXPECTED`.
- M3, b breaking a second file: `only` comes back `UNEXPECTED`.

The mypy key and pytest's `--ignore` are shown to matter by p's and q's own runs.

**Checkpoint:** the gate is green, and `scripts/gate-negative-tests.sh` reports 0 unexpected.

## Task 5 (part 2, #6): the dev tool pins are gate files

- **`pyproject.toml` header:**
  - the `[tool.*]` sections, plus the tool pins in `[dependency-groups] dev` (ruff, mypy, pytest)
    with what `uv.lock` resolves for them, are the gate's;
  - `[project]`, `[build-system]` and the rest of the dev group (hypothesis, a test library run
    inside pytest, and pre-commit, run by no gate step) are the package's and change in any spec,
    as a Decision.
- **The `[dependency-groups]` comment** says the same, per entry. Every entry stays exact, with its
  date.
- **The `[tool.uv]` comment:** "any other uv refuses to run here" becomes "refuses every command
  that reads this project's settings (`uv lock`, `uv sync`, `uv run`, …)", citing probe 4. The
  conclusion is unchanged, since the gate's first uv command is `uv sync --locked`.
- **`CLAUDE.md`'s gate-file list** names the tool pins and what `uv.lock` resolves for them.
  hypothesis and pre-commit are named as the package's.

**Checkpoint:** the gate is green.

## Task 6 (part 3, #7): the toolchain tier, pre-commit `--locked`, present-and-file

**`.claude/commands/agent-os/shape-spec.md`** (the gate task is a gate file):

- **Step 5 bullet (line 101):** a base proposal is presented to the owner. Approved ones are filed
  as one issue on `patchbay-standards`, whose spec lands them as a PR.
- **Step 5a:** lists `base/python/toolchain`, included in every spec without asking, its full text
  in `standards.md`. Only the one that exists is named.
- **Step 5b:** "(in addition to the core tier above)", leaving Step 5a's standards out of the list.
  The prompt says the tier holds toolchain.
- **Gate task:**
  - step 1 adds "at a work-tree top that is the repository root";
  - steps 4 and 5 name their listing;
  - the closing paragraph gives exit 1 or 2 as the script now words it;
  - step 9 gains the present-and-file step, from the sibling's text adapted to steps 7–9 and
    `agent-os/standards/base/…`, with `Proposals sent upstream:` always recorded;
  - the Step 9 "Plan complete" text says each proposal is filed upstream or declined by the owner.
- **`shape.md` template:**
  - Core Architecture and "Core (always applied)" name toolchain;
  - `Proposals sent upstream:` gets its four forms before `### Standards retrospective (proposed,
    base)`;
  - that paragraph and its entry line end in the issue or `declined by owner, <date>`.

**The other files:**

- **`agent-os/product/tech-stack.md` introduction:** cites
  `agent-os/standards/base/python/toolchain.md`.
- **`README.md`:** the two pre-commit commands take `--locked`.
- **`.pre-commit-config.yaml` header:** its two commands take `--locked` too.
- **`pyproject.toml` `--strict-config` comment:** "as the gate standard asks of a rule-set config"
  goes. It cites the rule that exists instead: toolchain.md "pytest and hypothesis", an unknown key
  fails rather than warns (probe 5).

**Checkpoint:** the gate is green.

## Task 7: Docs fixes (scope answer)

- **`CLAUDE.md`:**
  - the Ownership route (lines 40–42) and the Specs route (lines 78–80) follow the
    owner → issue → PR route;
  - the gate description gives exit 1/2, the root guard, and the mypy and pytest listing;
  - "Either way it records `Proposals sent upstream:`, `none` when there is no base proposal".
- **`README.md`:**
  - Layout's `pyproject.toml` bullet and the Install paragraph cover the gate pins, the package's
    entries, and the narrowed uv claim;
  - The gate: exit 2 on a failed `cd`, step 1's root guard, and steps 4–5's listing;
  - Syncing: the route.

## Task 8: Rerun the whole harness, and the diff against the sibling

After the last gate-file edit:

- **`scripts/gate-negative-tests.sh`** → `verification/gate-negative-tests.txt`.
  - It holds one run: a header with date, branch and what changed, the output, then
    `N runs, 0 unexpected` and `harness exit=0` last.
- **`scripts/gate-negative-tests.sh j`** → `verification/ci-negative-test.txt`.
  - The workflow is unchanged. The hosted run on the PR is its proof, recorded once it exists.
- **`verification/gate-sh-diff.txt`:** the header (the sibling's form), then
  `diff -u <(git -C ../patchbay-standards show 11ceffd:scripts/gate.sh) scripts/gate.sh`.
  - The header classifies every hunk: step lists, pins (the sibling's PYMARKDOWN block; here,
    pyproject), paths spelled from each root, N/M numbers, and banners and bodies.
  - The goal is no hunk beyond those. Anything else is named there and in `shape.md` Results.

## Task N (FINAL): Verification gate

1. `bash -n` on every shell script under `scripts/` as git lists them, at a work-tree top that is
   the repository root.
2. `uv sync --locked`, then `uv run --locked ruff format --check .`.
3. `uv run --locked ruff check .`.
4. `uv run --locked mypy` (strict, over `src/` and `tests/`, skipping what `.gitignore` ignores).
5. `uv run --locked pytest`, with `--ignore` for each path git ignores under `tests/`.
6. `scripts/sync-standards.sh --check` against `../patchbay-standards` at `11ceffd`.
7. **Docs:**
   - every changed file's header and pointers;
   - README and CLAUDE.md;
   - a search for "pull request" routes and "Proposals sent upstream";
   - `base/python/toolchain.md` read rule by rule against this tree (#7 item 3). A rule that reads
     false is a proposal, never an edit.
8. **Version:** `CHANGELOG.md` under `[Unreleased]`:
   - a Changed entry for this (fifth) spec;
   - a bullet for the sync `b3fc2fe` → `11ceffd` (`ae58aac`, PR #8);
   - the header's "a sync forward is recorded here as its own entry" reworded to say the next spec
     writes it, since the sync commit changes only the synced files (standards-sync.md).
   - No version bump.
9. **Standards retrospective, from the shipped diff.** It is the first here to present and file.
   - No project standard exists to edit, and `index.yml` is untouched.
   - Likely base proposals, decided from the diff:
     - verification-gate.md: the listing rule's `--ignore` form (git's ignored list given to a
       tool that walks a directory);
     - verification-gate.md: the global-excludes limit of a tool that reads `.gitignore` itself;
     - verification-gate.md: whether "a listed path missing from the disk" binds the tool form;
     - toolchain.md: `[tool.mypy] exclude_gitignore` and step 5's `--ignore`.
   - Present them with AskUserQuestion, multi-select: at most three to a question, each ending in
     "None of these".
   - File the approved ones as one issue with
     `gh issue create --repo fromtheoutfit/patchbay-standards`, no attribution:
     - one section per proposal with its verification pointer;
     - "Depends on" this branch;
     - Rules at the end;
     - titled a gate spec only if a sibling gate file must change.
   - Write the issue's number beside each, mark declined ones `declined by owner, <date>`, and
     record `Proposals sent upstream:`.
   - Retrospective edits are listed apart from the feature's.

Then, as the last act: `scripts/gate.sh` → `verification/gate-run.txt`, whose first line gives the
date and branch and whose last line is `exit=0`. Stop, and print `git status --short`.

## Not done by the agent

- No stage, commit, push or PR, and #5, #6 and #7 are not commented on or closed.
- The only GitHub write is the retrospective's issue, if the owner approves any proposal.
- `agent-os/standards/base/`, the `base:` section, `scripts/sync-standards.sh` and
  `.github/workflows/gate.yml` are not touched.

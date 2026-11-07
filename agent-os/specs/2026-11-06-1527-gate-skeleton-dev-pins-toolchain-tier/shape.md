# Gate spec: the skeleton and harness, the dev tool pins, the toolchain tier — Shaping Notes

Shaped 2026-11-06 in plan mode with this repository's customized `/agent-os:shape-spec`. The owner
answered the Step 1–5 questions and four design questions. Every answer was the recommended option.

## Core Architecture (Non-Negotiable)

- `base/python/toolchain` — one tool per job in a uv Python package, `pyproject.toml` the only
  config file, every tool run through `uv run --locked`, and the order of the gate's tool steps.
  Included without asking (Step 5a), its full text in `standards.md`. This spec is the one that
  puts it in Step 5a (#7), so it is the first to include it.

## Scope

The work the base standards at `11ceffd` ask of this repository's own gate files, after the sync
that brought them in (`ae58aac`, PR #8), recorded in three issues:

- **#5:** `scripts/gate.sh` takes the skeleton it shares with `patchbay-standards` (the guarded
  `cd`, `listed` and `present`, step 1's root guard, the exit contract as the standard words it);
  `scripts/gate-negative-tests.sh` takes the harness shape (every failing run names its lines, the
  gate's `FAIL` line last; every setup step `|| die`; the exclusive check; one run per transcript;
  the cases for a symlink to nothing, a copy nested in another repository and a failed `cd`). Its
  last section: whether each toolchain step meets the listing rule, answered step by step.
- **#6:** the dev group's tool pins are gate files: `pyproject.toml`'s header and `CLAUDE.md`'s
  gate-file list say so; hypothesis and pre-commit are classified; the `[tool.uv]` comment narrowed.
- **#7:** Step 5a lists `base/python/toolchain`; `tech-stack.md` cites it; pre-commit's two
  commands take `--locked`; the `--strict-config` comment names a rule that exists; the
  present-and-file step joins the gate task and the `shape.md` template.

Plus the stale text the same change touches, found reading the tree against `11ceffd` (below).
A `CHANGELOG.md` entry, the gate green, `verification/gate-run.txt` with the date and branch. No
stage, commit, push or PR by an agent.

## Shaping answers

- **Step 1, scope:** the three parts, plus the stale text found against `11ceffd`: #6 item 4 (the
  `[tool.uv]` comment and README line 47), `CLAUDE.md` and `README.md` sending a base change
  upstream "as a pull request", exit 2 on a failed `cd` and the root guard missing from both, the
  `.pre-commit-config.yaml` header's two commands, and a `CHANGELOG.md` line for the sync to
  `11ceffd`.
- **Step 2, visuals:** none.
- **Step 3, references:** `references.md`.
- **Step 4, product context:** no product decision changes; the introduction of
  `agent-os/product/tech-stack.md` cites the standard.
- **Step 5, standards:** `base/python/toolchain` as the core tier; `process/verification-gate`,
  `process/standards-sync`, `process/standards-retrospective`, `process/ownership` and
  `process/standards-index` feature-specific. Snapshot at `11ceffd` in `standards.md`.
- **Steps 4–5 and the listing rule** (owner): `exclude_gitignore = true` in `[tool.mypy]`; step 5
  passes pytest one `--ignore=<path>` for each path git ignores under `tests/`. Chosen over giving
  both tools git's list, and over recording the gap and changing no step.
- **The dev group** (owner): ruff, mypy and pytest are the gate's tool pins; hypothesis and
  pre-commit are the package's.
- **"FAIL as the last line"** (owner): the sibling's form. Each failing gate run's expected text
  ends with the gate's `FAIL  step N/M: <reason>` line, and `later` holds the run to no later step
  banner. The harness does not also assert it is the last line printed.

## Decisions

- **One gate spec carries #5, #6 and #7.** All three are "after the sync" work on this
  repository's gate files — `scripts/gate.sh`, `scripts/gate-negative-tests.sh`, the `[tool.*]`
  sections and dev tool pins of `pyproject.toml`, the gate task in `shape-spec.md` — and all three
  are read against the base standards now pinned at `11ceffd`. The gate's own files change only in
  a spec whose feature is the gate (`base/process/verification-gate.md`), so the three are one
  such spec rather than three that each reopen the same files.
- **The skeleton is the sibling's, word for word.** The header's exit and listing paragraphs, the
  guarded `cd`, the four helpers, step 1 and the closing line are copied from
  `patchbay-standards`' `scripts/gate.sh` at `11ceffd`, and `verification/gate-sh-diff.txt` shows
  what differs: only the step lists, the pins and the paths, or the hunk is named there.
- **The listing rule, step by step** (#5's last section; probes in `verification/probes.txt`):
  - Steps 2 and 3, ruff: the rule's second form. ruff reads `.gitignore` (`respect-gitignore`, on
    by default) and is given `.`, which git does not ignore. No change.
  - Step 4, mypy: walks `files = ["src", "tests"]` without reading `.gitignore`, so it did not meet
    the rule. `exclude_gitignore = true` in `[tool.mypy]` makes it the second form. mypy 2.4.1
    reads the `.gitignore` files from the work-tree top down and `.git/info/exclude`, not git's
    global excludes file; a file ignored only there is checked by mypy and not listed by git. The
    comment beside the key says so.
  - Step 5, pytest: reads no `.gitignore`. It is given `--ignore=<path>` for each path
    `git ls-files -z --others --ignored --exclude-standard --directory -- tests` lists, so git's
    own reading of the ignore rules decides, and `testpaths` and the collection rules stay
    pytest's. **A form the rule does not name**: the tool walks the directory, and git's list of
    what it ignores there is subtracted. Approved at shaping (owner) and recorded here before it is
    used, per the retrospective's ordering rule; it goes upstream in the retrospective.
  - A tracked file missing from the disk under `src/` or `tests/` is not refused by steps 2–5: the
    tools walk the disk, and the rule's second form asks only that they read `.gitignore` and be
    given no ignored path. Whether "a listed path missing from the disk fails the step" binds the
    tool forms is a question for the retrospective, not a change here.
- **A tracked file that `.gitignore` matches is a defect in the tree, not a case for the tools**
  (owner, 2026-11-06, asked after the probes). Probe 1 showed ruff skipping a force-added file
  that `.gitignore` still matches, though git lists it as tracked; probe 2 showed mypy's
  `exclude_gitignore` doing the same, and checking a file ignored only through git's global
  excludes file, which git and ruff skip. pytest's `--ignore` form gets the tracked case right: a
  tracked file drops out of git's ignored list. ruff and mypy keep the rule's second form as
  planned. Case p asserts the gap as it stands (force-added, steps 2–4 still pass), so a change
  in it is seen. Its "read once git lists it" half takes the pattern out of `.gitignore` instead
  of force-adding. mypy's global-excludes behaviour is a documented limit, in the comment beside
  the key, not a hole. The retrospective proposes that the listing step refuse the state:
  `git ls-files -ci --exclude-standard` listing anything fails the step by name. Neither this tree
  nor `patchbay-standards` lists anything there today.
- **The exclusive check, adapted to step 6.** `only` in `patchbay-standards` holds the entries
  `check-index.sh` lists under its FAIL lines. Here the gate's entries are step 6's drift report:
  the lines `sync-standards.sh --check` prints under `check base standards against`, indented two
  spaces (each `missing`, `extra` or `changed` entry, then the `index` and `script` lines). `only`
  holds them to exactly the lines a case names, in order, on b, c, e and f, the cases that claim one
  drift.
- **The dev group's entries, classified** (owner). The tools the gate runs, ruff, mypy and pytest,
  with what `uv.lock` resolves for them, are gate files (`verification-gate.md`, "Pinned").
  hypothesis is a test library pytest runs and pre-commit is run by no gate step: both are the
  package's, pinned exactly with their dates as toolchain.md's "Dependencies" asks of every entry,
  and changed in any spec as a Decision there.
- **`CHANGELOG.md` records the sync to `11ceffd`.** Its header says a sync forward is recorded as
  its own entry, but the sync commit changes nothing but the synced files
  (`base/process/standards-sync.md`, "Pinned, not tracking"), so `ae58aac` added none. This spec's
  entry carries a line for it, and the header says the spec after a sync writes it.

## Context

- **Visuals:** None.
- **References:** `references.md`.
- **Product alignment:** `agent-os/product/tech-stack.md`'s introduction cites
  `agent-os/standards/base/python/toolchain.md`; `mission.md` untouched.

## Standards Applied

**Core (always applied):**
- `base/python/toolchain` — Step 5a; its rules are read against this tree in the Docs step (#7
  item 3), and steps 4 and 5 change how two of its tools are run.

**Feature-specific:**
- `base/process/verification-gate` — the gate's own spec: the skeleton, the exit contract, the
  listing rule, the harness shape, the tool pins as gate files; every changed step carries its
  negative test.
- `base/process/standards-sync` — the harness fixture's wording (a local clone holds the pin
  whichever ref reaches it); the sync writes nothing under `.claude/commands/`, so the
  present-and-file step is this spec's.
- `base/process/standards-retrospective` — "Base proposals go to the owner, then upstream", which
  the gate task gains and this spec's own retrospective is the first here to follow.
- `base/process/ownership` — no stage, commit, push or PR; the retrospective's issue carries no
  attribution.
- `base/process/standards-index` — this repository has no project standards; the `base:` section
  is the sync's and is not touched.

## Verification Gate

Spec is not complete until `scripts/gate.sh` passes — `bash -n` on every shell script under
`scripts/` as git lists them, at a work-tree top that is the repository root; `uv sync --locked`,
then `uv run --locked ruff format --check .`, `uv run --locked ruff check .`, `uv run --locked
mypy` and `uv run --locked pytest` under `pyproject.toml`'s `[tool.*]` rule set and `uv.lock`'s
pins, each reading only the files git lists; and `scripts/sync-standards.sh --check` against
`../patchbay-standards` at the commit in `agent-os/standards/base/.version` — and the three
judgment steps are recorded, in this order: Docs, Version, then the standards retrospective below.

**Results (2026-11-06):** exit 0 on branch
`feature/5-gate-spec-2-take-patchbay-standards-pr-11s-gate-skeleton-and-harness-changes`,
`verification/gate-run.txt`, the last thing done before hand-over. The gate was also green after
each part (the skeleton and harness, the dev pins, the toolchain tier and the docs). Every gate
file changed, so every negative test was rerun after the last edit to them:

- `verification/gate-negative-tests.txt`: one run, every test but j, `53 runs, 0 unexpected`,
  `harness exit=0`;
- `verification/ci-negative-test.txt`: j, the job passing on a clean copy and failing at the
  gate's step on a broken one, `3 runs, 0 unexpected`. The workflow is unchanged; the hosted run
  on the pull request is its proof once it exists;
- `verification/reason-assertion-mutations.txt`: the root guard reverted, `present`'s symlink
  branch removed and b given a second drift, each `UNEXPECTED` with the status still as expected;
- `verification/probes.txt`: ruff, mypy, pytest and uv at their pins, before any gate edit;
- `verification/gate-sh-diff.txt`: the diff against the sibling's `scripts/gate.sh` at `11ceffd`.
  Every hunk is a step list, a pin or a path spelled from its root; the skeleton is byte-identical
  but for the N/M numbers. Nothing differs beyond step lists, pins and paths.

Revised after the review of PR 9 in `agent-os/specs/2026-11-07-0711-gate-revision-after-pr-9-review/`,
which replaces the listing Decisions above for steps 2–5 (`exclude_gitignore` and pytest's
`--ignore` are gone) and fixes the skeleton; the transcripts here are the first round's.

**Docs (step 7):**

- **Headers of the changed files:** `scripts/gate.sh` (the exit contract, the listing paragraph
  with steps 2–5's forms, the needs), `scripts/gate-negative-tests.sh` (the run/check/only shape,
  the fixture's wording, one run per transcript, the test list), `pyproject.toml` (the header's two
  kinds of entry, the dev group's comment, `[tool.uv]`, `[tool.mypy]`'s new key, `--strict-config`)
  and `.pre-commit-config.yaml`, each read against the code beside it.
- **`README.md` and `CLAUDE.md`:** the exit statuses, step 1's root guard, steps 4–5's listing, the
  gate's tool pins and the package's entries, uv's refusal narrowed, the pre-commit commands under
  `--locked`, a base proposal's route, and `Proposals sent upstream:`. Searched: no route sends a
  base change as a pull request first, no unlocked `uv run <tool>`, no "refuses to run here", no
  "none yet" or "empty for now" for Step 5a.
- **`agent-os/product/tech-stack.md`:** its introduction cites the toolchain standard.
- **`base/python/toolchain.md`, rule by rule against this tree (#7 item 3).** Every rule reads true
  here after this spec, the pre-commit commands the last that did not before it. Two read
  incomplete rather than false. "mypy" does not name `exclude_gitignore`. "The gate's tool steps"
  names `pytest` bare, where step 5 now gives it `--ignore` arguments. Both are proposals below,
  not edits.
- **The other synced standards that name what changed:** `verification-gate.md` ("One script",
  "Pinned", the harness bullet, "In a consuming project") and `standards-sync.md` (the fixture)
  read true of the shipped files, but for the listing rule's forms (proposals below).
- **Line widths:** no prose line this spec wrote is over 100 columns. The longer lines are code:
  `scripts/gate.sh`'s banners and `fail` calls, the skeleton's as the sibling has them, and the
  harness's case headers. The rest predate this spec or are copied verbatim: `plan.md` is the
  approved plan and `standards.md` the standards.

**Version (step 8):** under `[Unreleased]`, `### Changed`, in `CHANGELOG.md`: the fifth spec's
entry, and a line for the sync to `11ceffd` (`ae58aac`, PR #8), which had none. The header now
says the spec after a sync writes its entry. No version bump; no release is cut.

## Standards Retrospective

Step 9, always last, from the shipped diff against `92cd215`. The first retrospective here to
follow "Base proposals go to the owner, then upstream".

1. *A pattern no standard covers?* One.
   - Step 5's form of the listing rule, git's ignored list given as `--ignore` to a tool that walks
     a directory. Approved at shaping and recorded as a Decision before it was used; proposed below
     (2, and 4 for the toolchain's wording).
   - The rest is the sibling's, already upstream:
     - the exclusive check (`only`), adapted here to step 6's drift report, is the harness half of
       fromtheoutfit/patchbay-standards#17 proposal 5;
     - one run per transcript is #19;
     - the mutations file is #17 proposal 2.

     None is proposed again.
2. *A standard wrong or stale?* Four, all base, all proposals.
   - The listing rule's second form does not read what git lists when a tracked file is matched by
     `.gitignore` (probes 1–2, test p). The owner's call: refuse that state rather than make the
     tools robust to it (1).
   - The missing-file clause does not say which form it binds (3).
   - `toolchain.md`'s "mypy" and "The gate's tool steps" do not name how steps 4–5 read what git
     lists (4).
   - `standards-sync.md`'s "What the sync writes, and nothing else" leaves the project's
     `CHANGELOG.md` out, so the sync to `11ceffd` (`ae58aac`) recorded nothing there, though this
     repository's `CHANGELOG.md` header said every sync forward gets its own entry; this spec
     added the line afterwards (5, the owner's, after hand-over).
   - `verification-gate.md`'s "A key the tool does not know is not refused" is wrong of pytest
     under `--strict-config` (probe 5). It is already #17 proposal 3, so it is not proposed again.
3. *A deliberate deviation?*
   - **Deviation, not a standard change:** the harness's `cd` to the repository root ends in
     `|| die`, where the sibling's does not. The standard asks that a setup step that fails stop
     the harness by name, so this follows it; it differs only from the sibling.
   - **Deviation, not a standard change:** the probes were run before any gate edit, as planned.
     Section 5's printed lines did not show pytest's error, so it was rerun after the edits on a
     tree whose `[tool.pytest.ini_options]` differs only in its comment. `verification/probes.txt`
     says so.
4. *A moved pointer?* None in a standard. `README.md` already says the harness's transcripts live
   in the spec that last changed a gate file, which is now this one. The earlier specs' records
   stay as they were recorded.

No project standard exists to edit, and `agent-os/standards/index.yml` is untouched: its `base:`
section is the sync's. The retrospective's own change set is this section and
fromtheoutfit/patchbay-standards#20. It edited no file outside this spec folder.

Proposals sent upstream: fromtheoutfit/patchbay-standards#20.

### Standards retrospective (proposed, base)

Presented to the owner on 2026-11-06 with AskUserQuestion, multi-select, in two questions: 1–3
with "None of these", then 4 with "None of these". All four were approved and filed as one issue,
fromtheoutfit/patchbay-standards#20, titled a gate spec since proposal 1 needs a gate file changed,
as the issue says. No AI attribution.

Proposal 5 was the owner's, added on 2026-11-06 after the spec was handed over, with the
instruction to file it; the ask is its approval. It was filed as a comment on
fromtheoutfit/patchbay-standards#20, no AI attribution, which names it a gate-file proposal too:
the sync's output is `scripts/sync-standards.sh`'s, a gate file in every project.

- `base/process/verification-gate.md` — "One script", the listing rule: a tracked file that
  `.gitignore` matches fails the listing step by name (`git ls-files -ci --exclude-standard`
  listing anything). Verified against `verification/probes.txt` sections 1–2, test p's
  force-added run in `verification/gate-negative-tests.txt` (exit 0, the gap as it stands), and
  the command listing nothing in either repository today. Proposed, not applied; filed as
  fromtheoutfit/patchbay-standards#20.
- `base/process/verification-gate.md` — "One script", the listing rule: a third form, a tool that
  walks a directory given each path `git ls-files -z --others --ignored --exclude-standard
  --directory` lists there to skip. Verified against `scripts/gate.sh` step 5, test q and
  `verification/probes.txt` section 3. Proposed, not applied; filed as
  fromtheoutfit/patchbay-standards#20.
- `base/process/verification-gate.md` — "One script": the missing-file and symlink clause binds
  the git's-list form; a tool that walks the disk is not asked to see a file that is not there.
  Verified against `scripts/gate.sh` step 1's `present` and steps 2–5. Proposed, not applied;
  filed as fromtheoutfit/patchbay-standards#20.
- `base/python/toolchain.md` — "mypy" gains `exclude_gitignore = true` with its documented limit;
  "The gate's tool steps" says how each step reads only what git lists (ruff's `respect-gitignore`,
  mypy's key, pytest's `--ignore`). Verified against `pyproject.toml` `[tool.mypy]`,
  `scripts/gate.sh` steps 4–5, tests p and q, and `verification/probes.txt` sections 2–3.
  Proposed, not applied; filed as fromtheoutfit/patchbay-standards#20.
- `base/process/standards-sync.md` — "What the sync writes, and nothing else": the sync also
  writes an entry under `[Unreleased]` in the project's `CHANGELOG.md` naming the old and the new
  commit, so a sync forward is recorded by the change that makes it; "Pinned, not tracking", which
  limits the sync's commit to the synced files, gains `CHANGELOG.md` with it. Verified against
  this spec's `CHANGELOG.md`: `ae58aac` added no entry though the header asked for one, so this
  spec added "Base standards synced from `b3fc2fe` to `11ceffd` (`ae58aac`, PR #8)" afterwards and
  reworded the header to say the next spec writes it. Proposed, not applied; filed as a comment on
  fromtheoutfit/patchbay-standards#20.

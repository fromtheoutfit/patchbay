# Gate revision after the review of PR 3 — Shaping Notes

Shaped 2026-11-05 in plan mode with this repository's customized `/agent-os:shape-spec`, the Step
1–5 questions and one design choice asked and answered by the owner (recorded under Shaping
answers and Decisions).

## Core Architecture (Non-Negotiable)

None yet; see Step 5a of `.claude/commands/agent-os/shape-spec.md`. The toolchain, layout and
typing standards will fill this tier.

## Scope

The owner's review of PR 3 at commit `6c91362`, ten findings, addressed as the review
recommends: (1) the harness's scratch directory guard, (2) gate step 1's file list, (3) the
harness failing hard and asserting exit statuses, (4) CI checking `patchbay-standards` out at the
commit in `.version`, (5) negative tests for the sync-script and extra-file checks of step 2, (6)
setup-uv removed from the workflow, (7) the hosted run recorded, (8) Step 5b's reserved `root`
section, (9) `pyproject.toml`'s description, (10) Step 5a's heading. The hosted `gate` run
42124784656 passed on that commit. This is the gate's own spec: every gate file changes here, with
the negative test for each changed step, on the same branch so PR 3 carries the fix.

## Shaping answers

- **Step 1, scope:** all ten findings, in a new spec folder on the same branch. Design choice for
  finding 2: step 1's list is git's and bash scripts are parsed, any other file refused by name.
- **Step 2, visuals:** none.
- **Step 3, references:** the sibling's PR 9 revision record and this repository's gate files as
  committed; see `references.md`.
- **Step 4, product context:** aligned. `tech-stack.md` says the gate's tools are pinned in
  `scripts/gate.sh` and run through `uvx`; setup-uv returns to the workflow when a step first does.
- **Step 5, standards:** all five base standards, the snapshot unchanged from the first spec.

## Decisions

- **The review on PR 3 is the scope.** Ten findings, each with its disposition in `plan.md`'s
  table; all accepted as the review recommends, finding 2's shape the owner's choice. Nothing
  outside them changes but this spec folder, `CHANGELOG.md` and one pointer line in the first
  spec's `shape.md`.
- **Step 1 parses every shell script under `scripts/` as git lists them** (owner's choice): the
  tracked files plus the untracked ones git does not ignore, the rule `scripts/sync-standards.sh`
  already applies to `base/`, so an ignored `.DS_Store` is never seen and a script a spec adds
  before the owner stages it is. A file ending in `.sh` or starting with a bash shebang is parsed;
  any other file fails the step by name, since only shell scripts live under `scripts/` until a
  spec says otherwise; a tracked file missing from the disk and a tree that is not a git work
  tree each fail by name. `.DS_Store` is added to `.gitignore`.
- **The exit contract is unchanged**: 1 at the first failing step after `FAIL  step N/M:
  <reason>`, 2 on usage.
- **The harness fails hard and asserts.** `mk` dies on any setup failure; `run` takes the expected
  status, prints `exit=N`, marks a mismatch `UNEXPECTED`, and the harness exits 1 at the end
  naming the count, so a transcript's last line says whether every case behaved. The scratch
  directory is taken from `mktemp -d` under `|| die`, refused when empty, not a directory, or at
  or under the repository, and only then resolved; the trap removes `${NEG:?}`.
- **CI checks `patchbay-standards` out at the commit in `.version`**: a `run` step reads the file
  into `$GITHUB_OUTPUT` and the checkout takes it as `ref` at the default depth, the form
  `standards-sync.md` names. The first round's `main` with full history is gone: a pin off `main`
  that was later deleted or squashed would have failed only in CI.
- **setup-uv is removed**: no step assumes a runner, so none is installed; the toolchain spec adds
  it back, pinned, when a step first runs `uvx`. The deviation the first spec recorded closes.
- **A new spec folder on the same branch** (owner's choice): the first spec's record and
  transcripts stay as committed, with one line pointing here; this folder holds the current
  transcripts and the hosted run.
- **`pyproject.toml`'s description** is the README's one-liner; `uv.lock` carries no description
  and is unchanged.

## Context

- **Visuals:** None.
- **References:** `references.md`.
- **Product alignment:** `agent-os/product/tech-stack.md` (uv and `uvx` for pinned gate tools);
  `mission.md` untouched.

## Standards Applied

**Core (always applied):**
- none yet (Step 5a)

**Feature-specific:**
- `base/process/verification-gate` — the gate's own spec: every gate file changes here with its
  negative test; the CI rules (one job, pins by commit, the runner the script assumes, no cache,
  no credential, the replay before any push, the hosted run recorded); the file-list and exit
  rules this spec tightens.
- `base/process/standards-sync` — the drift check's three comparisons, each now with a negative
  test; the CI layout, with the pinned commit passed as the checkout's `ref`.
- `base/process/ownership` — no commit, stage, push, PR, approval or merge by an agent; nothing
  installed.
- `base/process/standards-index` — the reserved `root` section Step 5b now names; the index
  untouched.
- `base/process/standards-retrospective` — governs the closing step; base changes proposed, not
  edited.

## Verification Gate

Spec is not complete until `scripts/gate.sh` passes — `bash -n` on every shell script under
`scripts/` as git lists them, and `scripts/sync-standards.sh --check` against
`../patchbay-standards` at the commit in `agent-os/standards/base/.version` — and the three
judgment steps are recorded, in this order: Docs, Version, then the standards retrospective below.

**Results (2026-11-05):** `scripts/gate.sh` exit 0 on the tree, run as the last act before
hand-over on branch
`feature/1-bootstrap-shape-spec-claudemd-gate-with-the-drift-check-ci-readme-changelog`;
`verification/gate-run.txt` holds the transcript with the date and branch on its first line.
Every gate file changed in this spec, so every negative test ran after the last edit to any of
them, each run asserting its expected status: `verification/gate-negative-tests.txt` holds a to g
and u, 20 runs, 0 unexpected (a: step 1 names `scripts/broken.sh`, exit 1; b: `changed
process/ownership.md`; c: `base: section differs`; d: the sync script's exit 2 naming
`../patchbay-standards`, the gate's 1; e: `scripts/sync-standards.sh differs`; f: `extra
process/extra.md`; g: an ignored `scripts/.DS_Store` passes, a tracked `scripts/notes.txt` is
"not a shell script", a tracked script missing from the disk and a copy without `.git` are each
refused by name; u: `--help` and a stray argument exit 2, the clean copy 0).
`verification/ci-negative-test.txt` holds j, 3 runs, 0 unexpected: the pin step writes
`sha=b3fc2fe…` to `GITHUB_OUTPUT`, the sha in the copy's `.version`; the gate step from
`working-directory: patchbay` passes on the clean copy and fails at step 4 with exit 1 on the copy
with `broken.sh`. The hosted run 42124784656 (`success`, on `6c91362`, the workflow before this
revision) is recorded at its end; the revised workflow's hosted run is read back by the owner
after the push and recorded there.

**Docs (step 3):** `README.md` gate section read against `scripts/gate.sh`: step 1's list rule
and refusal, step 2, the exit contract, CI at the pinned commit, uv arriving with the toolchain
spec. `CLAUDE.md` Specs: step 1's wording matches the script; nothing says CI installs uv; the
gate's own files list is unchanged and true. `scripts/gate.sh`'s header names the list rule and
every refusal step 1 makes, each read against the loop below it. `scripts/gate-negative-tests.sh`'s
header names the nine cases, the assertion, the setup failure, the scratch guard and what it
needs. `.github/workflows/gate.yml`'s header says the pin step, the checkout at that commit, no
runner installed and why, and the pins the job has, read against the steps below.
`.claude/commands/agent-os/shape-spec.md`: Step 5a names the template's heading; Step 5b names
the reserved `root` section as `standards-index.md` defines it; the gate task, Step 8 and the
template's Verification Gate paragraph say step 1 the same way as the script. `pyproject.toml`'s
description is the README's first sentence. The first spec's `shape.md` carries one line pointing
here; its transcripts stay as recorded. Standards that name these files:
`verification-gate.md` "CI" ("install the runner the script already assumes": none assumed, none
installed, the deviation closed; every action pinned; the replay before any push; the hosted run
recorded) and `standards-sync.md` "In a consuming project" (the project in a subdirectory, the
sibling beside it at the commit in `.version`, "a step reads the file and passes it as that
checkout's `ref`") each read true against the shipped workflow. `agent-os/standards/index.yml`
unchanged. `agent-os/product/` unchanged and still true.

**Version (step 4):** recorded under `[Unreleased]` in `CHANGELOG.md`: a Changed entry for this
spec naming each finding's fix, and the first spec's Added bullets for the gate script, the
workflow and the harness rewritten to the tree, with `pyproject.toml` added to them.
`pyproject.toml` stays at 0.1.0: nothing is released, so there is no bump.

**Not done by the agent, by rule:** no file staged, committed or pushed; the pull request not
edited; the owner reads the diff at commit time.

## Standards Retrospective

Step 5, always last. Per `agent-os/standards/base/process/standards-retrospective.md`. Applied
2026-11-05 from the shipped diff against `6c91362` (`.claude/commands/agent-os/shape-spec.md`,
`.github/workflows/gate.yml`, `.gitignore`, `CHANGELOG.md`, `CLAUDE.md`, `README.md`,
`pyproject.toml`, `scripts/gate.sh`, `scripts/gate-negative-tests.sh`, the first spec's
`shape.md` and this spec folder). No base file and no line of the `base:` section is touched; this
repository has no project standard yet, so there is nothing to edit in place and `index.yml` is
unchanged.

1. *A pattern no standard covers?* Three, all in gate files and all for `patchbay-standards`,
   proposed below. The gate's file list: step 1 reads the tracked files plus the untracked ones
   git does not ignore, the rule `sync-standards.sh` applies to `base/`, and parses shell scripts
   only, refusing anything else by name; the sibling's gate uses `find`, which the review showed
   parsing a Finder stray. A harness that guards its scratch directory and asserts: `mktemp -d`
   under a hard failure, the result refused when empty or inside the repository, every `run`
   naming the status it expects and the harness exiting 1 on a mismatch; the sibling's harness has
   the same `mktemp` line finding 1 names and asserts nothing. And the pin step: a consuming
   project's workflow reads `.version` into `GITHUB_OUTPUT` and passes it as the checkout's `ref`,
   which `standards-sync.md` already allows in one clause and the sibling's guidance could name as
   the form to use, since `main` with full history fails on a pin off `main` that was later
   squashed. Nothing else new: the exit contract is the first spec's.
2. *A standard wrong or stale?* None found. `verification-gate.md`'s "install the runner the
   script already assumes" is now followed to the letter, which the first spec recorded as a
   deviation; `standards-sync.md`'s two forms for the checkout both read true, this spec using the
   first. `standards-index.md`'s reserved `root` section is what Step 5b now names.
3. *A deliberate deviation?* None. The first spec's one deviation (setup-uv installed with no step
   using it) is closed by finding 6. The gate files changed in this spec, whose feature is the
   gate, as `verification-gate.md` directs.
4. *A moved pointer?* None. The first spec's `shape.md` gained a pointer here; the `shape-spec.md`
   heading Step 5a names is now the template's. No standard pointed at a file this spec renamed.

### Standards retrospective (proposed, base)

- `base/process/verification-gate.md` — "One script" or "In a consuming project": the step that
  parses scripts lists them with git (tracked plus untracked-not-ignored, as the sync script lists
  `base/`) and parses shell scripts only, refusing any other file by name; `find` sees ignored
  strays and non-bash files. Verified against `scripts/gate.sh` as shipped and test g. The
  sibling's `scripts/gate.sh` adopts it in its next gate spec. Proposed, not applied.
- `base/process/verification-gate.md` — "Every step that can fail is proven to fail": the
  harness takes its scratch directory from `mktemp -d` under a hard failure and refuses one that
  is empty or inside the repository before any trap can remove it, and every negative run names
  the status it expects, the harness failing on a mismatch so a transcript's last line says
  whether the cases behaved. Verified against `scripts/gate-negative-tests.sh` as shipped (the
  guard, `run`, the summary line). The sibling's harness has the same `mktemp` line. Proposed,
  not applied.
- `base/process/standards-sync.md` — "In a consuming project": name the pin step as the form to
  use (a `run` step reads `.version` into `GITHUB_OUTPUT`, the checkout takes it as `ref` at the
  default depth), since `main` with full history fails on a pin off `main` that was later
  squashed or deleted. Verified against `.github/workflows/gate.yml` as shipped and test j.
  Proposed, not applied.
- `base/process/verification-gate.md` — the exit contract (1 at a failed step, named on stderr; 2
  on usage), as the first spec proposed; restated here because this spec's tests a, d, g and u
  verify it again. Proposed, not applied.

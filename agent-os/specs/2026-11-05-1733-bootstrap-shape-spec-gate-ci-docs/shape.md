# Bootstrap: shape-spec, CLAUDE.md, gate with the drift check, CI, README, CHANGELOG — Shaping Notes

Shaped 2026-11-05 in plan mode with the stock `/agent-os:shape-spec` (this once; the customized
command this spec writes serves every spec after). The Step 1–5 questions and two clarifications
were asked and answered by the owner (recorded under Shaping answers and Decisions).

## Core Architecture (Non-Negotiable)

None yet; see Step 5a of `.claude/commands/agent-os/shape-spec.md`. The toolchain, layout and
typing standards will fill this tier.

## Scope

GitHub issue #1, "Bootstrap: shape-spec, CLAUDE.md, gate with the drift check, CI, README,
CHANGELOG". Make this repository a patchbay repository before any Python tooling lands: the
customized shape-spec command, `CLAUDE.md`, a gate whose only runnable steps are `bash -n` over
`scripts/` and the base-standards drift check, the gate's workflow, the negative tests, a README
that says what the package is, a CHANGELOG, and `agent-os/product/`. The toolchain (ruff, mypy,
pytest) is the next spec; this one is the frame it lands in. Gate green,
`verification/gate-run.txt` with date and branch; no commit, PR or push by an agent.

## Shaping answers

- **Step 1, scope:** issue #1 as written. Two clarifications: the gate's exit contract follows the
  issue's words (1 on a failed step, 2 on usage) rather than the sibling's pass-through of the
  tool's status, and that contract is proposed to `verification-gate.md` in the retrospective
  below; the CI replay is a fifth negative-test case, because the gate standard requires it
  before any push.
- **Step 2, visuals:** none.
- **Step 3, references:** the sibling's gate files and its five spec folders; see `references.md`.
- **Step 4, product context:** `agent-os/product/` did not exist; this spec creates it. Skipped
  as a question.
- **Step 5, standards:** all five base standards under `agent-os/standards/base/process/`,
  included in `standards.md`. The Step 5a tier is empty.

## Decisions

- **GitHub issue #1 is the scope.** Its sections (shape-spec.md, CLAUDE.md, scripts/gate.sh, CI,
  negative tests, README.md and CHANGELOG.md, agent-os/product/) are the tasks; its "Rules"
  paragraph is this spec's definition of done. Nothing outside it changes but this spec folder.
- **This is a consuming project.** The five standards under `agent-os/standards/base/` are in
  force and read-only here: no file under `base/` and no line of the `base:` section of
  `agent-os/standards/index.yml` is edited, and `scripts/sync-standards.sh` is the synced copy
  at the pinned commit, not edited. A base change is a pull request to `patchbay-standards`,
  the sibling checkout at `../patchbay-standards`.
- **Exit contract of `scripts/gate.sh`** (owner's choice): a failed step prints
  `FAIL  step N/M: <reason>` on stderr and the gate exits 1, whatever the tool returned; any
  argument is usage, exit 2. The sibling's gate lets the tool's status through (2 from `bash -n`,
  2 from a sync precondition); the base standard says only "non-zero". Proposed below so the
  sibling adopts it in its next gate spec.
- **Two runnable steps, no tool pin yet.** Step 1 needs bash; step 2 needs git, cmp, comm, awk
  and sed, all already present. The script's header holds the place where the next spec pins
  ruff, mypy and pytest, one named variable per tool with its publish date, run through `uvx`.
- **CI checks `patchbay-standards` out at `main` with full history** (`fetch-depth: 0`), as the
  issue says; the drift check reads the commit in `.version`, which must be on `main`. uv is
  installed and pinned to 0.13.7, the sibling workflow's version, although no step runs it yet.
  Both repositories are public, so the second checkout needs no token and the checkout keeps
  none. The layout is `standards-sync.md`'s: both repositories under the workspace, the project
  in `patchbay/`, the sibling beside it, the gate run with `working-directory: patchbay`.
- **Negative tests are rebuilt here, not copied**: the sibling's cases test `check-index.sh`,
  pymarkdown and the sync script, none of which is a step here. The harness clones the sibling
  once into the scratch directory and lays each case out as `<case>/patchbay` beside a
  `<case>/patchbay-standards` symlink to the clone, so the sync script's default path resolves
  as it does in the tree. Nothing in the tree or in `../patchbay-standards` is written. Cases a
  (unparsable script), b (a one-byte edit under `base/`), c (a hand-edited `base:` entry), d
  (the sibling checkout missing), u (usage and the clean copy) and j (the CI replay).
- **Verbatim sections** of `CLAUDE.md` (Git, No AI attribution, Ownership) are the sibling's
  rules. Two phrases in Ownership read from the sibling's point of view ("The first spec
  installed uv with Homebrew unasked" and "a base standard, `base/process/ownership.md`"); on
  the owner's instruction they were adapted so the file reads true here, since "verbatim" meant
  the rules, not the sibling's history. Recorded under Docs.
- **Version:** `pyproject.toml` stays at 0.1.0; nothing is released, so the change sits under
  `[Unreleased]` with no bump.

## Context

- **Visuals:** None.
- **References:** `references.md`.
- **Product alignment:** N/A at shaping time (`agent-os/product/` is created by this spec:
  `mission.md` and `tech-stack.md`).

## Standards Applied

**Core (always applied):**
- none yet (Step 5a)

**Feature-specific:**
- `base/process/verification-gate` — the shape of `scripts/gate.sh` (one script, fixed order,
  stops at the first failure, every step reports by name, pins in the script), the judgment
  steps, the CI rules (one job, every action pinned to a commit, the runner pinned, no cache, a
  timeout, no credential), the negative tests and the CI replay, the gate-file rule, and the
  "In a consuming project" paragraph this gate follows.
- `base/process/standards-sync` — `scripts/sync-standards.sh --check` as a gate step; the CI
  layout of two checkouts under the workspace; the invariant the drift check holds; a base edit
  is a pull request to `patchbay-standards`.
- `base/process/ownership` — no commit, stage, push, PR, approval or merge by an agent; nothing
  installed outside the repository (bash, git and uv are already present); `CLAUDE.md` names the
  owner under `## Ownership` directly under `## Git`.
- `base/process/standards-index` — the project's `index.yml` carries the synced `base:` section
  untouched and its own sections beside it (none yet); the stock `index-standards` is not run on
  it.
- `base/process/standards-retrospective` — governs the closing step; a base change is proposed,
  never edited in place.

## Verification Gate

Spec is not complete until `scripts/gate.sh` passes — `bash -n` on every file under `scripts/`
and `scripts/sync-standards.sh --check` against `../patchbay-standards` at the commit in
`agent-os/standards/base/.version` — and the three judgment steps are recorded, in this order:
Docs, Version, then the standards retrospective below.

**Results (2026-11-05):** `scripts/gate.sh` exit 0 on the tree, run as the last act before
hand-over on branch
`feature/1-bootstrap-shape-spec-claudemd-gate-with-the-drift-check-ci-readme-changelog`;
`verification/gate-run.txt` holds the transcript with the date and branch on its first line. The
gate was green on the tree before `.github/workflows/gate.yml` was written, as the owner asked,
and again at hand-over. Every gate file is new in this spec, so every negative test ran after the
last edit to any of them: `verification/gate-negative-tests.txt` holds a (step 1 fails naming
`scripts/broken.sh`, exit 1, `2/2` never printed), b (step 2 names `process/ownership.md`
changed, exit 1), c (step 2 reports `base: section differs`, exit 1), d (the sync script's own
exit 2 naming `../patchbay-standards`, the gate's exit 1) and u (`--help` and a stray argument
exit 2 with the usage line; the clean copy exits 0); `verification/ci-negative-test.txt` holds j,
the replay of the workflow's one `run` step from `working-directory: patchbay` under the scratch
workspace, passing on the clean copy and failing at step 4 with exit 1 on the copy with
`broken.sh`. The hosted run on the pull request is the proof of the workflow itself; the owner
records its id and conclusion at the end of `ci-negative-test.txt` once it exists.

**Docs (step 3):** `README.md` rewritten and read against the tree: the layout lists what exists,
the gate section matches `scripts/gate.sh`'s two steps and exit contract, the sync section matches
`scripts/sync-standards.sh`'s usage line, and "the spec that last changed a gate file" is this one.
`CLAUDE.md`: the Specs section names the two steps, the judgment order, the CI layout and the
gate's own files as shipped; `## Ownership` sits directly under `## Git` (its `### No AI
attribution` subsection between them, as in the sibling), so `ownership.md`'s "In a consuming
project" holds. Two phrases in the Ownership section as first copied read from the sibling's point
of view: "The first spec installed uv with Homebrew unasked; its `shape.md` records that" is
`patchbay-standards`' history, not this repository's, and "a base standard,
`base/process/ownership.md`" is the sibling's path. On the owner's instruction both were adapted
so the file reads true here: the uv sentence is dropped, and the pointer is
`agent-os/standards/base/process/ownership.md`, the base standard every consuming project syncs
in. Nothing else in the section changed; "verbatim" in the issue meant the rules, not the
sibling's history.
`scripts/gate.sh`'s header names steps 1-2, the judgment steps 3-5, the exit contract, what each
step needs and the place for the pins, each read against the code below it.
`scripts/gate-negative-tests.sh`'s header names the six cases, the scratch layout and what it
needs. `.github/workflows/gate.yml`'s header says the layout and the pins the job has.
`.claude/commands/agent-os/shape-spec.md`'s gate task lists the two steps and the three judgment
steps and says `scripts/gate.sh` runs steps 1-2; the `shape.md` template matches this file's
headings. `agent-os/product/tech-stack.md`'s claims about `pyproject.toml`, `.python-version` and
the lockfile are true of the tree. Standards that name these files: `verification-gate.md` "In a
consuming project" (own step list in the gate's shape, `shape-spec.md` lists them with the
judgment steps after, the workflow runs the script and nothing else, `CLAUDE.md` names the script,
`--check` is a step, the workflow checks `patchbay-standards` out beside the project under the
workspace) and `standards-sync.md` "In a consuming project" (the sibling default, two checkouts,
the gate run from the project's directory, full history as the alternative to passing the pinned
commit as `ref`) each read true against `scripts/gate.sh` and `.github/workflows/gate.yml`.
`agent-os/standards/index.yml` is unchanged: its `base:` section is the sync's and this repository
has no section of its own yet.

**Version (step 4):** recorded under `[Unreleased]` in `CHANGELOG.md` as the first spec's Added
entry, with a closing paragraph naming the scaffold that predates it. `pyproject.toml` stays at
0.1.0: nothing is released, so there is no bump.

**Not done by the agent, by rule:** no file staged, committed or pushed, no pull request opened;
the owner reads the diff at commit time.

## Standards Retrospective

Step 5, always last. Per `agent-os/standards/base/process/standards-retrospective.md`. Applied
2026-11-05 from the shipped diff against `main` (`.claude/commands/agent-os/shape-spec.md`,
`.github/workflows/gate.yml`, `CHANGELOG.md`, `CLAUDE.md`, `README.md`, `agent-os/product/`,
`scripts/gate.sh`, `scripts/gate-negative-tests.sh`, and this spec folder). No base file and no
line of the `base:` section is touched; this repository has no project standard yet, so there is
nothing to edit in place and `index.yml` is unchanged.

1. *A pattern no standard covers?* Two, both in gate files and both for `patchbay-standards`,
   proposed below. The gate's exit contract: a failed step is exit 1 after `FAIL  step N/M:
   <reason>` on stderr, whatever the tool returned, and usage is exit 2; `verification-gate.md`
   says only "non-zero", and the sibling's gate passes the tool's status through (2 from
   `bash -n`). And the fixture for a consuming project's negative tests: one `git clone` of the
   sibling into the scratch directory per run, each case laid out as `<case>/patchbay` beside a
   `<case>/patchbay-standards` symlink to it, so the sync script's default path resolves as it
   does in the tree and the sibling is never written; the next adapter repository will copy
   that shape. Nothing else new: the harness's `mk`/`run`/`hdr`/`note` and the CI replay follow
   the sibling's, the transcripts follow its spec folders, and the CI layout is
   `standards-sync.md`'s.
2. *A standard wrong or stale?* None found. Read during the spec and found to match:
   `verification-gate.md`'s "In a consuming project" and `standards-sync.md`'s against the gate
   and the workflow as shipped; `ownership.md`'s placement rule against `CLAUDE.md`;
   `standards-index.md`'s against the untouched index. The pin and rule-set paragraphs of
   `verification-gate.md` are vacuous here until the toolchain spec, not wrong.
3. *A deliberate deviation?* One, recorded as a one-off: the workflow installs uv 0.13.7 although
   no gate step runs it, where `verification-gate.md` says CI installs "the runner the script
   already assumes". The issue asked for the pin so the toolchain spec's steps land on a workflow
   already proven; it stops being a deviation when that spec pins its first tool through `uvx`.
   Not a deviation: the stock `shape-spec` shaped this spec, as the issue says, since the
   customized one is this spec's own output.
4. *A moved pointer?* None. No standard pointed at a file in this repository before this spec.
   The two sibling-flavoured phrases first copied into `CLAUDE.md`'s Ownership section were
   adapted and are recorded under Docs; they are not standards pointers.

### Standards retrospective (proposed, base)

- `base/process/verification-gate.md` — "One script": fix the exit contract. Today it says the
  script "exits non-zero at the first step that fails". Proposed: exit 1 at the first step that
  fails, after a line on stderr naming the step and its reason (`FAIL  step N/M: <reason>`),
  whatever status the tool returned; exit 2 on usage. Verified against `scripts/gate.sh` as
  shipped and tests a, d and u in `verification/gate-negative-tests.txt` (d shows the sync
  script's 2 becoming the gate's 1). The sibling's `scripts/gate.sh` adopts it in its next gate
  spec. Proposed, not applied; a base standard changes in its own spec there, with the owner.
- `base/process/verification-gate.md` — "Every step that can fail is proven to fail", or
  `base/process/standards-sync.md` "In a consuming project": name the fixture a consuming
  project's negative tests use for the drift-check step: one clone of the sibling checkout into
  the scratch directory per run, each case as `<case>/patchbay` with `<case>/patchbay-standards`
  symlinked to the clone, the sibling itself never written, and the missing-sibling case made by
  removing the symlink. Verified against `scripts/gate-negative-tests.sh` as shipped (`mk`, test
  d). Proposed, not applied.

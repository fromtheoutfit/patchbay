# Issue #1: bootstrap patchbay as a patchbay repository

## Context

`fromtheoutfit/patchbay` is a fresh scaffold (one commit after the initial one): an empty typed
`patchbay` package, the five base standards synced in from `patchbay-standards` at
`b3fc2fe7aa61147ae688f946e2533ae21902713b`, `scripts/sync-standards.sh` installed by that sync,
and the stock Agent OS commands. It has no `CLAUDE.md`, no gate, no CI, no CHANGELOG, a two-line
README and no product docs. Issue #1 makes it a patchbay repository before any Python tooling
lands: the customized `shape-spec`, `CLAUDE.md`, a gate whose only runnable steps are `bash -n`
and the drift check, the gate's workflow, the negative tests, README, CHANGELOG and
`agent-os/product/`. The toolchain (ruff, mypy, pytest) is the next spec; this one is the frame.

Shaped 2026-11-05 in plan mode with the stock `/agent-os:shape-spec`. Answers:

- Step 1 scope: issue #1 as written. Clarifications: `gate.sh` exits 1 on any failed step and 2
  on usage (the issue's words; the sibling propagates the tool's status), and the exit contract is
  proposed to `verification-gate.md` in this spec's retrospective; the CI replay is a fifth
  negative-test case because the gate standard requires it before any push.
- Step 2 visuals: none. Step 3 references: the sibling's gate files and five spec folders.
- Step 4: `agent-os/product/` does not exist; this spec creates it. Skipped as a question.
- Step 5: all five base standards included in `standards.md`; Step 5a tier empty.

Facts verified while shaping: the drift check is green on the tree today (`--check` exit 0); the
pinned commit is `origin/main`'s tip in the sibling; both repositories are public, so the
workflow's second checkout needs no token; uv 0.13.7 is on PATH; the four stock commands other
than `shape-spec.md` are byte-identical to the sibling's. No file under
`agent-os/standards/base/` and no line of the `base:` section is edited; `scripts/sync-standards.sh`
is the synced copy and is not edited.

Base standards in force (read-only here): `agent-os/standards/base/process/{ownership,
standards-index, standards-retrospective, standards-sync, verification-gate}.md`.

## Spec folder

`agent-os/specs/2026-11-05-1733-bootstrap-shape-spec-gate-ci-docs/` with `plan.md`, `shape.md`,
`standards.md`, `references.md`, `verification/` (no `visuals/`).

## Task 1: Save spec documentation

- `plan.md`: this plan.
- `shape.md`, in the sibling's shape (its sync spec's `shape.md` is the model): `## Core
  Architecture (Non-Negotiable)` ("None yet; see Step 5a"), `## Scope` (issue #1), `## Shaping
  answers` (the five steps and the two clarifications above), `## Decisions` whose **first
  Decision is "GitHub issue #1 is the scope"**, citing it, then the decisions below; `## Context`;
  `## Standards Applied` (all five, each with why); `## Verification Gate` with Results, Docs and
  Version left to fill in Task 9; `## Standards Retrospective` filled in Task 9.
- `standards.md`: the snapshot paragraph, then the full text of all five base standards.
- `references.md`: the sibling's `shape-spec.md`, `CLAUDE.md`, `scripts/gate.sh`,
  `scripts/gate-negative-tests.sh` (fixture pattern `mk`/`run`/`hdr`/`note`, test j's replay),
  `.github/workflows/gate.yml` (the pins), `CHANGELOG.md`, and its gate spec (issue #3) and sync
  spec (issue #8) folders, each with relevance and what is borrowed.

Decisions to record in `shape.md`:

- Issue #1 is the scope; its Rules paragraph is the definition of done.
- Exit contract of `scripts/gate.sh`: 1 on a failed step with `FAIL  step N/M: <reason>` on
  stderr, 2 on usage (any argument). Proposed to `verification-gate.md` in the retrospective.
- Runnable steps are two; no tool pin exists yet (bash and git only), and the header says the
  next spec adds the pins (ruff, mypy, pytest), one variable per tool with its publish date.
- CI checks out `patchbay-standards` at `main` with full history (`fetch-depth: 0`), as the issue
  says; the sync script reads `.version` and compares against that commit, which must be on
  `main`. uv is installed and pinned to 0.13.7 although no step uses it yet, as the issue says.
- Negative tests are rebuilt for this gate, on a scratch copy of the project beside a scratch
  clone of the sibling; the tree and the sibling are never written. Five cases plus usage.
- Verbatim copies: `CLAUDE.md`'s Git, No AI attribution and Ownership sections are the sibling's
  bytes, as the issue directs. Two phrases in Ownership read from the sibling's point of view
  ("The first spec installed uv with Homebrew unasked", "a base standard, `base/process/ownership.md`");
  copied as directed and noted under Docs.
- Version: `pyproject.toml` stays 0.1.0; nothing is released, so the change sits under
  `[Unreleased]` with no bump. Recorded under Version.

## Task 2: Customize `.claude/commands/agent-os/shape-spec.md`

Copy the sibling's structure; every deviation from stock the sibling made is made here, with this
repository's wording. Stock text elsewhere stays stock; the other four commands are untouched.

- Step 3 examples: this repository's ("Look at how `scripts/gate.sh` reports a step",
  "`scripts/gate-negative-tests.sh` is the fixture shape for a scratch copy").
- Step 5: the two-kinds paragraph adapted to a consuming project: base standards live under
  `agent-os/standards/base/`, synced from `patchbay-standards` and pinned to the commit in
  `agent-os/standards/base/.version`; owned by `patchbay-standards`; **never edited here**; a change
  the spec would make is recorded in `shape.md` under `## Standards retrospective (proposed, base)`
  and becomes a pull request to `patchbay-standards` (the sibling checkout `../patchbay-standards`).
  Project standards are this repository's own files outside `base/` and change in its retrospective.
- Step 5a "Core Architecture (always included)": empty for now, with the note that the toolchain,
  layout and typing standards will fill it; record "none yet; see Step 5a" in `shape.md`.
- Step 5b: `index.yml`'s `base:` section is synced and keys resolve to
  `agent-os/standards/base/<key>.md`; the project's own sections sit beside it.
- The snapshot paragraph ("What you read here is a snapshot ... they change at the END of the
  spec, in the retrospective (gate step 5)"), verbatim but for the step number.
- Task N gate, this repository's list:
  1. `bash -n` on every file under `scripts/`
  2. `scripts/sync-standards.sh --check`: `agent-os/standards/base/`, the `base:` section and the
     script match `patchbay-standards` at the commit in `.version`, against `../patchbay-standards`
  3. **Docs**, 4. **Version**, 5. **Standards retrospective** (the sibling's text, renumbered).
  "`scripts/gate.sh` runs steps 1–2 as one command. Steps 3–5 are judgment."
- Step 8's "Always include the final verification task" sentence, Step 9's text, the Tips, and the
  `shape.md` / `standards.md` / `references.md` templates: the sibling's, with this gate named and
  the `index.yml` line reading "the project's own sections; the `base:` section is synced".

## Task 3: `CLAUDE.md`

- `## Git`, `### No AI attribution — anywhere`, `## Ownership`: the sibling's bytes, verbatim.
- One added line (after Ownership, before Specs): this is a consuming project, so
  `agent-os/standards/base/` is read-only here, and `../patchbay-standards` is where a base change
  goes, as a pull request.
- `## Specs & the standards retrospective`: the sibling's section adapted: work is shaped with
  `/agent-os:shape-spec` and follows the standards under `agent-os/standards/base/` (synced, pinned
  to the commit in `.version`) and the project's own; the gate is `scripts/gate.sh`, which runs
  `bash -n` on every file under `scripts/` and `scripts/sync-standards.sh --check` against
  `../patchbay-standards`, then Docs, Version and the retrospective recorded in `shape.md`; CI
  (`.github/workflows/gate.yml`) runs `scripts/gate.sh` and nothing else; the remaining bullets as
  the sibling has them, with `base/` read as `agent-os/standards/base/`.

## Task 4: `scripts/gate.sh` (run green before Task 5)

Model: the sibling's `scripts/gate.sh` (header, `step` banner, `cd "$(dirname "$0")/.."`,
`set -euo pipefail`, closing line). Differences:

- Usage: any argument prints a usage line and exits 2.
- `fail() { printf 'FAIL  step %s: %s\n' "$1" "$2" >&2; exit 1; }`; every step is `cmd || fail`.
- No pin variable yet; a comment block where the pins go, saying the next spec adds ruff, mypy and
  pytest there, one named variable per tool with its publish date, run through `uvx`.
- Step `1/2  bash -n on every file under scripts/`: `find scripts -type f | LC_ALL=C sort`, each
  file `bash -n` then `ok   <file>`.
- Step `2/2  scripts/sync-standards.sh --check against ../patchbay-standards at the commit in
  agent-os/standards/base/.version`: run it; its own `ok`/`FAIL` lines and JSON show; on failure
  `fail 2/2 "drift from patchbay-standards, or the sibling checkout unusable (see above)"`.
- Closing line: "Gate steps 1-2 passed. Steps 3-5 are judgment, recorded in shape.md: Docs,
  Version, the standards retrospective."

Run it: both steps green on the tree before writing the workflow (owner's rule).

## Task 5: `.github/workflows/gate.yml`

The sibling's file as the model (header comment, `name: gate`, `on: push main / pull_request`,
`permissions: contents: read`, one job `gate`, `ubuntu-24.04`, `timeout-minutes: 10`), with:

1. `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1`, `path: patchbay`,
   `persist-credentials: false`.
2. The same action: `repository: fromtheoutfit/patchbay-standards`, `ref: main`,
   `path: patchbay-standards`, `fetch-depth: 0` (the commit in `.version` must be on `main`),
   `persist-credentials: false`.
3. `astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3`, `version: "0.13.7"`,
   `enable-cache: false`.
4. `run: scripts/gate.sh` with `working-directory: patchbay`.

Nothing else. The header says the layout (both checkouts under the workspace, the project in a
subdirectory, the sibling beside it) is `standards-sync.md`'s.

## Task 6: `scripts/gate-negative-tests.sh`

Rebuilt for this gate (not copied; the sibling's cases test scripts this repository does not have).
Keep the sibling's harness shape: `set -uo pipefail`, `NEG=$(mktemp -d)` with a trap, `mk`, `run`
(prints output with the scratch path masked and `exit=N`), `hdr`, `note`, `[test ...]` arguments,
default every test but j, `all` adds j. Header: not run by the gate, parsed by step 1, each test on
a scratch copy, nothing in the tree or in `../patchbay-standards` touched; transcripts in the
spec's `verification/`.

Fixture: once per run, `git clone -q` the sibling (`$REPO/../patchbay-standards`) into
`$NEG/patchbay-standards` (a local clone carries every branch, so the pinned commit is present).
`mk <name>` copies `scripts/`, `agent-os/standards/`, `.gitignore` into `$NEG/<name>/patchbay`,
`git init` + `git add -A` there, and symlinks `$NEG/<name>/patchbay-standards` to the clone, so the
sync script's default path resolves as it does in the tree.

Cases, each asserting the named reason and the exit status, later steps never reached:

- `a`: `scripts/broken.sh` (`if true; then` with no `fi`); `gate.sh` must stop at step 1, exit 1,
  `2/2` never printed.
- `b`: one byte appended to `agent-os/standards/base/process/ownership.md`; step 1 passes, step 2
  fails naming `process/ownership.md` as changed, exit 1.
- `c`: a `description:` line of the `base:` section hand-edited; step 2 fails with
  `base: section differs`, exit 1.
- `d`: the `patchbay-standards` symlink removed; step 2 fails with the sync script's precondition
  naming `../patchbay-standards`, exit 1 (the step's own 2 is normalized by the gate).
- `u`: `gate.sh --help` and `gate.sh x` each exit 2 with the usage line; a clean copy exits 0.
- `j`: CI replay. The sibling's test j rebuilt for this workflow: read `.github/workflows/gate.yml`
  with pyyaml through `uv run --no-project --with pyyaml`, print the two `uses` checkouts and
  setup-uv as "not run here", execute each `run` step in `bash --noprofile --norc -eo pipefail`
  with its `working-directory` resolved under the scratch layout (`$NEG/j1` holds `patchbay/` and
  `patchbay-standards/` as the workflow lays them out); j1 clean must pass, j2 with `broken.sh`
  must fail at the run step with its exit status. The text block explaining that this is the job's
  control flow, not the hosted run, and that the hosted run id is recorded after the PR opens.

Transcripts: `verification/gate-negative-tests.txt` (a, b, c, d, u) and
`verification/ci-negative-test.txt` (j), first line the date and branch.

## Task 7: `README.md` and `CHANGELOG.md`

README (plain Markdown, blank line after the heading, no HTML entities):

- What patchbay is: headless control of software instruments from Python; the contracts, host and
  CLI that `patchbay-<instrument>` adapters plug into. An experiment, not a product.
- Names: distribution `patchbay-core`, import `patchbay`.
- Repository layout: `src/patchbay/`, `scripts/`, `agent-os/` (`product/`, `specs/`,
  `standards/base/` synced and read-only, `standards/index.yml`), `.claude/commands/agent-os/`,
  `.github/workflows/gate.yml`.
- Running the gate: `scripts/gate.sh`, what its two steps are, that it needs `../patchbay-standards`
  beside the checkout, that CI runs the same script.
- Syncing standards: `scripts/sync-standards.sh` (bare sync, `--check`, `--index-only`), pinned in
  `agent-os/standards/base/.version`, a base change is a PR to `patchbay-standards`.
- Standards and specs: shaped with `/agent-os:shape-spec`; `CLAUDE.md` holds the rules.

CHANGELOG: Keep a Changelog 1.1.0 header (the sibling's, with the "consuming projects pin" sentence
replaced by one saying base standards are pinned at the commit in `.version`), `## [Unreleased]`,
`### Added` with one entry for this spec (issue #1) listing what it adds, and a line that the
scaffold (package, lockfile, synced base standards at `b3fc2fe`, stock commands) predates it.

## Task 8: `agent-os/product/`

- `mission.md`: short. What core is (the contracts, host and CLI every adapter plugs into; headless
  control from Python). What it is not: no synth-specific concept lives here; core grows only when
  a second adapter needs the same thing. An experiment.
- `tech-stack.md`: the decisions already made, for the next spec to implement: uv and `uv_build`;
  Python >= 3.12; ruff with `select = ["ALL"]`; `mypy --strict`; pytest and hypothesis; pydantic v2;
  typer; src layout (`src/patchbay/`). Each one line, with "decided in issue #1, implemented by the
  toolchain spec".

## Task 9: Verification gate (always last)

1. `scripts/gate.sh` on the tree, as the last act after every other edit: exit 0. Save as
   `verification/gate-run.txt`, first line `Gate run 2026-11-05 on branch
   feature/1-bootstrap-shape-spec-claudemd-gate-with-the-drift-check-ci-readme-changelog, the last
   act before hand-over`, then `$ scripts/gate.sh` and the transcript with `exit=0`.
2. `scripts/gate-negative-tests.sh` → `verification/gate-negative-tests.txt`;
   `scripts/gate-negative-tests.sh j` → `verification/ci-negative-test.txt`. Rerun after the last
   edit to any gate file. The gate run in step 1 is redone if anything changes after it.
3. **Docs**: read README, `CLAUDE.md`, the headers of `gate.sh`, `gate-negative-tests.sh`,
   `gate.yml`, `shape-spec.md`'s gate task, `mission.md`, `tech-stack.md` against the shipped files;
   note the two sibling-flavoured phrases in the verbatim Ownership section. Record in `shape.md`.
4. **Version**: the `[Unreleased]` entry; version 0.1.0 unchanged, nothing released. Record.
5. **Standards retrospective** in `shape.md`, the four questions against the diff. Expected:
   no project standard exists; `index.yml`'s own sections unchanged (none yet). Under
   `### Standards retrospective (proposed, base)`: `base/process/verification-gate.md` should fix
   the exit contract (1 on a failed step, 2 on usage, the failing step named on stderr) so the
   sibling's `gate.sh` adopts it in its next gate spec; today it says only "non-zero". Verified
   against `scripts/gate.sh` and tests a, d, u as shipped. Anything else the diff teaches is
   added there; "no changes" is not expected.
6. Stop. Print `git status --short`. No stage, commit, PR or push (ownership rule); the owner
   reads the diff at commit time and records the hosted run id after the PR opens.

## Order of work

1 → 2 → 3 → 4 (gate green on the tree) → 5 → 6 (run; j after 5) → 7 → 8 → 9. Every edit after
the gate run means the run is redone; the transcripts kept are the final ones.

## Files

New: `CLAUDE.md`, `CHANGELOG.md`, `scripts/gate.sh`, `scripts/gate-negative-tests.sh`,
`.github/workflows/gate.yml`, `agent-os/product/mission.md`, `agent-os/product/tech-stack.md`,
`agent-os/specs/2026-11-05-1733-bootstrap-shape-spec-gate-ci-docs/{plan,shape,standards,references}.md`
and `verification/{gate-run,gate-negative-tests,ci-negative-test}.txt`.
Changed: `.claude/commands/agent-os/shape-spec.md`, `README.md`.
Untouched: everything under `agent-os/standards/`, `scripts/sync-standards.sh`, `pyproject.toml`,
`src/`, the other four commands.

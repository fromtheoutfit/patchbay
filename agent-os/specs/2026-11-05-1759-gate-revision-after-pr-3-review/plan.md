# Revision after the review of PR 3: the gate's files, CI, the harness and the docs

## Context

PR 3 (branch `feature/1-bootstrap-shape-spec-claudemd-gate-with-the-drift-check-ci-readme-changelog`,
commit `6c91362`) carries the bootstrap spec. The owner's review comment on it lists ten findings;
the hosted `gate` run 42124784656 passed on that commit. This revision addresses all ten as the
review recommends, as a new spec whose feature is the gate (every gate file changes: `gate.sh`,
the harness, the workflow, the gate task in `shape-spec.md`), on the same branch, so PR 3 carries
the fix. Shaped 2026-11-05 in plan mode with the customized `/agent-os:shape-spec`.

Owner's answers: all ten findings, in a new spec folder; step 1's file list is git's (tracked plus
untracked-not-ignored), bash scripts parsed and any other file refused by name; references are the
sibling's PR 9 revision record and this repository's gate files; all five base standards, the
snapshot unchanged; no visuals; product context aligned (tech-stack.md: gate tools pinned in
`gate.sh` and run through `uvx`, so setup-uv returns when a step first uses it); the first spec's
transcripts stay as committed, its `shape.md` gets one pointer line, CHANGELOG gets a second entry.

Base standards in force, read-only: `agent-os/standards/base/process/*.md`. No file there, no
`base:` entry and not `scripts/sync-standards.sh` is edited.

## Dispositions (the table goes into the new spec's plan.md)

| # | Finding | Disposition |
|---|---|---|
| 1 | `NEG=$(cd "$(mktemp -d)" && pwd -P)`: an empty `mktemp` result makes the EXIT trap delete the repository | Fix: `NEG=$(mktemp -d) \|\| exit 2`; refuse empty, not a directory, equal to or inside `$REPO`; resolve with `pwd -P` after; trap `rm -rf "${NEG:?}"`. Shown by a note in the transcript (the guard's lines), not a negative test that empties TMPDIR. |
| 2 | `find scripts -type f` parses .DS_Store, swap files, any non-bash file | Owner: list with git (tracked + untracked-not-ignored under `scripts/`, as the sync script reads `base/`); a `*.sh` or bash-shebang file is parsed; any other file fails the step by name; outside a git work tree the step fails by name; a tracked file missing from disk fails by name. `.DS_Store` added to `.gitignore`. Test g. |
| 3 | Harness ignores setup failures and asserts no exit status | Fix: `mk` fails hard (`\|\| die`); `run <case> <expected> <cmd...>` prints `exit=N` and, on a mismatch, `UNEXPECTED exit N (expected M)`; a counter makes the harness exit 1 at the end naming the count; the summary line is the last line of the transcript. |
| 4 | CI checks out `patchbay-standards` at `main`, full history | Fix: a `run` step reads `.version` into `$GITHUB_OUTPUT` and the checkout takes it as `ref`, default depth; no `fetch-depth: 0`. `standards-sync.md` names this form. Test j replays the pin step with `GITHUB_OUTPUT` pointed at a scratch file and shows the sha it wrote. |
| 5 | No negative test for the script and extra-file checks of step 2 | Fix: test e (a comment appended to the copy's `scripts/sync-standards.sh`: `script differs`, exit 1) and f (an untracked `base/process/extra.md`: `extra`, exit 1). |
| 6 | setup-uv installed, no step uses it | Fix: the step is removed; the header says the toolchain spec adds it, pinned, when a step first runs `uvx`. The first spec's recorded deviation closes. |
| 7 | Hosted run not recorded | Fix: run 42124784656, `success`, on `6c91362` (the workflow before this revision) recorded at the end of the new spec's `ci-negative-test.txt`, with a line that the revised workflow's run is read back by the owner after the push. |
| 8 | Step 5b omits the reserved `root` section | Fix: one sentence: a key in the reserved section `root` resolves to `agent-os/standards/<key>.md`. |
| 9 | `pyproject.toml` description is the placeholder | Fix: the README's one-liner. `uv.lock` does not carry the description, so it is unchanged. |
| 10 | Step 5a's heading name differs from the template's | Fix: Step 5a says `## Core Architecture (Non-Negotiable)`, the template's heading. |

## Spec folder

`agent-os/specs/2026-11-05-1759-gate-revision-after-pr-3-review/` with
`plan.md`, `shape.md`, `standards.md`, `references.md`, `verification/`.

## Task 1: Save spec documentation

- `plan.md`: this plan, the table included.
- `shape.md`: `## Core Architecture (Non-Negotiable)` ("None yet; see Step 5a"); `## Scope` (the
  review on PR 3, ten findings, the hosted run); `## Shaping answers` (Steps 1–5 as above);
  `## Decisions`, first "The review on PR 3 is the scope", then: step 1's list and filter (owner's
  choice, why), the exit contract unchanged, the harness asserts, CI pinned by `.version`, setup-uv
  removed, a new spec folder for the revision on the same branch; `## Context`; `## Standards
  Applied` (all five, what each governs here); `## Verification Gate` and `## Standards
  Retrospective` filled in Task 8.
- `standards.md`: the snapshot paragraph and the five standards, same bytes as the first spec's.
- `references.md`: the sibling's sync spec (`plan.md` table, `shape.md` "Revision after review",
  its harness's assertions and test j), and this repository's `scripts/gate.sh`,
  `scripts/gate-negative-tests.sh`, `.github/workflows/gate.yml` as committed at `6c91362`.
- First spec's `shape.md`: one line after its Verification Gate heading's paragraph: "Revised
  after the review of PR 3 in `agent-os/specs/<new folder>/`; the transcripts here are the first
  round's."

## Task 2: `scripts/gate.sh` (findings 2)

Step 1 becomes "every shell script under `scripts/`, as git lists them":

- `git rev-parse --show-toplevel` must succeed, else `fail 1/2 "not a git work tree"`.
- List: `git -c core.quotePath=false ls-files -z -- scripts` plus
  `ls-files -z --others --exclude-standard -- scripts`, `LC_ALL=C sort -zu`.
- Each path: not on disk → `fail` "tracked but missing from the disk"; name ends in `.sh` or first
  line matches `^#!.*bash` → `bash -n` or `fail` "does not parse"; else `fail` "not a shell script;
  only shell scripts live under scripts/".
- Banner `1/2  bash -n on every shell script under scripts/ (tracked or untracked, not ignored)`.
- Header: the list rule and what is refused; everything else unchanged (exit contract, pins
  comment, step 2, closing line).

## Task 3: `.github/workflows/gate.yml` (findings 4, 6)

Steps: checkout this repository into `patchbay/`; `- id: pin` `run: echo
"sha=$(tr -d '[:space:]' < patchbay/agent-os/standards/base/.version)" >> "$GITHUB_OUTPUT"`;
checkout `fromtheoutfit/patchbay-standards` with `ref: ${{ steps.pin.outputs.sha }}`, `path:
patchbay-standards`, `persist-credentials: false`, no `fetch-depth`; `run: scripts/gate.sh` with
`working-directory: patchbay`. No setup-uv. Header rewritten: the pin step is the form
`standards-sync.md` names, no runner is installed because no step assumes one, the toolchain spec
adds setup-uv pinned when it first runs `uvx`; the rest as before (pins by commit, timeout, no
credential, no cache).

## Task 4: `scripts/gate-negative-tests.sh` (findings 1, 3, 5, and tests for 2 and 4)

- Scratch dir guard per finding 1; `die` helper; `mk` with `|| die` on every command.
- `run <case> <expected> <cmd...>`: as today plus the assertion and the `unexpected` counter;
  final summary `N runs, M unexpected`, exit 1 when M > 0.
- Cases: a (unparsable `broken.sh`, exit 1), b (byte under `base/`, exit 1), c (hand-edited entry,
  exit 1), d (sibling missing, exit 1), e (sync script edited: `script differs`, exit 1), f
  (untracked `base/process/extra.md`: `extra`, exit 1), g (step 1's list: an ignored
  `scripts/.DS_Store` passes, exit 0; a tracked `scripts/notes.txt` refused by name, exit 1; a
  tracked script deleted from disk refused, exit 1; `.git` removed, refused by name, exit 1),
  u (usage exit 2 twice, clean copy exit 0), j (CI replay: the pin step run with `GITHUB_OUTPUT`
  set to a scratch file and its content printed, the checkouts not run, the gate step from
  `patchbay/`; j1 passes, j2 with `broken.sh` fails at the gate step, exit 1). Default a–g and u;
  `all` adds j. Header lists them.

## Task 5: `.claude/commands/agent-os/shape-spec.md` (findings 8, 10; gate task for 2)

Step 5a names `## Core Architecture (Non-Negotiable)`; Step 5b adds the `root` sentence; the gate
task's step 1 reads "every shell script under `scripts/`, as git lists them (tracked or untracked,
not ignored), must parse; any other file there fails the step"; Step 8's summary and the `shape.md`
template's Verification Gate paragraph say the same in short.

## Task 6: `CLAUDE.md`, `README.md`, `.gitignore`, `pyproject.toml` (findings 2, 6, 9)

- `CLAUDE.md` Specs: step 1's wording; CI no longer "installs uv" (it never said so; verify).
- `README.md` gate section: step 1's wording and rule; the sentence about the toolchain spec adds
  "and installs uv in CI then".
- `.gitignore`: `.DS_Store` appended under a `# Finder` comment.
- `pyproject.toml`: `description = "Headless control of software instruments from Python: the
  contracts, host and CLI that patchbay-<instrument> adapters plug into."`

## Task 7: `CHANGELOG.md`

Under `[Unreleased]`: a `### Changed` entry for the revision (new spec folder, PR 3's review, each
finding's fix in a clause: the file list, the pinned checkout, setup-uv removed, the harness guard
and assertions and tests e, f, g, the hosted run recorded, Step 5a/5b, the description). The first
entry's bullets that no longer describe the tree are rewritten (workflow: no uv, checkout at the
pinned commit; gate.sh: the list rule; harness: the cases).

## Task 8: Verification gate (always last)

1. Transcripts after the last edit to any gate file: `scripts/gate-negative-tests.sh` →
   `verification/gate-negative-tests.txt`; `scripts/gate-negative-tests.sh j` →
   `verification/ci-negative-test.txt`, then the hosted run 42124784656 (`success`, `6c91362`,
   the previous workflow) appended with the note for the owner. First line of each: date, branch.
2. `scripts/gate.sh` on the tree as the last act → `verification/gate-run.txt`, exit 0.
3. **Docs**: README, CLAUDE.md, the three headers, shape-spec.md, pyproject, the first spec's
   pointer line, and `verification-gate.md` / `standards-sync.md` "In a consuming project" against
   the shipped workflow (pinned checkout) and script. Recorded.
4. **Version**: the Changed entry; 0.1.0 unchanged. Recorded.
5. **Standards retrospective**: four questions on the diff. Expected proposals (base):
   `verification-gate.md` — the harness guards its scratch directory (the sibling's harness has
   the same `mktemp` line, finding 1 applies there) and asserts each expected status, exiting
   non-zero on a mismatch; step 1's file list is git's with the shell-script filter (the sibling
   uses `find`); the exit contract, restated from the first spec. Deviation closed: setup-uv.
6. Stop; print `git status --short`. No stage, commit, PR or push.

## Files

New: the spec folder. Changed: `scripts/gate.sh`, `scripts/gate-negative-tests.sh`,
`.github/workflows/gate.yml`, `.claude/commands/agent-os/shape-spec.md`, `CLAUDE.md`, `README.md`,
`CHANGELOG.md`, `.gitignore`, `pyproject.toml`, the first spec's `shape.md` (one line).
Untouched: `agent-os/standards/`, `scripts/sync-standards.sh`, `src/`, `uv.lock`, product docs.

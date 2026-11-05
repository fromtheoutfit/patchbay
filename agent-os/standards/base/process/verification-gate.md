# Verification Gate

The gate is the definition of done in every patchbay repository. It is the final task of every spec,
included without asking, whether or not `/agent-os:shape-spec` shaped the work, and a spec is not
complete until every step of it passes. A spec with a red step, a skipped step or an unrecorded
retrospective is unfinished work, however small the change; a one-file fix is exactly the kind of
work that quietly invents a pattern, so the gate runs on it too.

This standard fixes the shape of the gate: what every repository's gate does and in what order.
The runnable step list is each repository's own, named in its `scripts/gate.sh` and in the gate
task of its `shape-spec.md`; this standard names no step and no tool. The standard that names a
repository's steps is cited here when it ships.

## One script

- **`scripts/gate.sh` runs every runnable step, in a fixed order, as one command**, and exits
  non-zero at the first step that fails. Later steps do not run: a failing step 1 is reported
  before step 2 has a chance to pass, so a green run means every step ran and every step passed.
- **Every step reports by name.** Each step prints a numbered banner, and what passed is named
  (`ok   <what>`) or what failed is named with its reason and the offending path; a bare exit code
  is not a report. The script ends by naming the step that follows it, so a reader of the
  transcript knows the run was not the whole gate.
- **The script runs from the repository root** wherever it is invoked from, and assumes nothing
  the repository does not already provide.

## Pinned

- **A tool's version is pinned in the script**, in one named variable per tool, with the date it
  was published beside it. The pinned tool is run through a runner that executes it without
  installing it into the project, and the runner is one the repository already assumes. Nothing
  else is installed to run the gate. A pin is bumped deliberately, in the gate's own spec, and
  the gate rerun.
- **A rule set lives in a versioned config file**, at the repository root, named in the script;
  a config the tool cannot parse fails the step. A key the tool does not know is not refused, so
  the spec that adds or changes the config shows a changed value applied, in a negative test. The
  file's header says which step reads it and that it changes only in the gate's own spec.

## The fixed order

The runnable steps come first, in the order the script runs them. Three judgment steps follow, in
this order, and nothing in the script runs them; the script's closing line names them, and the gate
task of `shape-spec.md` lists them after the runnable steps:

- **Docs**: the documentation the change touches reads true after it. The README, the repository's
  `CLAUDE.md`, the header comments and pointers in the files changed, and every standard that names
  them are read against the shipped change, and what was checked is recorded in the spec's
  `shape.md`.
- **Version**: the change is recorded under `[Unreleased]` in `CHANGELOG.md`, and the version is
  bumped where a repository has one. Recorded in `shape.md`.
- **The standards retrospective**, per `base/process/standards-retrospective.md`: the four
  questions answered against the diff, the answer recorded in the spec's `shape.md` under
  `## Standards Retrospective`. "No changes" is valid; silence is not. It is always last.

A spec whose `shape.md` records the green run but not the three judgment steps has not finished the
gate.

## A failing step is fixed at its cause

- **The cause is fixed and the whole gate rerun from step 1.** A fix that lets the step pass
  without fixing what it reported is not a fix. Skipping the step, loosening the rule set,
  excluding the file it named or editing the script to pass each change a gate file, which the
  section below forbids inside a spec; a suppression comment placed in the file the step named
  loosens the rule for that file alone and is reviewed as the loosening it is.
- **A step that cannot pass on the shipped tree is a defect in the tree**, not a reason to bypass
  the step. The first spec in `patchbay-standards` added the one blank line `README.md` lacked
  after its heading rather than exclude the file; that is the whole of the rule.

## Every step that can fail is proven to fail

- **A step is shown to discriminate by a negative test**: a copy of the tree, broken in one way,
  that must fail that step with the named reason and the expected exit status, with the steps after
  it never reached. A step that has never been seen to fail is not known to check anything.
- **The spec that adds or changes a step ships its negative test**, and keeps the transcript in
  that spec's `verification/` folder. The tests are a script in the repository beside the gate's,
  not run by the gate, so a rerun is the same test. They run on a temporary copy outside the
  tree, never on the tree itself, and are rerun whenever the gate's files change.
- **Every spec keeps its green run** as `verification/gate-run.txt` in its spec folder, so the
  claim "gate green" has the transcript beside it. The first line of the transcript gives the date
  and the branch the run was made on, and the run is the last thing done before the work is
  handed over: an edit after the run is not covered by it. A transcript recorded before this rule
  stays as it was recorded.

## CI

- **The gate's workflow runs the same script and nothing else.** One workflow for the gate, one
  job, on every pull request and every push to the default branch: check out the repository,
  install the runner the script already assumes, run `scripts/gate.sh`. No linter, formatter,
  matrix or check is configured in it; a step the script does not run is not a gate step, and a
  check CI runs that the script does not is a gate a developer cannot run. A repository may have
  other workflows for other work; this rule is about the gate's. The judgment steps are never run
  by a machine.
- **Every action is pinned to a commit**, the full SHA in `uses:` with the tag it was taken from
  in a comment beside it, and the runner's own version is pinned through the action's input, so CI
  runs what the gate was proven with. The image is a named release, not `latest`. The job has a
  timeout, keeps no credential in the checkout and caches nothing, so it has no moving part beyond
  the script. A pin is bumped deliberately, in the gate's own spec, and the workflow rerun.
- **The workflow fails when the script fails**, because the script is one `run` step and a `run`
  step that exits non-zero fails the job. Before any push, the spec that adds or changes the
  workflow replays the job's `run` steps, read from the workflow file, on a copy of the tree with
  one script broken, and shows the job stops at that step with its exit status. That proves the
  job's control flow on the toolchain at hand, not the hosted run: the hosted run on the pull
  request is the proof of the workflow itself, and the spec records its run id and conclusion in
  `verification/` once it exists. What the script does on the hosted toolchain is the script's
  own portability, proven by its negative tests.

## The gate's own files change only in their own spec

- **The gate script, every script it runs, the rule-set config, the CI workflow and the gate task
  text in `shape-spec.md` are never changed as a side effect of a spec whose feature is something
  else**, and never from inside a retrospective. A gate that rewrites its own terms during the
  process it governs is what this rule exists to prevent.
- **A change to the gate is its own spec**, whose feature is the gate: on its own branch, with the
  owner, carrying the negative test for every step it adds or changes. A finding against a gate
  file made during some other spec is recorded in that spec's retrospective as a proposal and
  waits for the gate's spec.

## In this repository

The runnable steps are three: every script under `scripts/` parses, the standards under `base/`
and `README.md` lint clean against the pinned rule set, and `index.yml` lists exactly the tracked
files under `base/`. `scripts/gate.sh` names the tool, its pin and its config.
`scripts/check-index.sh` is the third step: it runs only in a git work tree, reads the tracked
list with `git ls-files`, refuses an untracked file under `base/` and a tracked one missing from
the disk, sorts every list after its last transform and checks both sorted before `comm`, and
holds `agent-os/standards/index.yml` to be a symlink to `../../index.yml`.
`scripts/gate-negative-tests.sh` holds every negative test, fifteen for the gate's scripts (a to
n except j), eight for `scripts/sync-standards.sh` (o to v, `base/process/standards-sync.md`) and
the CI replay (j), and is parsed by step 1, not run by the gate. `.github/workflows/gate.yml` is the
gate's workflow, pinned to `actions/checkout` v7.0.1 and `astral-sh/setup-uv` v10.3.3 by commit and
to uv 0.13.7, on `ubuntu-24.04` with a ten-minute timeout, no persisted credential and no cache.
Every spec folder under `agent-os/specs/` holds its `verification/gate-run.txt`; the spec that
built the gate holds its six negative tests as recorded, the spec that last changed the harness
holds the current transcripts, j's included, and the gate spec (issue #3) holds the hosted runs that
proved the workflow, by id.

## In a consuming project

This standard is synced in as `agent-os/standards/base/process/verification-gate.md`. The
project's `scripts/gate.sh` runs its own step list in this shape; its `shape-spec.md` lists those
steps in the gate task, followed by Docs, Version and the standards retrospective; its gate
workflow runs the script and nothing else; its `CLAUDE.md` names the script as the definition of
done. `scripts/sync-standards.sh --check` is one of its steps, and that script is a gate file the
sync itself replaces from the pinned commit, never a hand edit; its gate workflow checks
`patchbay-standards` out beside the project under the workspace, at the commit in
`agent-os/standards/base/.version` (`base/process/standards-sync.md`).

# Verification Gate

The gate is the definition of done in every patchbay repository. It is the final task of every spec,
included without asking, whether or not `/agent-os:shape-spec` shaped the work, and a spec is not
complete until every step of it passes. A spec with a red step, a skipped step or an unrecorded
retrospective is unfinished work, however small the change; a one-file fix is exactly the kind of
work that quietly invents a pattern, so the gate runs on it too.

This standard fixes the shape of the gate: what every repository's gate does and in what order.
The runnable step list is each repository's own, named in its `scripts/gate.sh` and in the gate
task of its `shape-spec.md`; this standard names no step and no tool. A consuming project's tool
steps, and the order they run in, are `base/python/toolchain.md`'s.

## One script

- **`scripts/gate.sh` runs every runnable step, in a fixed order, as one command**, and exits 1
  at the first step that fails, after a line on stderr naming the step and its reason,
  `FAIL  step N/M: <reason>`, whatever status the tool returned. Later steps do not run: a failing
  step 1 is reported before step 2 has a chance to pass, so a green run means every step ran and
  every step passed. The script takes no argument; any argument is usage, the usage line on stderr
  and exit 2 with no step run, and a script that cannot enter the repository root says so on
  stderr and exits 2 likewise. A transcript or a wrapper then has three statuses to tell apart: 0,
  every step passed; 1, a step failed and is named; 2, the script was not run as the gate.
- **Every step reports by name.** Each step prints a numbered banner, and what passed is named
  (`ok   <what>`) or what failed is named with its reason and the offending path; a bare exit code
  is not a report. The script ends by naming the step that follows it, so a reader of the
  transcript knows the run was not the whole gate.
- **A step that installs its pinned tools fails as itself.** The install is checked on its own,
  before any tool checks the tree, with a reason of its own: a lockfile that no longer matches its
  manifest, a manifest or lockfile the runner cannot read, a package that will not build, a runner
  missing from `PATH` or not at its pinned version, a pin that names no published version. A
  failed install is then never reported as the first tool's finding, and each tool's reason is
  about that tool alone. A tool run afterwards under the runner's locked mode repeats a check the
  install has passed.
- **A step that reads files from the tree reads the files git lists**: the tracked files plus the
  untracked ones git does not ignore, at the top of a git work tree that is the repository root.
  An ignored stray such as `.DS_Store` is never seen, and a file a spec adds before it is staged
  is. `find`, and a tool that walks a directory without reading `.gitignore`, see the stray, so a
  local run and CI's clean checkout can disagree. The step takes one of three forms:
  - **It reads git's list**, `git ls-files --cached --others --exclude-standard`, one call for
    both sets unless the step treats them apart, `-z` keeping paths verbatim (a list read by line
    takes `core.quotePath=false`), and checks each path on the disk: a listed path missing from the
    disk, or a symlink to nothing, fails the step by name. That clause binds this form; a tool that
    walks the disk is not asked to see a file that is not there, since an earlier step that lists
    the same files checks each one.
  - **It runs a tool that reads `.gitignore` itself** and is given no path git ignores.
  - **It runs a tool that walks a directory and reads files no list given to it holds back**: the
    step first refuses, by name, any file git ignores there that the tool would read, so its walk
    reads only what git lists. pytest loads the `conftest.py` of every directory it collects from,
    and one at the root, whatever `--ignore` names.
- **The first step makes the forms agree.** It asks git two things and compares no paths: that
  this directory is inside a work tree, `git rev-parse --is-inside-work-tree` printing `true`, and
  that it is the top, `git rev-parse --show-cdup` empty. `--show-cdup` alone prints nothing in
  `.git/` and in a bare repository too, where `--is-inside-work-tree` prints `false`. A path typed
  in another case, or spelled `C:/` rather than `/c/`, names the same directory, and comparing
  `pwd -P` with `--show-toplevel` as strings refuses the real root. A tree whose work-tree top is
  not the repository root, a copy without `.git` inside another repository's work tree or under its
  `.git/` included, fails the step by name: never listed against the outer repository, never a bare
  exit. It then refuses every tracked file a committed `.gitignore` matches under the paths the
  gate's listings read, `git ls-files --cached --ignored --exclude-per-directory=.gitignore --
  <those paths>`, naming each under one FAIL line: a file force-added, or added before its
  pattern, is in git's list though the repository says it is ignored, and a tool that reads
  `.gitignore` itself skips it, so with none every form reads one set of files. Only committed
  `.gitignore` files count, so every clone of a commit gets the same answer: `.git/info/exclude`
  and the global excludes file are the machine's, and a file no step reads never fails the gate.
  The fix is a `!` pattern, or untracking the file; a `!` pattern cannot re-include a file under an
  ignored directory, so the directory's contents are ignored (`dir/*`) rather than the directory.
- **A listing git cannot make fails its step by name.** Each listing is written to a file and git's
  own status checked: `git ls-files -z … > <file>.raw && LC_ALL=C sort -zu <file>.raw > <file>`,
  and the step fails by name when that fails ("git could not list the files under scripts/").
  Neither a pipe nor a process substitution keeps git's status: without `pipefail` a pipe's is the
  last command's, and a process substitution's is lost either way, so a corrupt index otherwise
  reads as an empty listing. `-u` lists each path once, since a path in merge conflict is in the
  index once per stage. The files go in a directory `mktemp -d` makes, checked before it is used and
  removed on exit; a step that cannot make it fails by name.
- **The script runs from the repository root** wherever it is invoked from, and assumes nothing
  the repository does not already provide.

## Pinned

- **A tool's version is pinned exactly, in one place, with the date it was published beside
  it.** In a repository with no package manifest the pin is in the script, one named variable
  per tool, and the tool runs through a runner that executes it without installing it into the
  project. In a repository with a manifest the pin is in the manifest's development dependency
  group, exact, and resolved in the lockfile, and the gate runs every tool under the runner's
  locked mode: a pin edited without re-locking fails the step rather than rewriting the lockfile,
  so the gate writes nothing but ignored files and caches. A type checker or a test runner needs
  the project installed, which a runner that installs nothing cannot give it. The runner is one
  the repository already assumes, and nothing else is installed to run the gate. A pin is bumped
  deliberately, in the gate's own spec, and the gate rerun. The pins are gate files either way: in
  the script, as part of it; in a manifest, the pins of the tools the gate runs and what the
  lockfile resolves for them, while the group's other entries, a test library a feature spec adds
  among them, are the project's.
- **The runner's own version is pinned too.** Where the manifest can pin it and the runner then
  refuses any other version on every command that reads the project's settings, it is pinned
  there, once: a local run and CI use the same runner, and CI reads the version from the manifest,
  as "CI" below says.
  Otherwise CI pins it, through the action's input, and a local run uses the runner on `PATH`.
- **A rule set lives in a versioned config file at the repository root, named in the script, or
  in the manifest's tool sections.** In the second case those sections, with the tool pins above,
  are the gate's, and the rest of the manifest is the project's, changing in any spec; the file's
  header says which is which. Either way a config the tool cannot parse fails the step, and
  the header says which step reads the rule set and that it changes only in the gate's own spec.

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
- **A rule set and a pin are each shown to be read, and the install to fail as itself.** A rule
  set is shown read by three cases: a changed value applied, so the clean tree now fails the
  step, and a value the tool cannot use and a file it cannot parse, each failing the step by name.
  Not every tool refuses a key it does not know: pymarkdown under `--strict-config` takes a
  misspelled key as absent and applies the default, where pytest under `--strict-config` refuses
  one (exit 4). So the changed value, which every tool applies, is what shows the file is read. A
  pin is shown read by a version that cannot install: in a lockfile, a pin edited and the
  lockfile left; in the script, a version never published; for a runner the manifest pins, a
  version that is not the one running. Each fails the install by its own reason before any tool
  runs, and the case where the first tool fails shows the install passing first.
- **The spec that adds or changes a step ships its negative test**, and keeps the transcript in
  that spec's `verification/` folder. The tests are a script in the repository beside the gate's,
  not run by the gate, so a rerun is the same test. They run on a temporary copy outside the
  tree, never on the tree itself, and are rerun whenever the gate's files change, and whenever a
  spec adds, removes or renames a file under a directory the tests copy, since a case can rest on
  what that directory holds.
- **A case states what it rests on.** A case whose expectation depends on what a copied directory
  holds sets the whole of that directory, not a part of it. A case that removed some files from
  its copy of `base/` and wrote an index for the rest went stale when a later spec added a standard
  there, and nobody saw it, since that spec changed no gate file and reran no test. A case that
  needs one named file there stops the harness by name when the file is absent.
- **The harness proves itself as it goes.** Its scratch directory comes from `mktemp -d` under a
  hard failure, is refused when empty or when it lies at or under the repository, and only then is
  the trap that removes it set, so a harness whose `mktemp` failed can remove nothing in the tree.
  A setup step that fails stops the harness by name (exit 2) rather than letting a case fail for
  the wrong reason. Every run names the status it expects and prints the one it got, and a run
  that expects a failure also names the reason its output must hold, the failing line with its
  path where one is printed: a script that gives one status for several reasons cannot otherwise
  be told apart from itself with the guard under test deleted. A run that fails at a step also
  holds its output to no later step's banner, so the steps after it are shown never reached, not
  assumed, and a passing run may name lines its output must hold, in order. The named lines are
  found one by one and say nothing of what else was printed, so a case whose reason is the whole
  of what a step must report also asserts that nothing else is reported: the entries the step
  lists are exactly the ones named. A case that says a line is printed once holds it to an exact
  count. A mismatch of any of these is marked `UNEXPECTED`, and the harness exits 1 at the end
  naming the counts, so a transcript's last line says whether every case behaved and a case that
  passed when it should have failed, or failed for another reason, is never read as a pass.
- **A change to the harness's assertions is shown to discriminate, as a step is.** The proof is a
  copy with the guard under test deleted, or put back as it was, run through the cases that cover
  it, which must come back `UNEXPECTED` with the harness exiting 1; the transcript is kept in the
  spec's `verification/`. An assertion no mutation trips is not known to assert anything.
- **A kept transcript holds one run of the harness and ends on that run's count.** The last line
  says whether every case behaved only while it is that run's: a second run appended after it
  makes the last line the second run's. An earlier run kept as evidence, a failing run before a
  fix, goes in a file of its own.
- **Every spec keeps its green run** as `verification/gate-run.txt` in its spec folder, so the
  claim "gate green" has the transcript beside it. The first line of the transcript gives the date
  and the branch the run was made on, and the run is the last thing done before the work is
  handed over: an edit after the run is not covered by it. A transcript recorded before this rule
  stays as it was recorded.
- **A step that refuses an untracked file by design cannot pass on the tree before the owner
  stages it**, and an agent never stages (`base/process/ownership.md`). This repository's index
  check refuses an untracked file under `base/`, so a spec that adds a standard records two runs
  in `gate-run.txt`: the tree's, which fails that step naming the new file, and a green run on a
  scratch copy of the tree with the file git-added. The hand-over says the owner's `git add` turns
  the tree's run green.

## CI

- **The gate's workflow runs the same script, and checks nothing the script does not.** One
  workflow for the gate, one job, on every pull request and every push to the default branch:
  check out the repository, install the runner the script already assumes and, in a repository
  with a lockfile, the locked toolchain, as a step of its own from the project's directory, then
  run `scripts/gate.sh`. That install is the one the script's own install step makes, so a failure
  there is one the gate would report, met before the gate starts. No linter,
  formatter, matrix or check is configured in it; a step the script does not run is not a gate
  step, and a check CI runs that the script does not is a gate a developer cannot run. A
  repository may have other workflows for other work; this rule is about the gate's. The judgment
  steps are never run by a machine.
- **Every action is pinned to a commit**, the full SHA in `uses:` with the tag it was taken from
  in a comment beside it, and the runner's own version is pinned, so CI runs what the gate was
  proven with: through the action's input, or, where the manifest pins the runner, by the action
  reading it from the manifest in the project's directory, with no input, so the version is
  written once. A failed lookup is loud, not a drift: the action installs its latest runner,
  which the manifest's pin refuses at the locked install, its first command that reads the
  project's settings, unless it is the pinned version. The
  image is a named release, not `latest`. The job has a timeout, keeps no credential in the
  checkout, and caches nothing but what a key that changes with the lockfile holds: the same key
  restores what the same lockfile resolves to, and a changed lockfile misses it, so the cache is
  not a moving part. A repository with no lockfile has nothing to key a cache on and caches
  nothing. A pin is bumped deliberately, in the gate's own spec, and the workflow rerun.
- **The workflow fails when the script fails**, because the script is one `run` step and a `run`
  step that exits non-zero fails the job. Before any push, the spec that adds or changes the
  workflow replays the job's `run` steps, read from the workflow file, on a copy of the tree with
  one script broken, and shows the job stops at that step with its exit status. That proves the
  job's control flow on the toolchain at hand, not the hosted run: the hosted run on the pull
  request is the proof of the workflow itself, and the spec records its run id and conclusion in
  `verification/` once it exists. What the script does on the hosted toolchain is the script's
  own portability, proven by its negative tests.

## The gate's own files change only in their own spec

- **The gate script, every script it runs, the tool pins (in the script, or in a manifest's
  development group with what the lockfile resolves for them), the rule-set config (a file, or a
  manifest's tool sections), the CI workflow and the gate task text in `shape-spec.md` are never
  changed as a side effect of a spec whose feature is something else**, and never from inside a
  retrospective. A gate that rewrites its own terms during the process it governs is what this
  rule exists to prevent.
- **A change to the gate is its own spec**, whose feature is the gate: on its own branch, with the
  owner, carrying the negative test for every step it adds or changes. A finding against a gate
  file made during some other spec is recorded in that spec's retrospective as a proposal and
  waits for the gate's spec.

## In this repository

The runnable steps are three: every shell script under `scripts/` parses, the Markdown files under
`base/` and `README.md` lint clean against the pinned rule set, and `index.yml` lists exactly the
tracked files under `base/`. `scripts/gate.sh` carries the exit contract above (tests e, f and x)
and names the tool, its pin and its config. Steps 1 and 2 read git's list from a temporary file,
each path once, and fail by name when git cannot list or no temporary directory can be made (tests
w and y). Step 1 first refuses a tree whose work-tree top is not the repository root, asked of git
(test w: the copy entered in upper case among it, one under another repository's `.git/` and one
in a bare repository), then every tracked file a committed `.gitignore` matches under `scripts/`,
`base/` and `README.md`, the paths its listings read (test y), then parses a file ending in `.sh`
or starting with a bash shebang; any other file fails the step by name, since only shell scripts
live under `scripts/` (test w). Step 2 passes pymarkdown the `.md` files of its list, since
pymarkdown walks a directory without reading `.gitignore` (test y), and, before pymarkdown
lints, installs the pin as itself: `uvx` missing from `PATH`, or a pin `uvx` cannot install, fails
the step by name, and pymarkdown's own reason is about findings and the rule set it reads (tests z
and e). `uvx` has no form that installs without running, so the install
check runs `pymarkdown version`, which checks nothing in the tree, and a pymarkdown that will not
start fails there by the same reason. This repository has no package manifest, so pymarkdown's
pin is `PYMARKDOWN_VERSION` in the script, with its date, run through `uvx`, and the rule set is
`.pymarkdown.yaml`, shown read by a changed value applied and by an unparsable value and an
unparsable file each refused (test i). `scripts/check-index.sh` is the third step: it runs only in
a git work tree whose top is the repository root, asked of git as step 1 asks it (test m), reads
the tracked list with `git ls-files`, each path once (test h), and fails by name when git cannot
list (test m), refuses an untracked file under `base/` and a tracked one missing from the disk,
sorts every list after its last transform and checks both sorted before `comm`, and holds
`agent-os/standards/index.yml` to be a symlink to `../../index.yml`.
`scripts/gate-negative-tests.sh` holds every negative test, nineteen for the gate's scripts (a to
n but j, with c as c1 to c3, and w, x, y and z), eight for `scripts/sync-standards.sh` (o to v,
`base/process/standards-sync.md`) and the CI replay (j), in the harness shape above, and is parsed
by step 1, not run by the gate.
`.github/workflows/gate.yml` is the gate's workflow, pinned to `actions/checkout` v7.0.1 and
`astral-sh/setup-uv` v10.3.3 by commit and to uv 0.13.7 through setup-uv's input, there being no
manifest to read it from, on `ubuntu-24.04` with a ten-minute timeout, no persisted credential and
no cache, there being no lockfile to key one on; a local run uses the uv on `PATH`. Every spec
folder under `agent-os/specs/` holds its `verification/gate-run.txt`; the spec that built the gate
holds its six negative tests as recorded, the spec that last changed the harness (the revision
after the review of PR 23) holds the current transcripts, j's included, with the mutations that
show its guards covered, and the gate spec (issue #3) holds the hosted runs that proved the
workflow, by id.

`scripts/gate.sh` here and in a consuming project share one skeleton: the `cd` and usage checks,
the `step`, `fail`, `git_list`, `listed`, `fail_list` and `present` helpers, step 1 with its root
guard, its temporary directory and its refusal of a tracked file a `.gitignore` ignores, and the
closing line. They differ only in their step lists, the pins those steps need and the paths each
spells from its root, the refusal's pathspec among them. A spec that changes the skeleton here
records the `diff -u` against a consuming project's `scripts/gate.sh` in its `verification/`, and
the project takes the change in its own gate spec after the sync that brings this standard in; the
revision after the review of PR 23 holds the current diff, against patchbay at `3f910d8`, which
names the hunks patchbay takes.

## In a consuming project

This standard is synced in as `agent-os/standards/base/process/verification-gate.md`. The
project's `scripts/gate.sh` runs its own step list on the skeleton above, with the exit contract
and the same first step: the work-tree top refused unless git says it is the root, a tracked file
a committed `.gitignore` matches refused under the paths its listings read, then every shell
script under `scripts/` parsed as git lists them, a file ending in `.sh` or starting with a bash
shebang, any other file refused by name. Every later step that reads files from the tree reads the
files git lists, in one of the three forms above.
Its `shape-spec.md` lists those steps in the gate task, followed by Docs, Version and the standards
retrospective; its gate workflow runs the script and checks nothing the script does not; its
`CLAUDE.md` names the script as the definition of done. `scripts/sync-standards.sh --check` is one
of its steps, and that script is a gate file the sync itself replaces from the pinned commit, never
a hand edit; its gate workflow checks `patchbay-standards` out beside the project under the
workspace, at the commit in `agent-os/standards/base/.version` by the pin step
`base/process/standards-sync.md` names, and its negative tests stand the sibling up by the fixture
named there.

A consuming project is a uv package, with a manifest and a lockfile, so its gate takes the
manifest's forms above. Its tools are pinned exactly in the `[dependency-groups] dev` section of
`pyproject.toml`, each with its publish date, resolved in `uv.lock` and run as
`uv run --locked <tool>`. The `[tool.*]` sections of `pyproject.toml` are the gate's, holding its
rule set and, in `[tool.uv] required-version`, uv's own pin, and so are the tool pins in
`[dependency-groups] dev` with what `uv.lock` resolves for them; `[project]`, `[build-system]` and
the rest of `[dependency-groups]` are the package's, and the file's header says which is which.
The step that runs the first tool opens with `uv sync --locked`, which installs exactly what
`uv.lock` names and fails the step as the sync, with its own reason, on a stale lockfile, a
manifest or lockfile uv cannot read, a package that will not build or a uv that is not the
required version; the tools after it run under `--locked`. Its gate workflow installs uv with
`astral-sh/setup-uv` pinned by commit, its `working-directory` the project's checkout and no
`version`, so it reads `required-version` from `pyproject.toml` there, with its cache on and
`cache-dependency-glob: uv.lock`; then runs `uv sync --locked` from the project's directory as a
step of its own; then the gate.

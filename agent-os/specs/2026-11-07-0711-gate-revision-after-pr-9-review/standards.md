# Standards for the gate revision after the review of PR 9

The following standards apply to this work, as they read when the spec was shaped (before the
retrospective), at the commit pinned in `agent-os/standards/base/.version`
(`11ceffdbd088bfb753dc54efa198dcb1ad6af0c9`). Each section below is the synced file
`agent-os/standards/base/<key>.md`, verbatim. If this spec changed or proposed a change to any of
them, `shape.md`'s Standards Retrospective says which and why — this file is the snapshot, not
the current text. `base/python/toolchain` is the Step 5a core tier, included without asking; the
other four are feature-specific.

---

## base/python/toolchain

# Toolchain

Every patchbay Python package does each job with one tool and configures every tool in
`pyproject.toml`. This standard says which tool does which job, what each tool's configuration
says and in what order the gate runs them, and every rule names the file of a consuming project it
is verified against. It was written from patchbay (`fromtheoutfit/patchbay`) at `73a583a`, whose
toolchain spec and its revision after the review of patchbay PR 4 record each choice as a Decision
with its reason; the probes it cites are recorded by the spec of issue #4 in `patchbay-standards`.

Where a tool's pin lives, the locked mode the tools run under, uv's own pin in `[tool.uv]
required-version`, which sections of `pyproject.toml` are the gate's and which the package's, the
`uv sync --locked` that opens the first tool's step and how CI installs the toolchain are
`base/process/verification-gate.md`'s ("Pinned", "CI", "In a consuming project"). This standard
cites them and does not restate them.

## One tool per job

- **uv owns the environment, the dependencies, the lockfile and the build.** `uv.lock` is the one
  lockfile and is committed, `.gitignore` leaving its `uv.lock` line commented out, and no file of
  another installer exists: no `requirements*.txt`, no other lockfile, no `tox.ini`. Verified
  against `pyproject.toml` (`[build-system]`, `[tool.uv]`, `[dependency-groups]`), `uv.lock`,
  `.gitignore` and the tracked files.
- **ruff lints and formats**: `ruff check` is the linter and `ruff format` the formatter, and there
  is no black, isort, flake8 or pylint. **mypy checks the types. pytest runs the tests**, and
  hypothesis generates and shrinks the inputs of property tests, run by pytest with no step of its
  own. **pre-commit runs the hooks at commit**, and no gate step runs it. Verified against the
  `[dependency-groups] dev` section of `pyproject.toml`, whose comment beside each pin names its
  job, and the comment over `[tool.ruff]`.
- **Every tool runs as `uv run --locked <tool>`**, so each is the version `uv.lock` resolves, with
  the one rule set in `pyproject.toml`, and a lockfile that no longer matches a pin fails the
  command. Plain `uv run` re-locks instead: with a pin edited and `uv lock` not run, it rewrites
  `uv.lock` to the new pin and runs (probed). This holds of the gate's steps in `scripts/gate.sh`,
  the hook entries in `.pre-commit-config.yaml`, and the two commands a person runs for the hooks,
  `uv run --locked pre-commit install` and `uv run --locked pre-commit run --all-files`, which the
  project's `README.md` and the header of `.pre-commit-config.yaml` name. There is no exception.
  Verified against those three files and the probes.

## pyproject.toml is the only config file

- **Every tool is configured under `[tool.*]` in `pyproject.toml` and nowhere else**: no
  `setup.py`, `setup.cfg`, `requirements*.txt`, `tox.ini`, `.flake8`, `mypy.ini`, `pytest.ini` or
  `.ruff.toml`. Verified against the header of `pyproject.toml`, which says so, and the tracked
  files.
- **Two exceptions sit beside it, each for a reason.** `.pre-commit-config.yaml`, because
  pre-commit cannot read its hooks from `pyproject.toml`: it registers hooks and configures no
  tool, ruff's version being `uv.lock`'s and its rules `[tool.ruff]`'s, as its header says.
  `.python-version`, the interpreter uv chooses and fetches, which `uv sync` reads and `uv init`
  writes: it holds the floor (below) and nothing else. Verified against both files, the project's
  `README.md`, which says `uv sync` reads `.python-version`, and the probes.
- **`uv.lock` configures nothing**: it is the resolution of what `pyproject.toml` requires.
  Verified against `uv.lock`.

## The build

- **`[build-system]` is `requires = ["uv_build>=X.Y.Z,<X.(Y+1).0"]` with
  `build-backend = "uv_build"`, the range `uv init` writes, and the range contains the uv that
  `[tool.uv] required-version` pins.** uv then builds the package with the backend bundled in
  itself, in `uv build` and in the editable build `uv sync` makes. A bump of `required-version`
  inside the range changes nothing; a bump past its upper bound moves the range in the same spec,
  which is the gate's, since `[tool.uv]` is a gate file. Verified against `pyproject.toml`
  (patchbay: `uv_build>=0.13.7,<0.14.0` beside `required-version = "==0.13.7"`).
- **Outside the range, uv builds another way, and nothing fails online.** uv 0.13.7 uses its
  bundled backend when the range contains the running uv or a version its source declares
  compatible (`0.9.30`, `0.10.12`, `0.11.33`, `0.12.24`), the second with a warning, `does not
  contain the current uv version`. For any other range, and for a `==` that is not the running uv,
  it builds through PEP 517 with a uv_build package from the index: online that build succeeds,
  offline it fails. So the range is held by reading `pyproject.toml` in the spec that moves the
  pin, not by the gate. Verified against uv's source at `0.13.7` (`check_direct_build`) and the
  probes, offline and online, of `uv build` and `uv sync`.
- **The upper bound stays, and the pin is not a literal `==`.** uv_build follows uv's versioning
  policy, and uv's documentation gives the upper bound as what keeps the package building as new
  versions are released; a frontend other than uv, such as `python -m build`, always uses the
  uv_build package, a release the range admits. A `==` builds through PEP 517 from the index as
  soon as it is not the running uv, and the range is what `uv init` writes and what patchbay ships.
  Verified against `pyproject.toml` and the probes.
- **`[tool.uv.build-backend] module-name` names the import package when it is not the distribution
  name.** Without it uv_build looks for the module the distribution name gives and the build fails:
  patchbay's distribution is `patchbay-core`, its import `patchbay`, and without the key uv_build
  expects `src/patchbay_core/__init__.py`. Verified against `pyproject.toml`.
- **`license` is an SPDX expression, and `license-files` is stated**, `license-files = ["LICENSE"]`.
  uv_build applies no default license glob: a wheel built without the key carries
  `License-Expression` and no license text. Verified against `pyproject.toml` and patchbay's
  `verification/wheel-license.txt` in the spec of its PR 4 revision, the wheel before and after;
  patchbay's `tests/unit/test_package.py` holds the installed metadata to `License-File: LICENSE`
  at every gate run.

## Python 3.12 is the floor

- **The floor is stated in four places, with one value**: `requires-python = ">=3.12"` in
  `[project]`, `.python-version` (`3.12`), `target-version = "py312"` in `[tool.ruff]` and
  `python_version = "3.12"` in `[tool.mypy]`. The two tool keys are stated, so a rule set never
  silently follows a raised floor. Verified against `pyproject.toml` and `.python-version`.
- **The floor is the family's**: every patchbay package states 3.12. Raising it is a change to this
  standard first, landed in `patchbay-standards` by its own spec; from a project it starts as a
  proposal its retrospective sends upstream (`base/process/standards-retrospective.md`). Each
  project then raises it in the gate spec that follows the sync bringing that change in, changing
  all four places together, since two of them are `[tool.*]` sections. Verified against
  `pyproject.toml` and `.python-version`, which state the value this standard gives.
- **The code is written for the floor and nothing below it.** Under `select = ["ALL"]` and that
  `target-version`, ruff refuses a version branch for an interpreter below the floor (UP036) and an
  import from `typing_extensions` of a name `typing` has at the floor (UP035). A backport of a
  standard-library module, `tomli` for `tomllib`, is a dependency, and fails the Decision
  "Dependencies" below asks for, since the standard library can. Verified against `pyproject.toml`
  and the probes.

## Dependencies

- **Adding a dependency is a Decision in the spec that adds it**, in that spec's `shape.md`: what
  it does, why the standard library cannot, and its license. This holds for `[project]
  dependencies` and for every dependency group. Verified against the header of `pyproject.toml`,
  and patchbay's toolchain spec, whose Decisions give all three for each of its five dev tools.
- **A dependency is added by the spec that uses it**, never ahead of it. Verified against
  `pyproject.toml`: patchbay's `dependencies` is empty though its product stack names pydantic and
  typer, since nothing in it yet crosses a boundary or has a CLI.
- **Every entry of the dev group is pinned exactly, with the date it was published beside it.** The
  pins of the tools the gate runs are `verification-gate.md`'s; the group's other entries take the
  same form (patchbay's hypothesis, run by pytest, and pre-commit, run by no gate step). Verified
  against `[dependency-groups] dev` in `pyproject.toml`.

## ruff

- **`[tool.ruff]` states `target-version`, the floor, and `line-length = 100`**: wide enough that
  a typed signature or a pydantic field with its description stays on one line, narrow enough to
  read in a split editor and a GitHub diff. The width is the family's, as the floor is: changed
  here first, then in each project's gate spec after the sync that brings it in. Verified against
  `pyproject.toml`.
- **`[tool.ruff.lint]` selects every rule, `select = ["ALL"]`, and the ignore list is what the
  tree and ruff taught.** Run `ALL` over the tree with the list empty. A rule the tree trips is
  fixed in the code where the rule is right, and ignored only where it is wrong for the tree. A
  conflict ruff warns of, between two rules or between a rule and the formatter, is ignored too,
  so the choice is the project's and written down rather than ruff's and silent. One comment per
  entry says why. Nothing is listed from memory: a rule the tree has not tripped and ruff has not
  warned of is not ignored (patchbay's run gave neither ISC001 nor PLR2004, and it lists neither).
  Verified against `[tool.ruff.lint]` in `pyproject.toml`, its comment, and the probes.
- **patchbay's list has six entries, each for a reason that holds of any patchbay package**, and a
  package lists each when its own run gives it:
  - Conflicts ruff warns of. `D203` and `D213`: `ruff check` and `ruff format` warn that D203 and
    D211, and D212 and D213, are incompatible, and drop D203 and D213 themselves; the ignore makes
    the choice explicit, no blank line before a class docstring and a multi-line docstring's
    summary on its first line. `COM812`: `ruff format` warns that it conflicts with the formatter,
    which owns trailing commas.
  - Findings the tree trips. `CPY001`, on every file: the license is the repository's `LICENSE`,
    and a copyright header in every file is noise every diff pays for. Under `"tests/**"` in
    `[tool.ruff.lint.per-file-ignores]`, `S101`, since `assert` is how a pytest test states its
    expectation, and `INP001`, since `tests/` is a tree pytest collects from `testpaths`, not a
    package, and has no `__init__.py`.

  Verified against `pyproject.toml` and the probes.
- **A suppression on one line names its code, `# noqa: <code>`, never a blanket `# noqa`.** Under
  `ALL`, PGH004 refuses a blanket `# noqa` even where it suppresses a finding, and RUF100 refuses a
  `# noqa` whose code suppresses nothing. A suppression loosens the rule for that line and is
  reviewed as the loosening it is (`verification-gate.md`, "A failing step is fixed at its cause").
  patchbay has none yet. Verified against `select` in `pyproject.toml` and the probes.
- **The ignore list grows only in the gate's own spec**, `[tool.ruff]` being a gate file
  (`verification-gate.md`, "The gate's own files change only in their own spec").

## mypy

- **`[tool.mypy]` is `strict = true` over `files = ["src", "tests"]`**, so the tests are typed to
  the package's bar, with `python_version` the floor, `warn_unreachable = true`, since code the
  checker proves unreachable is a bug and strict does not turn it on, and `implicit_reexport =
  false` stated though strict implies it, so a name is exported only by `__all__` or an explicit
  `from x import y as y`. Verified against `pyproject.toml`.
- **An untyped third-party package gets its own override**: a `[[tool.mypy.overrides]]` block with
  `module = ["name.*"]`, `ignore_missing_imports = true` and a comment naming the package and why;
  never a global `ignore_missing_imports`. patchbay imports nothing untyped yet and has no
  override, and the rule is the comment in its `[tool.mypy]`. Verified against `pyproject.toml`.

## pytest and hypothesis

- **`[tool.pytest.ini_options]` is `testpaths = ["tests"]` and
  `addopts = "-q --strict-markers --strict-config"`**: `-q` because a person reads the gate's
  transcript, `--strict-markers` so an unregistered marker, a typo, fails rather than silently
  selecting nothing, and `--strict-config` so a key pytest does not know fails the run rather than
  being ignored with a warning. Verified against `pyproject.toml` and the probes.
- **Every marker is registered under `markers` with its meaning**: patchbay's `integration`,
  "needs a running instrument; not selected by the gate until a spec says so". Verified against
  `pyproject.toml`.
- **Nothing else is set until a spec needs it**: patchbay has no `filterwarnings` and no
  `xfail_strict`. Verified against `pyproject.toml`.
- **hypothesis has no section**: it reads no settings from `pyproject.toml`, its profiles are code,
  and its `.hypothesis/` directory is ignored. Verified against `pyproject.toml` and `.gitignore`.

## pre-commit

- **`.pre-commit-config.yaml` holds two `repo: local` hooks, in this order: `ruff check --fix`,
  then `ruff format`**, ruff's recommended order, since a fix can change the formatting. Each
  `entry` is `uv run --locked ruff …` with `language: system` and `types_or: [python, pyi]`, so the
  hook runs the gate's ruff, at the version `uv.lock` resolves, with the gate's rules: one pin and
  one rule set. The `ruff-pre-commit` mirror is not used, since it would state ruff's version a
  second time. Verified against `.pre-commit-config.yaml`.
- **Each hook sets `require_serial: true`**, since two `uv run` calls syncing the same `.venv`
  would race, and **`minimum_pre_commit_version` is the dev group's pre-commit pin**. Verified
  against `.pre-commit-config.yaml` and `pyproject.toml`.
- **The hooks run ruff and nothing else, never mypy or pytest**: a hook is for what a commit can
  fix in a second, and the gate is the check. The person committing installs the git hook once,
  with `uv run --locked pre-commit install`. Verified against `.pre-commit-config.yaml` and the
  project's `README.md`.

## The gate's tool steps

- **After the gate's first step and before `scripts/sync-standards.sh --check`, the gate runs one
  step per tool, in this order: `ruff format --check .`, `ruff check .`, `mypy`, `pytest`.**
  Format before lint, so a formatting failure is reported before a lint finding the formatter would
  have changed; lint before types, since it is faster and its findings cheaper; tests last among
  the tools, since a type error usually explains a failing test. hypothesis runs inside `pytest`, and pre-commit in no
  step. Each tool runs as `uv run --locked <tool>`, and the first tool's step opens with
  `uv sync --locked`, both `verification-gate.md`'s. Verified against `scripts/gate.sh`
  (patchbay: steps 2 to 5 of six).

## In this repository

`patchbay-standards` has no package: no `pyproject.toml`, no `uv.lock`, no Python under `src/` or
`tests/`. This standard does not apply here, and no file here verifies it. Its rules were read from
patchbay at `73a583a`; a spec that changes one reads it again from a consuming project's shipped
files, and reruns the probes a rule rests on. The one Python tool this repository's gate runs,
pymarkdown through `uvx`, takes the no-manifest form of `verification-gate.md`. Step 5a of this
repository's `shape-spec.md` lists this standard with the note that it applies to consuming
projects; a spec shaped here records it under "Core Architecture" as not applying and does not copy
it into `standards.md`.

## In a consuming project

This standard is synced in as `agent-os/standards/base/python/toolchain.md`. Every rule above is
the project's, verified against the project's own files it names. The project's `shape-spec.md`
lists it in Step 5a, the tier every spec includes without asking, with its full content in that
spec's `standards.md`.

---

## base/process/verification-gate

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
  Either it reads git's list, `git ls-files --cached --others --exclude-standard`, one call for
  both sets unless the step treats them apart, `-z` keeping paths verbatim (a list read by line
  takes `core.quotePath=false`), and checks each path on the disk; or it runs a tool that reads
  `.gitignore` itself and is given no path git ignores. An ignored stray such as `.DS_Store` is
  never seen, a file a spec adds before it is staged is, and a listed path missing from the disk,
  or a symlink to nothing, fails the step by name. `find`, and a tool that walks a directory
  without reading `.gitignore`, see the stray, so a local run and CI's clean checkout can
  disagree. A tree whose work-tree top is not the repository root, a copy without `.git` inside
  another repository's work tree included, fails the first step that lists by name: never listed
  against the outer repository, never a bare exit.
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
  A key the tool does not know is not refused, so the changed value is what shows the file is
  read. A pin is shown read by a version that cannot install: in a lockfile, a pin edited and the
  lockfile left; in the script, a version never published; for a runner the manifest pins, a
  version that is not the one running. Each fails the install by its own reason before any tool
  runs, and the case where the first tool fails shows the install passing first.
- **The spec that adds or changes a step ships its negative test**, and keeps the transcript in
  that spec's `verification/` folder. The tests are a script in the repository beside the gate's,
  not run by the gate, so a rerun is the same test. They run on a temporary copy outside the
  tree, never on the tree itself, and are rerun whenever the gate's files change.
- **The harness proves itself as it goes.** Its scratch directory comes from `mktemp -d` under a
  hard failure, is refused when empty or when it lies at or under the repository, and only then is
  the trap that removes it set, so a harness whose `mktemp` failed can remove nothing in the tree.
  A setup step that fails stops the harness by name (exit 2) rather than letting a case fail for
  the wrong reason. Every run names the status it expects and prints the one it got, and a run
  that expects a failure also names the reason its output must hold, the failing line with its
  path where one is printed: a script that gives one status for several reasons cannot otherwise
  be told apart from itself with the guard under test deleted. A run that fails at a step also
  holds its output to no later step's banner, so the steps after it are shown never reached, not
  assumed, and a passing run may name lines its output must hold, in order. A mismatch of any of
  these is marked `UNEXPECTED`, and the harness exits 1 at the end naming the counts, so a
  transcript's last line says whether every case behaved and a case that passed when it should
  have failed, or failed for another reason, is never read as a pass.
- **Every spec keeps its green run** as `verification/gate-run.txt` in its spec folder, so the
  claim "gate green" has the transcript beside it. The first line of the transcript gives the date
  and the branch the run was made on, and the run is the last thing done before the work is
  handed over: an edit after the run is not covered by it. A transcript recorded before this rule
  stays as it was recorded.

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
and names the tool, its pin and its config. Steps 1 and 2 read the files git lists as the rule
above says. Step 1 first refuses a tree whose work-tree top is not the repository root, then
parses a file ending in `.sh` or starting with a bash shebang; any other file fails the step by
name, since only shell scripts live under `scripts/` (test w). Step 2 passes pymarkdown the `.md`
files of its list, since pymarkdown walks a directory without reading `.gitignore` (test y), and,
before pymarkdown lints, installs the pin as itself: `uvx` missing from `PATH`, or a pin `uvx`
cannot install, fails the step by name, and pymarkdown's own reason is about findings and the rule
set it reads (tests z and e). `uvx` has no form that installs without running, so the install
check runs `pymarkdown version`, which checks nothing in the tree, and a pymarkdown that will not
start fails there by the same reason. This repository has no package manifest, so pymarkdown's
pin is `PYMARKDOWN_VERSION` in the script, with its date, run through `uvx`, and the rule set is
`.pymarkdown.yaml`, shown read by a changed value applied and by an unparsable value and an
unparsable file each refused (test i). `scripts/check-index.sh` is the third step: it runs only in
a git work tree whose top is the repository root, reads the tracked list with `git ls-files`,
refuses an untracked file under `base/` and a tracked one missing from the disk, sorts every list
after its last transform and checks both sorted before `comm`, and holds
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
after the review of PR 18, issues #13 and #15) holds the current transcripts, j's included, and
the gate spec (issue #3) holds the hosted runs that proved the workflow, by id.

`scripts/gate.sh` here and in a consuming project share one skeleton: the `cd` and usage checks,
the `step`, `fail`, `listed` and `present` helpers, step 1 with its root guard, and the closing
line. They differ only in their step lists, the pins those steps need and the paths each spells
from its root. A spec that changes the skeleton here records the `diff -u` against a consuming
project's `scripts/gate.sh` in its `verification/`, and the project takes the change in its own
gate spec after the sync that brings this standard in; the spec of issue #10 holds the current
diff.

## In a consuming project

This standard is synced in as `agent-os/standards/base/process/verification-gate.md`. The
project's `scripts/gate.sh` runs its own step list on the skeleton above, with the exit contract
and the same first step: the work-tree top refused unless it is the root, then every shell script
under `scripts/` parsed as git lists them, a file ending in `.sh` or starting with a bash shebang,
any other file refused by name. Every later step that reads files from the tree reads the files
git lists, by git's list or by a tool that honours `.gitignore` and is given no path git ignores.
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

---

## base/process/standards-retrospective

# Standards Retrospective

`base/` describes how the patchbay packages are built; a consuming project syncs it in as
`agent-os/standards/base/`, next to the project's own standards. That description is only as
accurate as the last spec that checked it, and **nothing fails when it drifts**. No test goes
red because a standard describes a pattern we stopped using two specs ago, or because a spec
invented a pattern that never got written down.

This is the step that closes that loop. It runs as **the last item of the verification gate**,
on every spec-sized change, whether or not `/agent-os:shape-spec` shaped it. **Record the
answer either way**: "no changes" is a valid outcome, silence is not, because nobody can tell it
apart from "never noticed."

## Why this exists

A pattern invented inside a spec and never written down is a pattern the next spec re-invents
differently. Three specs later there are three ways to do the same thing, all of them
defensible, none of them written anywhere, and the standards confidently describe a fourth.

The cost of asking at the end of a spec is a paragraph. The cost of not asking is the
`discover-standards` pass again.

## The ordering rule

**No pattern is invented that is not in the standards.** If a spec needs one that isn't there,
it is proposed, added, and only then used, in that order. Reaching the retrospective and
discovering a whole new pattern already shipped means the proposal step was skipped; add it now
(or propose it, if it belongs in `base/`), and note in `shape.md` that it landed late.

At shaping time this means: when the plan needs a pattern the standards don't cover, that is a
standards change to decide with the user, not an ad-hoc call to make inside the implementation.

## The questions

Check each against the spec's actual diff.

1. **Did this spec introduce a pattern no standard covers?** A new adapter shape, a new way of
   naming or validating a parameter, a new test seam, a new way two packages talk to each
   other. If it will be copied by the next person who does something similar, it belongs in a
   standard.
2. **Did a standard turn out to be wrong, or stale?** Correct it, citing the code that proves
   the correction. This includes standards you merely *read* during the spec and found didn't
   match reality; you don't have to have changed the code to have learned this.
3. **Did the spec deliberately deviate from a standard?** Either the standard grows the
   exception (with its condition), or the deviation is recorded in `shape.md` as a one-off with
   its reason. A deviation that is neither will read as a violation to the next reviewer.
4. **Did anything a standard points at move, get renamed, or get deleted?** File paths, module
   and class names, config keys, command and script names, and test-file references inside
   standards go stale silently. Fix the pointer.

## Verify against the code, not against the spec

**A standard rewritten during a retrospective is verified against the shipped code and tests,
never against the spec's own decisions or plan.** Read the artifact being described, not the
artifact that described it.

A sibling project has already paid for this lesson. A guard was meant to hold a list of third
parties equal to the list a published document named, and the list was transcribed by reading
that document. The document was missing one entry, so the guard was missing it too, and it
passed. A description copied from the thing it describes agrees with that thing by
construction, **including when the thing is wrong**. The same trap catches a standard rewritten
from the plan that shaped the code instead of from the code that shipped.

**The same holds of a tool's documentation, and of a probe.** A rule that rests on how a tool
behaves is verified by running the tool at its pinned version, on a scratch copy, with the
transcript in the spec's `verification/`, and:

- **the probe's cases are chosen so they can tell the competing claims apart**, not only the
  case that confirms the expected one;
- **the probe's setup is shown to have done what it claims** before its result is read;
- **where a probe and the documentation disagree, the tool's source at the pinned version
  decides**.

A spec that changes such a rule reruns the probe.

`patchbay-standards` paid for all three in one spec. A probe of a build tool tried one version
range outside the running tool, saw the build succeed with a warning, and concluded that the range
did not matter, against the tool's documentation. The range held another version that the tool's
source, at the pinned version, lists as accepted. A range outside every accepted version, and an
exact pin of another version, cases the probe never ran, build with a package fetched from the
index and fail offline: the documentation was right. A second probe, meant to empty a linter's
ignore list, overrode the list in a configuration layer that does not reset the file's and showed
no finding for a rule the file ignores, the same reading a review finding rested on. The tool's
printed settings showed the setup had not done what it claimed; with the selection reset as well,
the rule reports on every file.

## Who owns which standard

Two kinds of standard sit side by side in a consuming project, and the retrospective treats
them differently:

- **Base standards** live under `base/` in `patchbay-standards` and are synced into a consuming
  project as `agent-os/standards/base/`, pinned to a commit. They are owned by
  `patchbay-standards`, and **a base standard is never edited in place during a spec**, not in
  a consuming project and not in `patchbay-standards` itself. The change the spec would make is
  written up in `shape.md` under `### Standards retrospective (proposed, base)`: the file, the
  change, and the shipped code that proves it. That proposal goes to the owner before the spec
  is done and, approved, to `patchbay-standards` as an issue (below), whose own spec lands it as
  a pull request; a consuming project picks it up on its next sync, and until then lives with
  the standard as it is. The proposal, not a local edit, is the record. (Inside
  `patchbay-standards`, changing a base standard is a spec's feature work on its own branch,
  never a side effect of some other spec's retrospective.)
- **Project standards**, everything under `agent-os/standards/` outside `base/`, belong to the
  project and are edited in the retrospective as the questions above direct.

**Every standards edit is approved by a person, always**: a base proposal when the owner sends it
upstream and again as the pull request to `patchbay-standards`, a project standard in the
project's own review of the retrospective's change set. An agent proposes; it does not land a
standard on its own.

## Base proposals go to the owner, then upstream

A retrospective that records one or more entries under
`### Standards retrospective (proposed, base)` is not complete until the owner has seen them. The
agent presents every proposal, each in one or two sentences with the shipped file and the test it
is verified against, and asks which to send upstream: AskUserQuestion, multi-select. A question
holds at most four options, so it carries at most three proposals and ends with a "None of these"
option. A call holds at most four questions, so twelve proposals; more take another call. Then,
before the spec reports done:

- **The approved proposals become one issue on `patchbay-standards`**, created with
  `gh issue create --repo fromtheoutfit/patchbay-standards` from the project's checkout, with no
  AI attribution (`base/process/ownership.md`). It has one section per proposal with its
  verification pointer, a "Depends on" line naming the repository and branch that hold the
  evidence, and it ends with the rules its spec is held to, as
  `fromtheoutfit/patchbay-standards#12` does. The issue's number is written in `shape.md` beside
  each proposal it carries.
- **Its title names it a gate spec when any proposal it carries needs a gate file changed**
  (`base/process/verification-gate.md`), and a standards spec otherwise. A gate spec's issue says
  which proposals touch gate files, and its standards proposals land with it in the same spec.
- **A declined proposal stays in `shape.md`**, marked `declined by owner, <date>`, so the record
  says it was seen.
- **A proposal neither filed nor marked declined is a gate failure for the spec.** The step is
  judgment, like the rest of the retrospective; no machine runs it.

The issue is filed while the evidence it cites is still uncommitted work on the branch, since an
agent never pushes (`base/process/ownership.md`); the owner's push puts it there. When the pull
request opens, whoever writes its body, the owner or an agent asked to, names the issue in the
body, adds the pull request to the issue's "Depends on" line, and checks that every path the issue
cites exists at the pull request's head.

Writing the issue is the agent's work; which proposals it carries is the owner's call. The rule
holds in `patchbay-standards` too: a proposal recorded here becomes an issue here, and the spec
that takes the issue lands it as a pull request.

## Keep the index in step

A standard added, renamed or removed carries its index entry in the same change set: a project
standard in the project's own sections of `agent-os/standards/index.yml`, a base proposal in the
root `index.yml` of `patchbay-standards`, where `scripts/check-index.sh` holds the index to the
files under `base/` and the `gate` check is required on `main`, so a proposal without its entry
does not merge. The index's format, the description line and how a consuming project's index
relates to the root index are `base/process/standards-index.md`'s.

## Never edit this file from inside a retrospective

A gate that rewrites its own terms during the process it governs is precisely what this
prohibition exists for. Strengthening or relaxing the retrospective is a deliberate edit made in
its own spec, with the user, on its own branch, never inside the retrospective of some other spec.

The gate's own files are under the same rule. Which files those are, and that they change only in
a spec whose feature is the gate, are `base/process/verification-gate.md`'s.

## Recording the answer

`shape.md` gets a `## Standards Retrospective` heading. One of two shapes:

```markdown
## Standards Retrospective

Standards retrospective: no changes.

Proposals sent upstream: none.
```

or

```markdown
## Standards Retrospective

- `agent-os/standards/testing/fixtures.md` — added the shared-fixture rule; this spec found
  that two adapters each built the same fake device. Verified against `tests/conftest.py` as
  shipped.
- `agent-os/standards/index.yml` — description updated for the above.
- **Deviation, not a standard change:** the dry-run flag skips the version check. One-off;
  nothing reads the version on that path.

Proposals sent upstream: fromtheoutfit/patchbay-standards#<N>; declined:
`base/process/verification-gate.md` (<its short name>).

### Standards retrospective (proposed, base)

- `base/process/standards-retrospective.md` — [the change, and the shipped file and test that
  prove it]. Proposed, not applied; filed as fromtheoutfit/patchbay-standards#<N>.
- `base/process/verification-gate.md` — [the change, and the shipped file and test that prove
  it]. Proposed, not applied; declined by owner, <date>.
```

The `(proposed, base)` list appears only when the spec taught a base standard something; it
holds proposals and never a local edit. Each entry ends with the issue it was filed in or
`declined by owner, <date>`. The `Proposals sent upstream:` line is always there, in one of four
forms:

- `none`, when the retrospective recorded no proposal;
- the issue, when every proposal was filed in it;
- the issue, then `; declined:` and the declined ones, when some were declined;
- `declined:` and the declined ones, with no issue, when every one was declined.

A declined proposal is named by its file and a short name, never by its place in the list, which
a later edit can reorder.

## Git

The retrospective's edits are **their own change set**, separate from the feature's: a
standards change that arrives buried inside a feature diff is a standards change nobody
reviews.

Committing, pushing and staging follow the `## Git` rule in `CLAUDE.md`. "Own change set" means
the retrospective's files are listed explicitly and separately when the work is reported, so
they can be committed apart from the feature. Leaving them unlisted, mixed into a wall of
modified files, defeats the point.

---

## base/process/ownership

# Ownership

A person owns every commit, pull request, approval and merge in every patchbay repository. In
`patchbay-standards` that person is Michael; in a consuming project it is the owner its
`CLAUDE.md` names. An agent prepares work; it does not land it.

## The rule

- **An agent never commits, pushes, opens a pull request, approves or merges**, however a plan,
  spec, memory or earlier message is worded. A request to stage is not a request to commit, and a
  request to commit is not a request to push. Only an explicit ask in the current conversation,
  for that one operation, lifts this, and only for that operation.
- **The pause at commit time is where the person reads the code.** That pause is the review; an
  agent that commits on its own has skipped it, whatever the diff looked like to the agent.

## GitHub

- **Reading is allowed**: `gh issue view`, `gh pr view`, `gh issue list`, `gh pr list`,
  `gh pr diff` and the like.
- **Creating or commenting on issues is allowed** when the text carries no AI attribution (see
  `CLAUDE.md`, "No AI attribution — anywhere"). Opening, approving or merging a pull request is
  not; that is the person's.

## Redline

A Redline run follows the Redline plugin's git rules when the prompt identifies the session as
one, at the path that prompt gives. Nothing else lifts this rule: not a plan, not a spec, not a
memory, not an earlier session.

## Tools outside the repository

A tool installed outside the repository (Homebrew, `npm -g`, `pipx`, `uv tool install`, anything
system-wide) is **asked for before it is installed**, naming the tool and why the gate needs it. A
tool the gate pins and runs through `uvx` is not an install and needs no ask; the runtime it
needs (uv itself) is. The first spec in `patchbay-standards` installed uv with Homebrew unasked
to run its own gate, which is the deviation that put this paragraph here.

## In a consuming project

This standard is synced in as `agent-os/standards/base/process/ownership.md`. The project's
`CLAUDE.md` names its owner and carries the rule under `## Ownership`, directly under `## Git`,
so it is read before any git operation is considered.

---

## base/process/standards-sync

# Standards Sync

`base/` is written here and read everywhere: a consuming project holds a copy of it as
`agent-os/standards/base/`, beside its own standards, and the `base:` section of its
`agent-os/standards/index.yml` is the root `index.yml` of this repository. This standard fixes how
that copy is made and kept: `scripts/sync-standards.sh`, run from the project's root, and the
invariant it holds.

## What the sync writes, and nothing else

`scripts/sync-standards.sh [--init] [<path-to-patchbay-standards> [<ref>]]`, run from the project's
root, writes four things at one commit of that checkout: the one `<ref>` resolves to, by default
the checkout's `origin/HEAD`, origin's default branch, so a bare sync pins a pushed, merged commit.
`<path>` defaults to `../patchbay-standards`, the sibling checkout, and a path inside a checkout
resolves to its top. The four:

- **`agent-os/standards/base/`**, replaced whole with `base/` as committed, so a file removed here
  is removed there.
- **`agent-os/standards/base/.version`**, the commit as forty hex digits and a newline: the one
  file under a project's `base/` that is not a standard.
- **The `base:` section of `agent-os/standards/index.yml`**, replaced with the `base:` section of
  the root `index.yml` at that commit, byte for byte. Every other line of the project's index is
  left as it was, in place and in order.
- **`scripts/sync-standards.sh`**, the project's copy, replaced with the script at that same commit
  as the last thing the sync writes, so the project carries the script at its pinned commit and
  the next sync runs it. The sync that delivers a change to the script is run by the copy before
  it: a fix to the sync applies from the next sync on.

Nothing else is written, `.claude/commands/` included. A step a base standard asks the gate task
of the project's `shape-spec.md` to carry, as "Base proposals go to the owner, then upstream" in
`base/process/standards-retrospective.md` does, is made by the project, with its `shape.md`
template line, in its own gate spec after the sync that brings the standard in: the gate task
text is a gate file, which changes only in the gate's own spec
(`base/process/verification-gate.md`).

It reads from the commit's tree, never the working tree: each file is read raw with `git cat-file`,
so an uncommitted edit in the checkout cannot be synced, neither a standard nor the script itself,
and neither can the checkout's line-ending settings or attributes. Every precondition is checked
first, and `base/`, `.version` and the new index are built in a temporary directory and swapped in
only then: a refusal leaves the project as it was. What it did is reported on stderr (each file
added, removed or changed, the old and new commit, what the index and the script did) and as one
JSON object on stdout after the last write, for a wrapper to read. Exit 0 is a sync whose result
it compared against the export and found equal; 1 is a result that did not match; 2 is usage or a
precondition, each named: a bad flag or two mode flags, a directory that is not the top of a git
work tree, `<path>` not a patchbay-standards checkout, no `origin/HEAD` to default the ref to,
`<ref>` not a commit, no parseable `base:` section in the project's index without `--init` or in
the commit's `index.yml`, a path under `base/` that is not a regular file or holds a control
character. An explicit `<ref>` whose commit is not on origin's default branch is synced with a
`WARN` line naming it: a commit not pushed or not merged can be rebased or abandoned, leaving the
pin at nothing.

## The invariant

**`agent-os/standards/base/`, less `.version`, and the `base:` section of the project's index are
byte-identical to `base/` and the root `index.yml` of `patchbay-standards` at the commit in
`.version`**, and the project's `scripts/sync-standards.sh` is the script at that commit.
`scripts/sync-standards.sh --check [<path>]` holds it: it exports the pinned commit from the
checkout and names every file missing, extra or changed, whether the `base:` section differs and
whether the script does, exit 1 on any of them, writing nothing. The project's files are the
tracked ones plus the untracked ones git does not ignore, as `scripts/check-index.sh` reads them,
so an ignored `.DS_Store` is never drift. A pinned commit the checkout does not have is a
precondition (exit 2), not drift: fetch it. The check is a step of the project's gate.

No entry in the `base:` section and no file under `base/` is edited by hand. A description the
project disagrees with, a rule it would change, a standard it lacks, is a proposal in the
project's retrospective: the owner sends it upstream as an issue on `patchbay-standards`, that
issue's spec lands it there as a pull request, and the project takes it when it moves its pin. The
route is `base/process/standards-retrospective.md`'s, "Base proposals go to the owner, then
upstream".

## Pinned, not tracking

A project pins one commit and stays on it until it decides otherwise. The default ref is origin's
default branch, so a bare sync moves to what is merged, never to whatever branch the checkout
happens to be on. Syncing forward is deliberate: read this repository's `CHANGELOG.md` from the
pinned commit to the target first, since the `base/` lines of each entry are what the sync will
bring in; run the sync; read what it reports; commit the result in its own change set, titled
`chore: sync base standards to <sha>`. That commit changes nothing but `agent-os/standards/base/`,
`.version`, the `base:` section and `scripts/sync-standards.sh`. Work the new standards ask of the
project's own files is its own spec, after.

## The index

The `base:` section is the line `base:` with nothing after the colon, and every line after it that
is indented, blank or a column-0 comment, up to the last indented line: a trailing blank or comment
line and the next column-0 key are the project's, and a trailing comment in the root `index.yml`
stays here. The sync replaces that span and nothing else, so the project's own sections, its
header comment, its blank lines and the comments it keeps beside its keys come through byte for
byte; test r in `scripts/gate-negative-tests.sh` holds that against an index built by hand, a
section on line 1 included.

- **`--index-only [<path>]`** regenerates the section alone, from the commit in `.version`, and
  touches no file under `base/` and not the script. It is the regeneration that is safe to run on
  a synced index: a hand-edited entry is drift to `--check` and is repaired by it (test s). The
  stock `/agent-os:index-standards` rewrites the whole file and is not run on a synced index, as
  `base/process/standards-index.md` says.
- **`--init`** creates the section for a project syncing for the first time, before the first
  column-0 key other than `root:` that sorts after `base` (above the column-0 comment lines
  directly over that key, which stay with it) or at the end, with one blank line on each side, and
  creates the file when there is none. That is the one place the sync normalizes: the blank lines
  directly above the insertion collapse to the one, and a missing final newline is added. Without
  `--init` a missing section is refused; a `base:` line that is not a parseable section (a second
  `base:` line, or content after the colon) is refused either way.

## In this repository

`scripts/sync-standards.sh` lives here and is run from a consuming project; here
`agent-os/standards/base` is a symlink and the script refuses to run (exit 2, test u). It is a
gate file in every project, so it changes only in its own spec here, carrying its negative tests:
o to v in `scripts/gate-negative-tests.sh`, each on a scratch checkout whose `HEAD` and
`origin/main` hold the working tree's files beside a scratch Agent OS project with its own index
sections and standards, the sync run from the project with the sibling checkout as the default
path and its `origin/main` as the default ref. Gate step 1 parses the script.

## In a consuming project

This standard is synced in as `agent-os/standards/base/process/standards-sync.md`. The project's
checkout of `patchbay-standards` sits beside it as `../patchbay-standards`. The first sync is run
from the checkout's copy, `../patchbay-standards/scripts/sync-standards.sh --init`, which installs
`scripts/sync-standards.sh`; every later sync and check runs the project's copy.
`scripts/sync-standards.sh --check` is a step of the project's `scripts/gate.sh`. The project's
gate workflow checks both repositories out under the workspace, since `actions/checkout` writes
nowhere else: the project into a subdirectory and `patchbay-standards` beside it, at the commit in
`agent-os/standards/base/.version`, each action pinned as the gate standard directs, and runs
`scripts/gate.sh` with the project's directory as the working directory. The pin is read by a
`run` step with an `id`, which writes the file's forty digits to `GITHUB_OUTPUT` as `sha`, and the
second checkout takes `steps.<id>.outputs.sha` as its `ref`, with `repository` and `path` set and
no `fetch-depth`: the default depth fetches that one commit, whatever branch it is on. Checking the
default branch out with full history instead fails the moment a pinned commit is squashed or
deleted from it, and fails only in CI. The hosted run then compares against the real thing at the
pinned commit, and does not go red when `main` moves here.

The project's negative tests (`base/process/verification-gate.md`, "Every step that can fail is
proven to fail") stand the sibling up once per run: one `git clone` of `../patchbay-standards`
into the scratch directory, a local clone, which shares the sibling's objects and so holds the
pinned commit whenever the sibling does, whichever of its refs reaches it. A `--no-local` or
`file://` clone copies only what the sibling's local branches and tags reach, and loses a pin that
only a remote-tracking ref reaches. The clone's branches are the sibling's local ones and its
`origin/HEAD` is the branch the sibling has checked out, neither of which the drift check reads,
since it takes the pin from `.version`. Each case is laid out as `<case>/patchbay` with
`<case>/patchbay-standards` a symlink to that clone, so the script's default path resolves in the
copy as it does in the tree and `../patchbay-standards` itself is never written. The
missing-sibling case removes the symlink; the drift cases edit the copy under `<case>/patchbay`.
The CI replay runs the workflow's `run` steps with the scratch directory as the workspace, each
from its `working-directory`, and prints what the pin step wrote beside the commit in `.version`.

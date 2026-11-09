# Standards for the gate spec after the sync to e31f7db, and Event.at's offset

The following standards apply to this work, as they read when the spec was shaped (before the
retrospective), at `e31f7db`. If this spec changed or proposed a change to any of them, `shape.md`'s
Standards Retrospective says which and why — this file is the snapshot, not the current text.

---

## base/python/toolchain

# Toolchain

Every patchbay Python package does each job with one tool and configures every tool in
`pyproject.toml`. This standard says which tool does which job, what each tool's configuration
says and in what order the gate runs them, and every rule names the file of a consuming project it
is verified against. It was written from patchbay (`fromtheoutfit/patchbay`) at `73a583a`, whose
toolchain spec and its revision after the review of patchbay PR 4 record each choice as a Decision
with its reason; the probes it cites are recorded by the spec of issue #4 in `patchbay-standards`.
"The gate's tool steps" and the `files` rule of "mypy" were read again at `3f910d8`, after
patchbay's revision after the review of its PR 9, by the gate spec of issues #17, #19 and #20,
which reran their probes. "Dependencies" and the suppression rules of "ruff" and "mypy" were read
again at `7471387`, after patchbay's contracts spec and its revision after the review of its PR 11,
by the spec of issue #21, which reran the probes they rest on (its `verification/probes.txt`).

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
  `pyproject.toml`: patchbay's three runtime dependencies came with the code that imports them,
  numpy and pydantic with its contracts spec and pydantic-core with that spec's revision, each a
  Decision in its spec's `shape.md`; typer, which its product stack names for the CLI, is not
  declared, since nothing in it has a CLI yet.
- **A runtime dependency is a range: the version the gate ran as its floor, the next major as its
  ceiling** (`pydantic>=2.14.3,<3`), since an adapter installs the package beside its own
  dependencies, and an exact pin would refuse every other version. The dev group's entries stay
  exact (below). Verified against `[project] dependencies` in `pyproject.toml` and the comment
  over it.
- **A package the code imports directly is declared, even when another dependency brings it in**:
  patchbay's `errors.py` imports pydantic-core's `ErrorDetails`, which pydantic does not re-export,
  so `pydantic-core>=2.50.4,<3` is declared beside the pydantic that requires it. Verified against
  `pyproject.toml` and `src/patchbay/errors.py`; probe f of issue #21's spec.
- **The spec that adds a runtime dependency shows the lock's change in its `verification/`**: the
  lock gained the dependency and the dependencies it brings, and changed no resolution of a tool
  the gate runs, a package a tool shares with it (`typing-extensions`) included. Declaring a
  package the lock already holds changes only the package's own entry, its `dependencies` and its
  `requires-dist`. Verified against the `verification/uv-lock-diff.txt` of patchbay's contracts spec
  (additions only: annotated-types, numpy, pydantic, pydantic-core and typing-inspection) and of
  its revision (patchbay-core's own entry gaining pydantic-core, twice).
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
  warned of is not ignored (patchbay's first run gave neither ISC001 nor PLR2004, and it lists
  neither). When patchbay's contracts revision took the `test_` prefix off its contract tests, D401,
  which waives a function named `test_*`, reported their docstrings, and they were rewritten in
  the imperative, "Check that ...", not ignored. Verified against `[tool.ruff.lint]` in
  `pyproject.toml`, its comment, `src/patchbay/testing/contract_tests.py` and the probes, probe b
  of issue #21's spec among them.
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
  Verified against `select` in `pyproject.toml` and the probes.
- **A suppression sits only where the code cannot change, with its reason beside it**, on its line
  or in the comment directly above, since no tool checks the reason and the reviewer reads it
  there. patchbay's `src/` holds four, each coded: `# noqa: BLE001` on the event bus's catch of
  every subscriber's `Exception`, the behaviour `base/python/events.md` requires;
  `# type: ignore[attr-defined]` on the base-init marker; and `# type: ignore[assignment]` on each
  of the two `__hash__: ClassVar[None] = None` (`base/python/models.md`). A third party's method is
  wrapped, never overridden with its signature copied (`base/python/models.md`), so PLR0913 has no
  case: the three `# noqa: PLR0913` patchbay's contracts spec put on copied signatures went with
  the copies in its revision. Verified against `src/patchbay/events.py` and
  `src/patchbay/models.py`, and the suppressions counted in issue #21's
  `verification/patchbay-evidence.txt`; probe b of that spec.
- **The ignore list grows only in the gate's own spec**, `[tool.ruff]` being a gate file
  (`verification-gate.md`, "The gate's own files change only in their own spec").

## mypy

- **`[tool.mypy]` is `strict = true` over `files = ["src", "tests"]`**, so the tests are typed to
  the package's bar, with `python_version` the floor, `warn_unreachable = true`, since code the
  checker proves unreachable is a bug and strict does not turn it on, and `implicit_reexport =
  false` stated though strict implies it, so a name is exported only by `__all__` or an explicit
  `from x import y as y`. Verified against `pyproject.toml`.
- **`files` is what a bare `uv run --locked mypy` walks**; the gate gives mypy git's list instead
  ("The gate's tool steps"). There is no `exclude_gitignore`: under it mypy's walk skipped a
  tracked file `.gitignore` matches, and in a linked worktree, where `.git` is a file, checked a
  module that only `.git/info/exclude` hides. Verified against `[tool.mypy]` in `pyproject.toml`
  (patchbay at `3f910d8`), its test p and the probes.
- **An untyped third-party package gets its own override**: a `[[tool.mypy.overrides]]` block with
  `module = ["name.*"]`, `ignore_missing_imports = true` and a comment naming the package and why;
  never a global `ignore_missing_imports`. patchbay's runtime dependencies, numpy, pydantic and
  pydantic-core, are typed, it has no override, and the rule is the comment in its `[tool.mypy]`.
  Verified against `pyproject.toml` and the clean mypy run in issue #21's
  `verification/patchbay-evidence.txt`.
- **A `# type: ignore` names its code, `# type: ignore[<code>]`, as a `noqa` does**: under
  `select = ["ALL"]` ruff's PGH003 refuses a blanket one, and strict's `warn_unused_ignores`
  refuses a coded one that suppresses nothing. In `src/` one sits only where the code cannot change
  ("ruff", above); in a test one may hold a refusal mypy must keep making
  (`base/testing/tests.md`). Verified against `src/patchbay/models.py`, the six in `tests/unit/`
  and `pyproject.toml`; probes b and c of issue #21's spec.

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
  step per tool, in this order: format, lint, types, tests.** Format before lint, so a formatting
  failure is reported before a lint finding the formatter would have changed; lint before types,
  since it is faster and its findings cheaper; tests last among the tools, since a type error
  usually explains a failing test. hypothesis runs inside `pytest`, and pre-commit in no step. Each
  tool runs as `uv run --locked <tool>`, and the first tool's step opens with `uv sync --locked`,
  both `verification-gate.md`'s. Verified against `scripts/gate.sh` (patchbay: steps 2 to 5 of
  six).
- **ruff and mypy are given git's list; pytest walks, after a refusal.** The command lines are
  `uv run --locked ruff format --check -- <the .py and .pyi files git lists>`, then
  `uv run --locked ruff check -- <the same>`, then
  `uv run --locked mypy -- <those under src/ and tests/>`, each path checked on the disk: the
  listing rule's first form (`verification-gate.md`, "One script"), so a tracked file `.gitignore`
  matches is read and git alone decides what `.gitignore`, `.git/info/exclude` and the global
  excludes file hide. Walking, ruff (`respect-gitignore`) and mypy (`exclude_gitignore`) skip a
  force-added file `.gitignore` still matches. Then `uv run --locked pytest`, which walks
  `testpaths`: pytest has no form that reads a list without also loading the `conftest.py` of each
  directory it collects from, so its step first refuses, by name, any `.py` file git ignores under
  `tests/` and an ignored `conftest.py` at the root (the refusal form). Verified against
  `scripts/gate.sh` steps 2 to 5 and tests p and q (patchbay at `3f910d8`), and the probes.

## In this repository

`patchbay-standards` has no package: no `pyproject.toml`, no `uv.lock`, no Python under `src/` or
`tests/`. This standard does not apply here, and no file here verifies it. Its rules were read from
patchbay at `73a583a`, the tool steps and mypy's `files` again at `3f910d8`; a spec that changes one
reads it again from a consuming project's shipped files, and reruns the probes a rule rests on.
"Dependencies" and the suppression rules were read again at `7471387`. The one Python tool this
repository's gate runs, pymarkdown through `uvx`, takes the no-manifest form of
`verification-gate.md`. Step 5a of this repository's `shape-spec.md` lists this standard with the
note that it applies to consuming projects; a spec shaped here records it under "Core Architecture"
as not applying and does not copy it into `standards.md`.

## In a consuming project

This standard is synced in as `agent-os/standards/base/python/toolchain.md`. Every rule above is
the project's, verified against the project's own files it names. The project's `shape-spec.md`
lists it in Step 5a, the tier every spec includes without asking, with its full content in that
spec's `standards.md`.

---

## base/python/layout

# Layout

Where everything in a patchbay package lives: its modules, the subpackage its consumers' tests use,
what its `__init__.py` holds, and the one direction its modules import in. Every rule names the file
of a consuming project it is verified against, the test that holds it and the probe a rule about a
tool's behaviour rests on. Written from fromtheoutfit/patchbay at `7471387`, the merge of its PR 11,
whose contracts spec and that spec's revision record each choice as a Decision; the evidence is in
the `verification/` of the spec of issue #21 in `patchbay-standards` and of its revision after the
review of PR 25, patchbay's own probes cited by name and the ones those specs added by letter. The
toolchain spec of issue #4 deferred its `__init__.py` rules here.

Where a test file lives is `base/testing/tests.md`'s; how a name is re-exported so mypy sees it is
`base/python/typing.md`'s.

## The package

- **`src/<package>/` holds one module per concern.** patchbay's core holds four: `contracts.py`,
  the protocol an adapter implements; `models.py`, the values that cross a boundary; `events.py`,
  the events, their bus and its subscriptions; `errors.py`, the exceptions. Verified against
  `src/patchbay/` and the docstring of `src/patchbay/__init__.py`.
- **What a consumer's tests use is a `testing/` subpackage, shipped in the wheel**, a module per
  thing it holds: patchbay's `patchbay.testing` holds the contract tests (`contract_tests.py`),
  the reference implementation they are proven against (`fake.py`) and a subscriber that records
  what it receives (`recording.py`). The root does not re-export it and no module outside it
  imports it, so importing the package loads none of it; a consumer imports it by name. It imports
  no pytest (`base/testing/tests.md`). Verified against `src/patchbay/testing/`, its
  `__init__.py`'s docstring, `src/patchbay/__init__.py`, and the wheel's files and the modules an
  import of the package loads, in the `verification/patchbay-evidence.txt` of the spec of issue #21.
- **No two modules of the package share a basename**, its subpackages' included, so the test
  module each takes its name from (`base/testing/tests.md`, the mirror) is one no other test module
  has, and mypy, which reads `tests/` with no `__init__.py`, never meets two modules of one name.
  The named exception is `__init__.py`, one per package, whose tests take their names from what
  they hold (`base/testing/tests.md`). patchbay's seven, `contracts`, `errors`, `events`, `models`,
  `contract_tests`, `fake` and `recording`, are seven names. Verified against `src/patchbay/` and
  `tests/unit/`; probe n.

## `__init__.py`

- **A package's `__init__.py` holds its re-exports and `__all__`, the root's `__version__` too, and
  nothing else**: no definition and no logic. A module the root imports for itself is bound to a
  private name (`import importlib.metadata as _metadata`), so every public name the root binds is
  an export. `testing/__init__.py` holds re-exports and `__all__` alone. Verified against
  `src/patchbay/__init__.py`, `src/patchbay/testing/__init__.py` and `tests/unit/test_package.py`
  (`test_public_names_are_in_all`).
- **`__version__` is read from the installed distribution's metadata**,
  `importlib.metadata.version("<distribution>")`, so `pyproject.toml` is the one place the version
  is written. Nothing falls back around it: where no distribution is installed, as from a bare
  `src/` on `sys.path`, `importlib.metadata` raises `PackageNotFoundError` and the import fails,
  rather than the package inventing a version. Verified against `src/patchbay/__init__.py`, its
  docstring, and `tests/unit/test_version.py` (`test_version_matches_pyproject`).
- **A test holds the root's surface to `__all__`**: every name the root binds without a leading
  underscore is in `__all__`; every name in `__all__` is bound, and listed once; and each is the
  very object its module defines, not a copy or a second type. Submodules are left out of the
  first: importing `patchbay.errors` binds `errors` on the package, the import system's doing and
  not an export, and `from patchbay import *` does not import them. Verified against
  `tests/unit/test_package.py` (`test_public_names_are_in_all`, `test_every_name_in_all_resolves`,
  `test_the_package_re_exports_the_contract_surface`).

## One direction of import

- **The modules import in one direction, from the errors module up to the root, and are built in
  that order with the gate green after each.** The errors module is the leaf and imports nothing
  from its package (`base/python/errors.md`). In patchbay, `models.py` imports `errors.py`;
  `events.py` imports both; `contracts.py` imports `events.py` and `models.py`; the `testing`
  modules import those; `__init__.py` imports the four. They were built in that order, errors,
  models, events, contracts, the `testing` subpackage with the fake, the contract tests, then
  `__init__.py`, with the gate green after each, at 28, 103, 127, 131, 162, 186 and 188 tests: a
  module cannot pass mypy before what it imports exists. Verified against the imports of each
  module in `src/patchbay/` and the contracts spec's `shape.md` ("Results").
- **A protocol that a module's own API takes lives in that module, beside the API**, so no two
  modules import each other: `Subscriber` is defined in `events.py`, beside the
  `EventBus.subscribe` that takes it, and `contracts.py` re-exports it (`base/python/typing.md`,
  "Re-exports"). `Subscriber` is bounded by `Event`: placed in `contracts.py`, it would have
  `contracts.py` import `Event` from `events.py`, and `events.py` import `Subscriber` from
  `contracts.py` for `subscribe`. Verified against
  `src/patchbay/events.py`, `src/patchbay/contracts.py` and `tests/unit/test_contracts.py`
  (`test_subscriber_is_the_events_module_s_own`).

## In this repository

This repository has no package, so this standard does not apply here; its `shape-spec.md` lists it
in Step 5a for consuming projects.

## In a consuming project

Synced in as `agent-os/standards/base/python/layout.md`, its rules the project's, verified against
the project's own files; Step 5a includes it in every spec, with its full content in that spec's
`standards.md`.

---

## base/python/typing

# Typing

A patchbay package is typed so that mypy, strict over the package and its tests, refuses what the
contracts forbid before a test runs. This standard says how keys, protocols, generics and re-exports
are written for mypy to hold them, and which annotation form pydantic needs. Every rule names the
file of a consuming project it is verified against, the test that holds it and the probe a rule
about a tool's behaviour rests on. Written from fromtheoutfit/patchbay at `7471387`, the merge of
its PR 11, whose contracts spec and that spec's revision record each choice as a Decision; the
evidence is in the `verification/` of the spec of issue #21 in `patchbay-standards` and of its
revision after the review of PR 25, patchbay's own probes cited by name and the ones those specs
added by letter.

mypy's configuration, strict with `implicit_reexport = false`, is `base/python/toolchain.md`'s. How
mypy reads a model's frozenness is `base/python/models.md`'s, and the variance of the subscriber
protocol `base/python/events.md`'s.

## Keys

- **Distinct keys are distinct `NewType`s**, so mypy refuses one where the other is expected, and a
  plain `str` where either is: patchbay's `ParameterId`, the key a host knows a parameter by, and
  `PresetKey`, the key a preset file knows a value by. Each is a `str` at runtime, so a key costs
  nothing to build or to serialize. Verified against `src/patchbay/models.py` and
  `tests/unit/test_models.py` (`test_a_preset_key_is_not_a_parameter_id`, whose coded ignore holds
  mypy's refusal); probe `typing_probe.py` E and F.

## Protocols

- **A protocol's data member is a read-only property**, so an implementation may give it as a
  plain attribute or as a property: `Instrument.name`. Verified against `src/patchbay/contracts.py`
  and `tests/unit/test_contracts.py` (`test_an_object_with_every_member_is_an_instrument`, whose
  `_Silent` gives `name` as a class attribute); probe `runtime.py` 7.
- **A protocol method's parameters are positional-only**, so an implementation names its own:
  every method of `Instrument`, and `Subscriber.__call__`. Verified against
  `src/patchbay/contracts.py`, `src/patchbay/events.py` and `tests/unit/test_contracts.py`; probe
  `typing_probe.py` H.
- **A protocol is checked at runtime with `isinstance`, which asks only whether every member's name
  is there**, under `@runtime_checkable`; a member's signature is mypy's to hold, and its
  behaviour the contract suite's (`base/testing/tests.md`). `issubclass` is refused for a protocol
  with a data member, by mypy statically and by Python at runtime, and is not used. Verified
  against `src/patchbay/contracts.py` and `tests/unit/test_contracts.py`
  (`test_an_object_with_every_member_is_an_instrument`,
  `test_an_object_missing_a_member_is_not_an_instrument`,
  `test_issubclass_is_refused_for_a_protocol_with_a_data_member`); probe `runtime.py` 7.

## Generics

- **Generics use PEP 695's syntax**: a type parameter list on the class or function,
  `class Subscriber[E: Event]`, `def _refusing[**P, R]`, `def of_type[E: Event]`, and the `type`
  statement for an alias, `type ContractTest = Callable[[Instrument, EventBus], None]`. There is
  no `TypeVar`, `ParamSpec`, `Generic` or `TypeAlias` in `src/` or `tests/`. Under
  `select = ["ALL"]` at the 3.12 floor, ruff asks for it: UP046 for a `Generic` class, UP047 for a
  function over a `TypeVar`, UP040 for a `TypeAlias`. Verified against `src/patchbay/events.py`,
  `src/patchbay/models.py`, `src/patchbay/testing/contract_tests.py` and
  `src/patchbay/testing/recording.py`; probe m.

## Re-exports

- **A module re-exports a name by listing it in its `__all__`**, never by importing it alone: under
  `implicit_reexport = false` mypy refuses `from module import name` for a name the module imports
  but does not list, and `--implicit-reexport` lifts the refusal. `patchbay.contracts` imports
  `Subscriber` from `patchbay.events` and lists it in its `__all__`, and every name the package's
  root exports is in the root's `__all__` (`base/python/layout.md`). Verified against
  `src/patchbay/contracts.py`, `src/patchbay/__init__.py`, `pyproject.toml` (`[tool.mypy]`) and
  `tests/unit/test_contracts.py` (`test_subscriber_is_the_events_module_s_own`); probe k.

## Annotations pydantic reads

- **A module whose annotations pydantic reads carries no `from __future__ import annotations`**:
  every module that defines a model. With it, ruff under `select = ["ALL"]` reports an import used
  only in a field's annotation (TC003 for the standard library) and asks for it under
  `if TYPE_CHECKING:`, where pydantic cannot reach it, and the model moved so is not fully defined
  at its first use. Without it, ruff reads the annotation as evaluated at runtime and asks nothing.
  Verified against `src/patchbay/` and `tests/` (no module carries the import); probe l.

## In this repository

This repository has no package, so this standard does not apply here; its `shape-spec.md` lists it
in Step 5a for consuming projects.

## In a consuming project

Synced in as `agent-os/standards/base/python/typing.md`, its rules the project's, verified against
the project's own files; Step 5a includes it in every spec, with its full content in that spec's
`standards.md`.

---

## base/python/models

# Models

Every value that crosses a patchbay package's boundary is a pydantic model on one base. This
standard says what that base guarantees and how each guarantee is kept: frozen, closed, finite and
strict, refusing as the package, read-only inside, and computing alike. Every rule names the file of
a consuming project it is verified against, the test that holds it and the probe a rule about a
tool's behaviour rests on. Written from fromtheoutfit/patchbay at `7471387`, the merge of its PR 11,
whose contracts spec and that spec's revision record each choice as a Decision; the evidence is in
the `verification/` of the spec of issue #21 in `patchbay-standards` and of its revision after the
review of PR 25, patchbay's own probes cited by name and the ones those specs added by letter.

How mypy reads a model's frozenness is here; the type system's other rules, the future import a
model's module never carries among them, are `base/python/typing.md`'s. What the package's errors
are, and what escapes them, is `base/python/errors.md`'s; an event is a model with rules of its own
in `base/python/events.md`.

## One base

- **Every model derives from one public base, the package's own**: patchbay's `PatchbayModel`, in
  `models.py` and in the root's `__all__`, from which every model and every event derives. A model
  that derives from it has every guarantee below, whichever module defines it. Verified against
  `src/patchbay/models.py`, `src/patchbay/events.py`, `src/patchbay/__init__.py` and
  `tests/unit/test_models.py` (`test_a_model_on_patchbay_model_refuses_as_patchbay_at_any_depth`).
- **The base is frozen by the class keyword `frozen=True`, and every subclass writes the keyword
  again on its class line.** mypy, with no pydantic plugin loaded (`[tool.mypy]` names none), reads
  frozen from the keyword and not from `model_config`: given the keyword it refuses an assignment
  to a field and a subclass that leaves the keyword out ("Non-frozen dataclass cannot inherit from
  a frozen dataclass"); given `model_config` alone it accepts an assignment pydantic refuses at
  runtime. The class keyword and `model_config` merge at runtime. There is no exception: every
  event's class line carries it too. Verified against `src/patchbay/models.py` and
  `src/patchbay/events.py` (every class line), `pyproject.toml` (`[tool.mypy]`),
  `tests/unit/test_models.py` (`test_a_frozen_model_is_unchanged_by_a_refused_assignment`) and
  `tests/unit/test_events.py` (`test_an_event_is_frozen`), each holding mypy's refusal with a coded
  ignore; probes `typing_probe.py` C and D, `frozen_kw.py`, `frozen_kw2.py` and `config_form.py`.
- **The base's `model_config` is closed, finite and strict**: `extra="forbid"`,
  `allow_inf_nan=False` and `strict=True`. A field the model does not declare, NaN and an infinity
  are refused, and no value is converted from another type: `"0.5"` is not 0.5, `1` is not `True`,
  a list is not a tuple and a `str` is not an enum. Strict admits three things, by pydantic's
  design: an int for a float; a dict for a nested model, every field inside it validated by the
  nested model's own config, so as strictly where the nested model is on the base too, and laxly
  where it is not, strict outside or not; and `model_validate_strings`, whose purpose is parsing
  strings. Every model a model holds is on the base, so strict holds at every depth. A model's own
  `model_config` adds to the base's and relaxes none of it: patchbay's `Patch` adds base64 for
  bytes, `RenderResult` arbitrary types for its array. Verified against `src/patchbay/models.py`
  and `tests/unit/test_models.py` (`test_every_entry_point_refuses_with_patchbay_validation_error`,
  `test_strict_refuses_a_conversion`, `test_strict_admits_an_int_for_a_float_and_json_forms`);
  probes `runtime.py` 5, `strict_nested.py` (1, strict inside; 2, a lax model inside a strict one
  admitting `'0.5'`) and `config_form.py`.

## Refusing as the package

- **A model's own entry points refuse with the package's validation error, chained from
  pydantic's.** The constructor, `model_validate`, `model_validate_json` (bad JSON included),
  `model_validate_strings`, the JSON-data entry point below, assignment and deletion each raise
  `PatchbayValidationError` from pydantic's `ValidationError`, which is a `ValueError` and so never
  escapes as one (`base/python/errors.md`). Verified against `src/patchbay/models.py`
  (`_refusals`) and `tests/unit/test_models.py`
  (`test_every_entry_point_refuses_with_patchbay_validation_error`); probe `runtime.py` 6.
- **Validation pydantic runs on behalf of something else is that thing's, and raises pydantic's
  error**: a `TypeAdapter` over a model, or a plain `BaseModel` that holds one as a field. A model
  that derives from the base is not something else: it refuses as the package at any depth.
  `model_copy(update=...)` validates nothing and is not a way in. No hook covers every path:
  pydantic-core collects a `ValueError` raised inside a validator, with its path, beside the outer
  model's own refusals, and lets any other exception through unwrapped, which ends the outer
  validation at the first nested refusal and loses the outer path and the outer refusals. So the
  package's error is raised around the entry points, never from inside a validator. Verified
  against `src/patchbay/models.py` (its docstring) and `tests/unit/test_models.py`
  (`test_validation_run_for_something_else_raises_pydantic_s_error`,
  `test_a_model_on_patchbay_model_refuses_as_patchbay_at_any_depth`); probe a (a1, a2, a5).
- **A validator raises `ValueError`**, which pydantic collects with the field's path; a validator
  that calls code raising the package's error catches it and raises `ValueError` from it
  (patchbay's `Parameter._default_is_a_value`). Verified against `src/patchbay/models.py`,
  `src/patchbay/events.py` and `tests/unit/test_models.py`
  (`test_a_parameter_that_does_not_hold_together_is_refused`); probe a (a1).
- **pydantic's validating classmethods are wrapped, never restated.** In the base, under
  `if not TYPE_CHECKING:`, each of `model_validate`, `model_validate_json` and
  `model_validate_strings` is `classmethod(_refusing(BaseModel.<name>.__func__))`, where
  `_refusing[**P, R]` is a `functools.wraps` decorator that raises a refusal as the package's
  error. mypy, which skips the block, checks every call against pydantic's own `Self`-typed
  signatures, so a misspelled keyword is a type error; at runtime the wrapper forwards whatever it
  is given, so a keyword a later pydantic adds reaches pydantic, and `inspect.signature` of each
  equals pydantic's. Nothing is copied, so ruff's PLR0913 has no case (`base/python/toolchain.md`,
  "ruff"). Verified against `src/patchbay/models.py` and `tests/unit/test_models.py`
  (`test_the_validating_classmethods_keep_pydantic_s_signatures`,
  `test_a_keyword_reaches_pydantic_through_the_wrapper`); probes `footing.py` A and
  `footing_typing.py`.
- **The base's own `__init__` carries pydantic's base-init marker**,
  `__pydantic_base_init__ = True`, with its coded `# type: ignore[attr-defined]` and the reason in
  the comment above it. The override validates exactly what `BaseModel.__init__` does. Without the
  marker, pydantic builds a nested model by calling that `__init__` with the parsed input in Python
  mode: strict then refuses a valid JSON enum string one level down, and a nested refusal escapes
  the outer validation without the outer path or the outer refusals. Verified against
  `src/patchbay/models.py` and `tests/unit/test_models.py`
  (`test_a_patch_round_trips_through_json_byte_for_byte`); probes `models_init.py` and a (a3, a4).

## Python input and JSON data

- **Python input is Python's types, strictly; data in JSON's form goes through one entry point on
  the base**, patchbay's `from_json_data(data)`, for what `json.loads`, a YAML or a TOML parser
  gives. It validates `json.dumps(data)` with `model_validate_json`, so the data meets pydantic's
  JSON rules exactly: an enum by its value, bytes as base64 where the model reads them so, a time
  as an ISO string, an array for a tuple. Strict still refuses `"0.5"` for a float, `1` for `True`
  and NaN. A value JSON cannot hold, a set, a `datetime` or a circular reference, is refused as the
  package's error with one detail at the root, chained from `json`'s `TypeError` or `ValueError`.
  The name keeps out of pydantic's `model_` namespace, where a later pydantic method could land.
  Verified against `src/patchbay/models.py`, `tests/unit/test_models.py`
  (`test_from_json_data_takes_json_s_own_forms`, `test_from_json_data_is_still_strict`,
  `test_from_json_data_refuses_data_json_cannot_hold`, `test_a_patch_comes_back_from_its_json_data`)
  and `tests/unit/test_events.py` (`test_an_event_comes_back_from_its_json_data`); probe
  `footing.py` E.

## Frozen inside

- **A mapping field is sorted by key and held as a `MappingProxyType`**, by an after-validator,
  with a wrap serializer that hands pydantic a plain dict: pydantic validates a `Mapping` to a
  `dict` that a frozen model still lets anyone change, and cannot serialize a proxy without the
  serializer. The same model then writes the same JSON whatever order it was built in. Verified
  against `src/patchbay/models.py` (`Patch`) and `tests/unit/test_models.py`
  (`test_a_patch_s_mappings_are_read_only`, `test_a_patch_has_one_json_whatever_order_it_was_built_in`);
  probe `runtime.py` 1 and 2.
- **An array field is copied, marked unwriteable, and checked for its dtype, its shape and finite
  values**, an arbitrary-type field being only an `isinstance` check; and the model defines `__eq__`
  with `np.array_equal`, since `==` on two arrays has no truth value. Verified against
  `src/patchbay/models.py` (`RenderResult`) and `tests/unit/test_models.py`
  (`test_a_render_result_holds_a_read_only_copy`, `test_a_render_result_refuses_audio_of_another_shape`,
  `test_a_render_result_refuses_audio_that_is_not_finite`, `test_render_results_compare_by_their_arrays`);
  probe `runtime.py` 4.
- **A model that cannot be hashed says so the way Python does**, `__hash__: ClassVar[None] = None`,
  with its coded `# type: ignore[assignment]` and the reason in the comment above it: pydantic's
  frozen hash would raise on a mapping or an array from inside. Verified against
  `src/patchbay/models.py` (`Patch`, `RenderResult`) and `tests/unit/test_models.py`
  (`test_a_patch_is_not_hashable`, `test_a_render_result_is_not_hashable`); probe `runtime.py` 1
  and 4.
- **Bytes go into JSON as base64** (`ser_json_bytes` and `val_json_bytes`), since pydantic's default,
  UTF-8, fails on bytes that are not text. Verified against `src/patchbay/models.py` (`Patch`) and
  `tests/unit/test_models.py` (`test_a_patch_round_trips_through_json_byte_for_byte`); probe
  `runtime.py` 3.
- **An id is non-empty wherever it appears**, a mapping's key included, written
  `Annotated[ParameterId, Field(min_length=1)]` where a field's `Field` cannot reach it. Verified
  against `src/patchbay/models.py`, `src/patchbay/events.py`, `tests/unit/test_models.py`
  (`test_a_patch_s_parameter_ids_are_not_empty`) and `tests/unit/test_events.py`
  (`test_a_changed_parameter_is_named`); probe `footing.py` D.

## Computing alike

- **A quantity every implementation must compute alike is one method on the model, in exact
  arithmetic**, so it is an int for every valid input, never an overflow or an infinity: patchbay's
  `RenderRequest.samples(pattern)`, the length of every render, and `sample_at(pattern, beat)`,
  where a note falls, each in `fractions.Fraction` and rounded half to even. An implementation
  calls the method and never restates the formula. A float derived from one divides an int by an
  int (`RenderResult.audio_seconds`), which Python rounds correctly and which overflows only where
  the quotient passes the largest float, as an array's length over a positive rate never does.
  Verified against
  `src/patchbay/models.py`, `src/patchbay/testing/fake.py` and
  `src/patchbay/testing/contract_tests.py`, which call them, and `tests/unit/test_models.py`
  (`test_samples_is_an_int_however_long_the_render`, `test_samples_rounds_half_to_even`,
  `test_sample_at_places_a_beat_by_the_rule_that_fixes_the_length`,
  `test_sample_at_is_an_int_at_any_tempo`, `test_audio_seconds_holds_at_any_rate`); probes
  `footing.py` B and s.

## In this repository

This repository has no package, so this standard does not apply here; its `shape-spec.md` lists it
in Step 5a for consuming projects.

## In a consuming project

Synced in as `agent-os/standards/base/python/models.md`, its rules the project's, verified against
the project's own files; Step 5a includes it in every spec, with its full content in that spec's
`standards.md`.

---

## base/python/errors

# Errors

A patchbay package reports every failure as an exception of its own, carrying the fields that say
what failed. This standard says how the package's exceptions are arranged, what each carries and
what may leave a public method. Every rule names the file of a consuming project it is verified
against, the test that holds it and the probe a rule about a tool's behaviour rests on. Written from
fromtheoutfit/patchbay at `7471387`, the merge of its PR 11, whose contracts spec and that spec's
revision record each choice as a Decision; the evidence is in the `verification/` of the spec of
issue #21 in `patchbay-standards` and of its revision after the review of PR 25, patchbay's own
probes cited by name and the ones those specs added by letter.

Where a model's refusal comes from is `base/python/models.md`'s, and what the event bus raises and
lets through is `base/python/events.md`'s; this standard names both and restates neither.

## One root

- **A package's exceptions have one root, and every exception the package raises derives from
  it**: patchbay's `PatchbayError`, so a caller catches every failure the package reports with one
  `except`. The root derives from `Exception`, and no exception's MRO holds a built-in narrower
  than `Exception`, so a caller's `except ValueError` or `except KeyError` never catches the
  package's error by accident: `PatchbayValidationError` is not a `ValueError`, though the pydantic
  error it stands in for is. The one exception is the contract suite's violation,
  `ContractViolationError`, an `AssertionError`: it is a failed assertion to pytest, raised by a
  test and never by the package's API (`base/testing/tests.md`). Verified against
  `src/patchbay/errors.py`, `src/patchbay/testing/contract_tests.py` and
  `tests/unit/test_errors.py` (`test_error_is_a_patchbay_error_and_no_builtin_subtype`).
- **Every exception's name ends in `Error`**, the root's included, as ruff's N818 asks under
  `select = ["ALL"]`. Verified against `src/patchbay/errors.py`,
  `src/patchbay/testing/contract_tests.py` and `pyproject.toml` (`[tool.ruff.lint]`, whose ignore
  list does not hold N818); probe j.

## Fields and messages

- **An error takes its fields as constructor arguments, keeps each as an attribute of the same
  name, and passes them to `Exception.__init__` in the same order**, so `args` holds them, and
  `copy` and pickling, which rebuild an exception by calling its class with its `args`, rebuild it.
  An error that passed a message instead cannot be copied or unpickled. Its message is `__str__`,
  built from the fields. The root takes no fields. Verified against `src/patchbay/errors.py` and
  `tests/unit/test_errors.py` (`test_fields_are_attributes`, `test_error_is_rebuilt_from_its_args`,
  `test_message_is_built_from_the_fields`); probe f (f3).
- **A field is typed as the plain value it is**: an id or a unit as `str`, a bound or a value as
  `float`. The errors module then imports nothing from its own package, and every other module can
  import it: it is the leaf the package's modules are built up from (`base/python/layout.md`). A
  third party's type a field carries is imported from the package that defines it, which the
  manifest declares: `PatchbayValidationError.details` holds pydantic-core's `ErrorDetails`, which
  pydantic does not re-export (`base/python/toolchain.md`, "Dependencies"). Verified against
  `src/patchbay/errors.py`, whose one import is `pydantic_core`, and `pyproject.toml`
  (`[project] dependencies`); probe f (f2).
- **No field takes the name of a third party's method on the error it stands in for.** A
  validation error's refusals are `.details`: pydantic's `ValidationError.errors` is a method, and
  a tuple of that name fails code ported from it with "'tuple' object is not callable", where a
  missing attribute fails it by name. A failure that carries exceptions holds them as
  `.exceptions`, the name `ExceptionGroup` gives them. Verified against `src/patchbay/errors.py`
  and `tests/unit/test_errors.py` (`test_no_field_is_named_like_pydantic_s_errors_method`); probe
  f (f2).

## What escapes

- **No built-in exception leaves a public method.** A lookup that fails is the package's not-found
  error, `ParameterNotFoundError(parameter_id, instrument)`, never `KeyError`; a value a parameter
  does not take is `ValueOutOfRangeError` or `UnitMismatchError`, never `ValueError`; a refused
  model input is the package's validation error (`base/python/models.md`). Two named exceptions,
  each passing an exception the package did not raise: validation pydantic runs on behalf of
  something else raises pydantic's error (`base/python/models.md`), and a `BaseException` that is
  not an `Exception` passes through the bus where a subscriber raised it
  (`base/python/events.md`). Verified against `src/patchbay/errors.py`,
  `src/patchbay/testing/fake.py` (`_parameter`), `src/patchbay/testing/contract_tests.py`
  (`an_unknown_id_raises_parameter_not_found`, `a_value_out_of_range_raises_value_out_of_range`)
  and `tests/unit/testing/test_fake.py`
  (`test_get_of_an_unknown_id_names_the_id_and_the_instrument`).
- **An error raised in place of another is chained from it**, `raise ... from error`, so the cause
  stays on `__cause__`: the validation error from pydantic's, the JSON-data refusal from `json`'s,
  the bus's failure from the first subscriber's exception, a refused patch from the check that
  refused it. The one exception is `from None` where the replaced error is the lookup's own
  `KeyError`, which says nothing the not-found error does not. An error with no cause, a patch for
  another instrument, is raised plainly. Verified against `src/patchbay/models.py`,
  `src/patchbay/events.py`, `src/patchbay/testing/fake.py` (`_parameter`, `_check_whole`),
  `tests/unit/test_models.py` (`test_every_entry_point_refuses_with_patchbay_validation_error`,
  `test_from_json_data_refuses_data_json_cannot_hold`) and `tests/unit/test_events.py`
  (`test_a_failing_subscriber_hides_the_event_from_no_other`).

## In this repository

This repository has no package, so this standard does not apply here; its `shape-spec.md` lists it
in Step 5a for consuming projects.

## In a consuming project

Synced in as `agent-os/standards/base/python/errors.md`, its rules the project's, verified against
the project's own files; Step 5a includes it in every spec, with its full content in that spec's
`standards.md`.

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
work tree (asked of git, comparing no paths: `git rev-parse --is-inside-work-tree` printing `true`,
which it does not in `.git/` or a bare repository, and `--show-cdup` empty, so a project's root
typed in another case is its root), `<path>` not a patchbay-standards checkout, no `origin/HEAD` to
default the ref to, `<ref>` not a commit, no parseable `base:` section in the project's index
without `--init` or in the commit's `index.yml`, a path under `base/` that is not a regular file or
holds a control character, a listing of the project's files git cannot make. Each is found before
anything is written. An explicit `<ref>` whose commit is not on origin's default branch is
synced with a `WARN` line naming it: a commit not pushed or not merged can be rebased or abandoned,
leaving the pin at nothing.

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
`.version`, the `base:` section, `scripts/sync-standards.sh` and the project's `CHANGELOG.md`,
where it adds one entry under `[Unreleased]` naming the old commit and the new, as the sync's
report gives them (`sync base standards: <old> -> <new>`; a first sync names the new alone), so a
sync forward is recorded by the change that makes it. The script writes no `CHANGELOG.md`: the
person who syncs writes the entry, in the same commit. Work the new standards ask of the project's
own files is its own spec, after.

A base change that leaves a consuming project's gate files out of step with a rule says so where
the project's sync will read it. Its entry in this repository's `CHANGELOG.md` names the project
and the work, and an issue in that project records the work for the gate spec that follows its
sync. The sync brings the rule; the project's gate spec brings its gate files in step.

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
path and its `origin/main` as the default ref; u holds its refusals, a folder below the project's
root and its `.git/` among them, and its root typed in upper case passing; t and u hold a project
index git cannot read, refused by name. Gate step 1 parses the script.

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

## base/python/events

# Events

What a patchbay package has done, it says after doing it, as an event published on a bus. This
standard says what an event is, how the bus delivers it, and what a subscriber and a subscription
are. Every rule names the file of a consuming project it is verified against, the test that holds it
and the probe a rule about a tool's behaviour rests on. Written from fromtheoutfit/patchbay at
`7471387`, the merge of its PR 11, whose contracts spec and that spec's revision record each choice
as a Decision; the evidence is in the `verification/` of the spec of issue #21 in
`patchbay-standards` and of its revision after the review of PR 25, patchbay's own probes cited by
name and the ones those specs added by letter.

An event is a model, and every rule of `base/python/models.md` holds of it; where `Subscriber`
lives, beside the bus, is `base/python/layout.md`'s; the errors the bus raises are
`base/python/errors.md`'s.

## The event

- **An event is a frozen model on the package's base**, `Event`, every event type its subclass with
  `frozen=True` on its class line. Its payload is typed fields on its own class, never a dict.
  Beside the payload every event carries `name`, `version` (the payload's shape, `1` or more, so a
  subscriber can tell a later shape), `at`, `source` (what built it) and `correlation_id` (the
  call it belongs to), the last two non-empty. Verified against `src/patchbay/events.py` and
  `tests/unit/test_events.py` (`test_each_event_names_itself_in_past_tense_dotted_form`,
  `test_an_event_says_where_it_came_from`, `test_an_event_is_frozen`,
  `test_an_event_round_trips_through_json`).
- **An event's name is dotted lowercase words, in the past tense, fixed per class by a `Literal`
  default**: `parameter.changed`, `patch.loaded`, `render.completed`. Two words or more, each a
  lowercase letter then letters, digits or underscores; a class cannot be built under another
  name. The shape is validated; the tense is the reviewer's to hold, no check reading it. Verified
  against `src/patchbay/events.py` (`_NAME`, each subclass's `name`) and `tests/unit/test_events.py`
  (`test_an_event_s_name_is_fixed_by_its_class`, `test_an_event_s_name_is_dotted_lowercase_words`,
  `test_a_name_with_digits_and_underscores_is_an_event_s_name`).
- **An event is stamped with the UTC time it was built**, `at` defaulting to `datetime.now(UTC)`.
  A time given for `at` is judged by its zone's answer for no particular instant,
  `tzinfo.utcoffset(None) == timedelta(0)`, not by its offset at the time given, and is held as
  `datetime.UTC` at the same instant, so a time read back from JSON, whose zone pydantic parses as
  its own, is held the same way. UTC, `timezone.utc`, `ZoneInfo("UTC")` and pydantic's parsed `Z`
  answer zero and are accepted. A naive time is refused, and so are a fixed zone at another offset
  and a zone whose offset changes, such as Europe/London, which answers `None`, in every season:
  whether an event is valid never depends on when it was built. The check reads the zone's answer
  and not every instant's offset, so a `tzinfo` that answers zero for no instant and another offset
  at a real one is accepted, and converted at that instant's offset. Verified against
  `src/patchbay/events.py` (`_in_utc`) and `tests/unit/test_events.py`
  (`test_an_event_is_stamped_in_utc_when_built`, `test_an_event_s_time_is_refused_unless_utc`, its
  London cases in January and July, `test_a_time_in_utc_is_held_as_datetime_utc`,
  `test_an_event_round_trips_through_json`); probes `footing.py` C and r.

## The bus

- **The bus is synchronous and in-process**: `publish` calls every subscriber whose type the event
  is, in the order they subscribed, and returns once all have run. It never alters an event: each
  subscriber receives the very object published. Verified against `src/patchbay/events.py`
  (`EventBus`) and `tests/unit/test_events.py`
  (`test_publish_delivers_to_every_subscriber_once_in_subscription_order`,
  `test_subscribe_by_type_receives_only_that_type`, `test_subscribe_to_the_base_event_is_every_event`,
  `test_publish_with_no_subscribers_does_nothing`).
- **A publish delivers over a snapshot of the subscriptions it began with**, so a subscription
  made or cancelled during a publish takes effect from the next event. Verified against
  `src/patchbay/events.py` and `tests/unit/test_events.py`
  (`test_a_subscriber_added_during_a_publish_starts_with_the_next_event`,
  `test_a_cancel_during_a_publish_takes_effect_from_the_next_event`).
- **A subscriber that raises hides the event from no other.** The bus runs every subscriber, then
  raises one error carrying each failure in the order raised, chained from the first: patchbay's
  `SubscriberFailedError(event_name, exceptions)`. It catches `Exception` only, under the one
  coded `# noqa: BLE001` with its reason beside it (`base/python/toolchain.md`, "ruff"): a
  `BaseException` that is not an `Exception`, `KeyboardInterrupt` and its kind, stops delivery where
  it is raised. Verified against `src/patchbay/events.py` (`_deliver`) and
  `tests/unit/test_events.py` (`test_a_failing_subscriber_hides_the_event_from_no_other`,
  `test_a_base_exception_stops_delivery_where_it_is_raised`); probe b.

## Subscribing

- **`subscribe` refuses a bad subscription where it is made**: an event type that is neither
  `None`, for every event, nor a subclass of `Event`, and a subscriber that cannot be called, each
  raise the package's error, patchbay's `SubscriptionRejectedError`, with nothing subscribed. A
  bad subscription then fails once, where it is made, and not at every publish after it. The
  types already say so to mypy; the check says so to a caller mypy never saw. Verified against
  `src/patchbay/events.py` and `tests/unit/test_events.py`
  (`test_a_bad_subscription_is_refused_where_it_is_made`).
- **`subscribe` returns a `Subscription`**, which says what it delivers and to whom:
  - `cancel()` ends it from the next event, and a second `cancel()` does nothing;
  - it is a context manager that cancels on leaving the block, whether the block returned or
    raised, and what the block raised goes on;
  - the bus drops a cancelled subscription, so it holds the subscriber no longer and the
    subscriber can be collected;
  - each `subscribe` is a subscription of its own, so one subscriber subscribed twice receives
    twice and is cancelled one subscription at a time.

  Verified against `src/patchbay/events.py` (`Subscription`, `EventBus._remove`) and
  `tests/unit/test_events.py` (`test_a_subscription_says_what_it_delivers_and_to_whom`,
  `test_cancel_ends_delivery_and_a_second_cancel_does_nothing`,
  `test_a_subscription_is_a_context_manager_that_cancels_on_exit`,
  `test_a_cancelled_subscriber_is_no_longer_held_by_the_bus`,
  `test_each_subscribe_is_its_own_subscription`).
- **The subscriber protocol is generic and contravariant**: `Subscriber[E: Event]`, a
  `runtime_checkable` protocol whose one member is `__call__(self, event: E, /) -> None`. A
  subscriber for one type takes that type, and a handler of the base event serves for any type:
  mypy accepts `subscribe(ParameterChanged, handler)` for a handler taking a `ParameterChanged` and
  refuses that handler where every event is wanted. The event is positional-only, so a subscriber
  names its parameter as it likes, and any function will do. `subscribe` has two overloads,
  `(type[E], Subscriber[E])` and `(None, Subscriber[Event])`. Verified against
  `src/patchbay/events.py` and `tests/unit/test_events.py` (`test_a_function_is_a_subscriber`);
  probe `typing_probe.py` G, H and I.

## In this repository

This repository has no package, so this standard does not apply here; Step 5b of its `shape-spec.md`
leaves it out.

## In a consuming project

Synced in as `agent-os/standards/base/python/events.md`, its rules the project's, verified against
the project's own files; Step 5b surfaces it from the index for a spec that adds an event or touches
the bus.

---

## base/testing/tests

# Tests

How a test in a patchbay package is written and where it lives, and how the contract suite, the
tests every implementation of a package's protocol runs, is written and proven. Every rule names the
file of a consuming project it is verified against, the test that holds it and the probe a rule
about a tool's behaviour rests on. Written from fromtheoutfit/patchbay at `7471387`, the merge of
its PR 11, whose contracts spec and that spec's revision record each choice as a Decision; the
evidence is in the `verification/` of the spec of issue #21 in `patchbay-standards` and of its
revision after the review of PR 25, patchbay's own probes cited by name and the ones those specs
added by letter. The toolchain spec of issue #4 deferred its test-file rules here.

pytest's and hypothesis's configuration, the `"tests/**"` per-file ignores and mypy's `files` are
`base/python/toolchain.md`'s. Where the `testing` subpackage lives is `base/python/layout.md`'s.

## Test files

- **The tests mirror the source, one test module per module**: `src/<package>/<module>.py` is
  tested by `tests/unit/test_<module>.py`, and `src/<package>/testing/<module>.py` by
  `tests/unit/testing/test_<module>.py`. Two named exceptions: the root `__init__.py` is tested by
  `test_package.py`, its surface and its distribution's metadata, and `test_version.py`, its
  version; `testing/__init__.py`, which holds re-exports alone, has no test module. No two modules
  of the package share a basename (`base/python/layout.md`), so the mirror never gives two test
  modules one name. Verified against `src/patchbay/` and `tests/unit/`.
- **Every module under `tests/` has a basename no other module there has, `conftest.py` included,
  and `tests/` has no `__init__.py`**: `tests/` is a tree pytest collects from `testpaths`, not a
  package, and mypy, given `src` and `tests`, refuses two modules of one name as a duplicate, two
  test files or two `conftest.py` alike, though pytest loads both of the latter. Verified against
  `tests/unit/`, the comment on INP001 in `pyproject.toml`'s per-file ignores, and the gate's mypy
  step; probes n and q.
- **`tests/` holds one `conftest.py` at most, in the directory that holds every test taking its
  fixtures**, the fixtures function-scoped so every test starts fresh: a second is a duplicate
  module to mypy (above). patchbay's is `tests/unit/testing/conftest.py`, whose `bus` and
  `instrument` the contract tests and the fake's tests both take, and there is no other. Verified
  against `tests/unit/testing/conftest.py`, `tests/unit/testing/test_contract_tests.py` and
  `tests/unit/testing/test_fake.py`; probe q.

## Inside a test

- **A test reads the repository's files from pytest's root**, `pytestconfig.rootpath`, the
  directory pytest took its own configuration from, never a path counted up from the test file.
  Verified against `tests/unit/test_version.py` (`test_version_matches_pyproject`).
- **A property test's strategy generates only inputs the property holds of, and a known
  counterexample is pinned with `@example`**, so it is tried on every run, not only when the search
  finds it. Verified against `tests/unit/test_version.py`
  (`test_release_pattern_rejects_a_non_numeric_segment`, its strategy filtered and its `@example`
  the Arabic-Indic ten) and `tests/unit/test_models.py` (`_FINITE`).
- **A pattern a value is held to spells its digits `[0-9]`, never `\d`**, which matches any Unicode
  decimal digit, ARABIC-INDIC DIGIT ONE among them; and a character ruff finds confusable is
  written as its escape, as RUF001 (in a string) and RUF003 (in a comment) ask, the rules kept:
  each reports the character itself and neither its escape. Verified against
  `tests/unit/test_version.py` (`_RELEASE` and its comment); probes f (o1), o (the character) and
  p (its escape).
- **A test that holds a refusal mypy must keep making carries a coded `# type: ignore[<code>]` on
  the refused line**, and strict's `warn_unused_ignores` fails the gate the day mypy stops refusing
  and the ignore suppresses nothing (`base/python/toolchain.md`, "mypy"). patchbay's tests hold six:
  a `PresetKey` where a `ParameterId` is expected (`arg-type`); `issubclass` of `Instrument`
  (`misc`); an assignment to a frozen model (`misc`); an assignment to a frozen event (`misc`); an
  item assigned into a `Patch`'s mapping (`index`); and a subscription of types mypy refuses
  (`call-overload`). Verified
  against `tests/unit/test_models.py` (`test_a_preset_key_is_not_a_parameter_id`,
  `test_a_frozen_model_is_unchanged_by_a_refused_assignment`, `test_a_patch_s_mappings_are_read_only`),
  `tests/unit/test_contracts.py` (`test_issubclass_is_refused_for_a_protocol_with_a_data_member`)
  and `tests/unit/test_events.py` (`test_an_event_is_frozen`, `_subscribe_unchecked`); probe c.

## The contract suite

- **The contract tests ship in the package that defines the protocol, in its `testing`
  subpackage, as plain functions `<property>(instrument, bus) -> None`**, taking an instrument that
  publishes on `bus`, both fresh for the test, and listed once in one tuple a consumer
  parametrizes over: patchbay's `CONTRACT_TESTS`, typed `tuple[ContractTest, ...]`, run as
  `@pytest.mark.parametrize("contract_test", CONTRACT_TESTS, ids=lambda test: test.__name__)`.
  Verified against `src/patchbay/testing/contract_tests.py` and
  `tests/unit/testing/test_contract_tests.py` (`test_contract`).
- **No contract test's name starts with `test_`**, so pytest never collects one a consumer imports
  by name: it runs from the tuple, once. Each docstring is imperative, "Check that ...", as ruff's
  D401 asks once the prefix that waived it is gone. Verified against
  `src/patchbay/testing/contract_tests.py` and `tests/unit/testing/test_contract_tests.py`
  (`test_the_contract_tests_are_never_collected_by_pytest`); probes e and b.
- **A contract test fails with an `AssertionError` subclass carrying fields**, patchbay's
  `ContractViolationError(test, expected, actual)`, its message built from them
  (`base/python/errors.md`): a failed assertion to pytest. It never uses `assert`, which
  `python -O` strips, and never imports pytest, a development dependency an installed package
  cannot count on. An exception the test does not expect propagates as itself. Verified against
  `src/patchbay/testing/contract_tests.py`, `src/patchbay/testing/__init__.py` and
  `tests/unit/testing/test_contract_tests.py`
  (`test_a_contract_violation_is_an_assertion_error_with_fields`); probe d.
- **Each contract test works out what it expects from the instrument's parameters and the contract
  alone**, never from an implementation's code. Values are set at a parameter's bounds, so an
  instrument that stores what it is given gets back exactly that; a value past a bound is the next
  float beyond it, `math.nextafter`, since at 2**53 and at the largest float `bound + 1.0` is the
  bound itself, and a bound with no finite float beyond it gets no candidate there. A ratio's
  candidates stay in `[0, 1]`, and a choice or a boolean adds `minimum + 0.5`. Verified against
  `src/patchbay/testing/contract_tests.py` (`_other_value`, `_out_of_range`) and
  `tests/unit/testing/test_contract_tests.py`
  (`test_a_correct_instrument_with_the_widest_bounds_passes`); probes f (f1) and `mutations.py`.
- **Each contract test is proven by the reference implementation broken its way**, and the proof
  asserts the reason the test gives, not only that it fails: the violation names the test, and its
  `expected` starts with the reason. A test holds the table of broken implementations to the
  suite, each contract test once and nothing else. Verified against
  `tests/unit/testing/test_contract_tests.py` (`test_every_contract_test_has_a_broken_fake`,
  `test_each_contract_test_catches_its_broken_fake`).
- **A correct implementation at the edges passes every contract test**: patchbay's reference fake,
  widened through its `parameters()` with one parameter up to 2**53 and one over every finite
  float. Put back to the arithmetic it replaced, `bound + 1.0`, two contract tests fail it with "no
  exception". Verified against `tests/unit/testing/test_contract_tests.py` (`_WideRange`,
  `test_a_correct_instrument_with_the_widest_bounds_passes`); probe `mutations.py`.
- **The suite holds the protocol's promises, a refusal's among them**: a call the instrument
  refuses changes nothing and publishes nothing; a call it carries out publishes its event once; a
  patch bad only at its last entry in key order is refused whole, changing and publishing nothing,
  which catches an implementation that loads one value at a time; and a render no implementation
  could produce raises the package's render error, never a built-in exception or exhausted
  memory. Verified against `src/patchbay/testing/contract_tests.py`
  (`a_patch_refused_part_way_changes_nothing`, `an_impossible_render_raises_render_failed`, and
  the eleven beside them) and `tests/unit/testing/test_contract_tests.py` (`_LoadsUntilARefusal`,
  `_RendersAnyLength`).
- **The suite runs with function-scoped `bus` and `instrument` fixtures in the `conftest.py` beside
  the tests that run it**, the instrument built on the bus, and runs unchanged against whatever
  instrument the fixture returns. Verified against `tests/unit/testing/conftest.py` and
  `tests/unit/testing/test_contract_tests.py` (`test_contract`).

## In this repository

This repository has no package, so this standard does not apply here; Step 5b of its `shape-spec.md`
leaves it out.

## In a consuming project

Synced in as `agent-os/standards/base/testing/tests.md`, its rules the project's, verified against
the project's own files; Step 5b surfaces it from the index for a spec that writes or changes a
test.

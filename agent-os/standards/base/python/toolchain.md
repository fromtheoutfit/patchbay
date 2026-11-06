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

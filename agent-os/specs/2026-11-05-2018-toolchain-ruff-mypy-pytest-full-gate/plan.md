# Plan: issue #2 — Toolchain setup (pyproject.toml as the only config, ruff, mypy, pytest, hypothesis, pre-commit, the full gate)

## Context

Issue #2 (`gh issue view 2`) configures the Python toolchain every patchbay repository will use and
gives the gate real steps to run. It is the first spec with Python in it and the code the toolchain
base standard (patchbay-standards issue #4) will later be verified against, so **every
configuration choice is a Decision in `shape.md` with its reason**, and nothing is configured
anywhere but `pyproject.toml` (one accepted exception, below). This is a gate spec: `scripts/gate.sh`,
`scripts/gate-negative-tests.sh`, `.github/workflows/gate.yml` and the gate task in
`.claude/commands/agent-os/shape-spec.md` all change here, each new step with a negative test.

Shaped with `/agent-os:shape-spec` in plan mode; eight questions asked and answered by the owner
(recorded in `shape.md` under Shaping answers).

### Owner's answers (shaping)

1. **Runner:** the issue wins. Every step is `uv run --locked <tool>`; pins are `==` in
   `[dependency-groups] dev` with the publish date in a comment, resolved in `uv.lock`; the
   lockfile is the pin. Base proposal, in the owner's words: *"pins live in the script when the
   repository has no package manifest, otherwise in the lockfile the gate runs under --locked."*
   `tech-stack.md` corrected in Docs.
2. **Visuals:** none. 3. **References:** this repo's gate files + the sibling's `gate.sh` (pin
   comment style) and workflow (pinned setup-uv step). 4. **Version:** `0.0.1`, the issue's number,
   "the first deliberate version choice should be a deliberate number".
5. **Standards:** all five base standards, feature-specific; Step 5a tier still empty.
6. **pre-commit:** `.pre-commit-config.yaml` is the one file beside `pyproject.toml`, holding hook
   registration only: `repo: local`, `language: system`, `entry: uv run --locked ruff …`, so ruff's
   version has one pin (uv.lock) and its rules one home (pyproject.toml).
7. **Ruff ignores:** fix the code when the rule is right (write the docstring); ignore only when
   the rule is wrong for this tree, one comment per rule, from an actual `select = ["ALL"]` run.
8. **Hypothesis:** the property test exercises the version check's own pattern.

### Pins verified 2026-11-05 (PyPI JSON / GitHub API)

| Tool | Pin | Published |
|---|---|---|
| ruff | 0.17.4 | 2026-11-05 |
| mypy | 2.4.1 | 2026-10-28 |
| pytest | 9.2.0 | 2026-10-27 |
| hypothesis | 6.170.14 | 2026-10-30 |
| pre-commit | 4.7.0 | 2026-10-12 |
| uv (setup-uv `version:`, matches local Homebrew uv) | 0.13.7 | 2026-11-03 |
| astral-sh/setup-uv | `68559e99cc807c1eb7e9238fd43a15bba460eec2` # v10.3.3 | 2026-10-28 |
| actions/checkout (unchanged) | `3d3c42e5aac5ba805825da76410c181273ba90b1` # v7.0.1 | — |

Local: uv 0.13.7 at `/opt/homebrew/bin/uv`; a uv-managed CPython 3.12.16 is already present, so
`.python-version` = 3.12 resolves without any install. Nothing is installed outside the repo;
`uv sync` writes only `.venv/` (ignored) and the uv cache.

## Build order (owner's: gate green after each stage)

Stage A → B → C → D → E below; run `scripts/gate.sh` after each. The gate grows in stage C, so
A and B are checked with the two existing steps plus the tools run by hand.

## Task 1: Save spec documentation

Create `agent-os/specs/2026-11-05-HHMM-toolchain-ruff-mypy-pytest-full-gate/` (HHMM = save time):

- `plan.md` — this plan.
- `shape.md` — per the template in `shape-spec.md`: Core Architecture "None yet; see Step 5a",
  Scope (issue #2), Shaping answers (the eight above), **Decisions** (every configuration choice,
  each with its reason — list under "Decisions to record"), Context, Standards Applied, Verification
  Gate (results/Docs/Version filled at the end), Standards Retrospective (filled at the end).
  The first Decision cites issue #2 as the scope.
- `standards.md` — full text of the five base standards as they read now (snapshot).
- `references.md` — this repo's `scripts/gate.sh` (step/fail/banner shape, exit contract),
  `scripts/gate-negative-tests.sh` (mk/run/hdr/note, assertion, scratch guard),
  `.github/workflows/gate.yml` (layout, pin step); sibling `../patchbay-standards/scripts/gate.sh`
  (pin-with-date comment) and `.github/workflows/gate.yml` (setup-uv step pinned by commit with
  `version:`).
- `verification/` — `gate-run.txt`, `gate-negative-tests.txt`, `ci-negative-test.txt` at the end.

## Task 2 (stage A): pyproject.toml and uv.lock

Edit `pyproject.toml` only. Header comment at the top: the `[tool.*]` sections are the rule set
gate steps 2–5 read and change only in the gate's own spec; `[project]` and
`[dependency-groups]` are the project's and change in any spec (adding a dependency is a
Decision). No `setup.py`, `setup.cfg`, `requirements*.txt`, `tox.ini`, `.flake8`, `mypy.ini`,
`pytest.ini`, `.ruff.toml`.

- `[project]`: `version = "0.0.1"`, `license = "MIT"` (PEP 639 SPDX string; `LICENSE` exists),
  description/readme/authors/requires-python as they are, `dependencies = []`.
- `[build-system]` and `[tool.uv.build-backend]` unchanged (`uv_build>=0.13.7,<0.14.0`,
  `module-name = "patchbay"`).
- `[dependency-groups] dev = [ "ruff==0.17.4", # published 2026-11-05 … ]` for ruff, mypy,
  pytest, hypothesis, pre-commit (pins from the table, one date comment each). Each is a
  Decision: what it does, why stdlib cannot, its license (ruff MIT, mypy MIT, pytest MIT,
  hypothesis MPL-2.0, pre-commit MIT).
- `[tool.ruff]`: `target-version = "py312"`, `line-length = 100` (comment: why 100).
  `[tool.ruff.lint] select = ["ALL"]`; `ignore = [...]` **built from the run** (Task 3 writes the
  code first, then: run `uv run ruff check .`, read every rule tripped, fix the code where the
  rule is right, add an ignore with a one-line comment where the rule is wrong for this tree —
  expected from experience but *not written until seen*: the formatter-conflict pair
  `COM812`/`ISC001` that ruff itself warns about under ALL, the mutually exclusive pydocstyle
  pairs `D203`/`D211` and `D212`/`D213`). `[tool.ruff.lint.per-file-ignores] "tests/**" = [...]`
  likewise from the run (expected: `S101` assert, `PLR2004` magic values, possibly `INP001` if
  tests stay a non-package). `ruff format` is the formatter; no black.
- `[tool.mypy]`: `strict = true`, `files = ["src", "tests"]`, `warn_unreachable = true`,
  `implicit_reexport = false` (explicit though strict implies it, as the issue names it),
  `python_version = "3.12"`. No `[[tool.mypy.overrides]]` yet; a comment says where one goes and
  that each needs its reason.
- `[tool.pytest.ini_options]`: `testpaths = ["tests"]`,
  `addopts = "-q --strict-markers --strict-config"` (`--strict-config` so an unknown key fails the
  step, per the gate standard's "a config the tool cannot parse fails the step"),
  `markers = ["integration: needs a running instrument; not run by the gate by default"]`.
- Then `uv lock` (resolves the dev group; uv.lock gains the five tools and their deps) and
  `uv sync --locked`. Check: `uv run --locked ruff --version` etc. print the pins.

Gate check after A: `scripts/gate.sh` (two steps) green; `uv lock --check` clean.

## Task 3 (stage B): the package and the two tests

- `src/patchbay/__init__.py`: module docstring; `from importlib.metadata import version`;
  `__version__ = version("patchbay-core")`; `__all__ = ["__version__"]`. Nothing else. `py.typed`
  stays.
- `tests/conftest.py`: a docstring only ("shared fixtures; none yet").
- `tests/unit/test_version.py`:
  - `test_version_matches_pyproject`: read `pyproject.toml` with `tomllib` (path from
    `Path(__file__).parents[2]`), assert `patchbay.__version__ == project.version`.
  - `test_version_is_a_release_segment`: `_RELEASE = re.compile(r"\d+(\.\d+)*")` fullmatches
    `__version__`.
  - Hypothesis: `@given(st.tuples(st.integers(min_value=0), ×3))` → `f"{a}.{b}.{c}"` fullmatches
    `_RELEASE`; and `@given(st.text(min_size=1).filter(lambda s: not s.isdigit()))` → a
    non-numeric segment does not. Exercises hypothesis under mypy --strict.
- `tests/__init__.py` / `tests/unit/__init__.py`: decided by the ruff run (INP001) and recorded;
  default is no `__init__.py` with `INP001` ignored for `tests/**` and the reason.
- Run `uv run --locked ruff format --check .`, `ruff check .` (build the ignore list here, per
  answer 7), `mypy`, `pytest`; all clean. Gate (two steps) green.

## Task 4 (stage C): scripts/gate.sh — six steps, and the negative tests

`scripts/gate.sh` steps, in order: 1 `bash -n` (as is) · 2 `uv run --locked ruff format --check .`
· 3 `uv run --locked ruff check .` · 4 `uv run --locked mypy` · 5 `uv run --locked pytest` ·
6 `scripts/sync-standards.sh --check` (as is). Banners `N/6`; `fail N/6 "<reason>"` after each;
closing line names steps 7–9 as judgment. Header rewritten: the pins section says the tool pins
are the `==` entries of `[dependency-groups] dev` in `pyproject.toml`, resolved in `uv.lock`, run
under `--locked` so a stale lock fails the step rather than being rewritten; `[tool.*]` is the
rule set; what each step needs (uv on PATH; network the first time). `--locked` is a Decision:
the gate writes nothing, and a lock that disagrees with `pyproject.toml` is a failure by name.

`scripts/gate-negative-tests.sh`:
- `mk` also copies `pyproject.toml`, `uv.lock`, `.python-version`, `README.md` (the build backend
  reads it), `src/`, `tests/`. Each copy syncs its own `.venv` from the uv cache on first
  `uv run`.
- New cases, each asserting its status and that later steps are never reached:
  - **h** misformatted `src/patchbay/_broken.py` (`x  =  1`): step 2 fails naming it, exit 1.
  - **i** well-formatted file with an unused import: step 2 passes, step 3 fails (F401), exit 1.
  - **k** `tests/unit/test_broken.py` that passes ruff but returns `Any` from a function typed
    `-> int` (`json.loads`): step 4 fails under `strict` only (`warn_return_any`), showing the
    strict value applied, exit 1.
  - **l** a test asserting `__version__ == "9.9.9"`: steps 2–4 pass, step 5 fails, exit 1.
  - **m** config: `line-length` lowered to 40 in the copy's `pyproject.toml` makes the clean tree
    fail step 2 (a changed value applied, per the gate standard); an unparsable `pyproject.toml`
    (a stray `[`) fails step 2 by name.
  - **n** a dev pin edited in `pyproject.toml` without re-locking: step 2 fails with uv's
    lockfile message (`--locked` proven), exit 1.
- Existing a–g, u keep passing; **j** replays the workflow's new `uv sync --locked` run step too.
- Header updated: cases, what `mk` copies, time (each case syncs a venv from cache), needs uv.
- Run `scripts/gate-negative-tests.sh` → `verification/gate-negative-tests.txt`; `… j` →
  `verification/ci-negative-test.txt` (after stage E).

Gate (six steps) green after C.

## Task 5 (stage D): pre-commit

`.pre-commit-config.yaml` (the one file beside `pyproject.toml`; it configures no tool):
header comment saying so; `minimum_pre_commit_version: "4.7.0"`; `repos: - repo: local` with two
hooks, `ruff-format` (`entry: uv run --locked ruff format`) and `ruff-check`
(`entry: uv run --locked ruff check --fix`), `language: system`, `types_or: [python, pyi]`.
Never mypy or pytest. Verify: `uv run --locked pre-commit validate-config` and
`uv run --locked pre-commit run --all-files` (does **not** run `pre-commit install`; the hook
install into `.git/hooks` is the owner's choice — README says how). Gate green after D.

## Task 6 (stage E): CI

`.github/workflows/gate.yml`: after the second checkout, `astral-sh/setup-uv@68559e99… # v10.3.3`
with `version: "0.13.7"`, `enable-cache: true`, `cache-dependency-glob: "patchbay/uv.lock"`,
`working-directory: patchbay`; then `run: uv sync --locked` with `working-directory: patchbay`;
then `scripts/gate.sh` as is. Header rewritten: why the runner returns, the cache keyed on
`uv.lock` (a Decision and a deviation from the base "caches nothing", proposed), one job, the
script and nothing else. Replay with test **j** before any push (the owner pushes); the hosted
run id is recorded by the owner in `ci-negative-test.txt` afterwards.

## Task 7: Docs, CHANGELOG, product doc

- `README.md`: Layout (src now has code; `tests/`; `.pre-commit-config.yaml`), **Install**
  (`uv sync`), the gate's six steps and exit contract, pre-commit (`uv run pre-commit install`),
  the one-config-file rule and its one exception.
- `CLAUDE.md` Specs section: gate step list updated to six; gate's own files list gains
  `pyproject.toml`'s `[tool.*]` sections and `.pre-commit-config.yaml`? — no: pre-commit is not a
  gate file; only `[tool.*]` is named as the rule set.
- `.claude/commands/agent-os/shape-spec.md` gate task (Task N), Step 8 and the shape.md template
  paragraph: six runnable steps, then Docs, Version, retrospective. (Gate file; this is a gate spec.)
- `agent-os/product/tech-stack.md`: first bullet corrected — tools pinned in `pyproject.toml`'s
  dev group, resolved in `uv.lock`, run by the gate through `uv run --locked`.
- `CHANGELOG.md` `[Unreleased]`: Added entry for this spec (each file, the pins, the six steps,
  the negative tests, pre-commit, CI); version set to 0.0.1 noted. `.python-version` stays 3.12.

## Task 8 (FINAL): Verification gate

1. `scripts/gate.sh` green, as the last act, transcript → `verification/gate-run.txt` with date
   and branch on line 1. Negative tests rerun after the last edit to any gate file.
2. **Docs**: read README, CLAUDE.md, tech-stack.md, every changed file's header, shape-spec.md's
   gate task and the standards that name them (`verification-gate.md`, `standards-sync.md`,
   `ownership.md`) against the shipped tree; record in `shape.md`.
3. **Version**: CHANGELOG entry; `pyproject.toml` 0.0.1 (the issue's number, not a release
   bump); record.
4. **Standards retrospective** (last), from the shipped diff. No project standard exists; Step 5a
   stays empty (the toolchain standard is written in `patchbay-standards`, issue #4, verified
   against this code). `index.yml` untouched. Proposals under `(proposed, base)`:
   - `verification-gate.md` "Pinned": the owner's wording on where pins live (script vs
     lockfile under `--locked`); the rule-set config may be the `[tool.*]` sections of the
     package manifest, whose other sections change in any spec; verified against
     `pyproject.toml`, `scripts/gate.sh`, test n.
   - `verification-gate.md` "CI": a cache keyed on the lockfile is not a moving part;
     "install the runner" is setup-uv pinned + `uv sync --locked`; verified against `gate.yml`
     and test j.
   - Anything the ruff/mypy run teaches about "fix at its cause" vs per-file-ignores for tests.
5. Then stop and print `git status --short`. No stage, commit, push or PR.

## Decisions to record in shape.md (each with its reason)

Issue #2 as scope · uv run --locked over uvx (owner) · `==` pins with dates in the dev group,
uv.lock the resolution · each dev dependency (purpose, why not stdlib, license) · version 0.0.1
(owner) · `license = "MIT"` SPDX · ruff target-version/line-length 100/select ALL · every ignore
and per-file-ignore from the run, with its comment (owner: fix when right, ignore when wrong) ·
tests as a non-package or not (from the run) · mypy strict/files/warn_unreachable/
implicit_reexport/python_version · pytest testpaths/addopts (incl. `--strict-config`)/integration
marker · `[tool.*]` as the gate's rule set within a file whose other sections change in any
spec · six-step order · `.pre-commit-config.yaml` the one exception, local hooks via uv run
(owner), never mypy/pytest · setup-uv pinned by commit with `version: 0.13.7`, cache keyed on
`uv.lock`, `uv sync --locked` before the gate · each new negative test's shape (h i k l m n) ·
`.python-version` stays 3.12.

## Verification (how to test end to end)

- `uv sync --locked && scripts/gate.sh` exits 0 with six `==` banners.
- `scripts/gate-negative-tests.sh` ends `N runs, 0 unexpected`; `… j` likewise.
- `uv run --locked pre-commit run --all-files` passes.
- Edit `pyproject.toml` `line-length` → gate fails at step 2 (then revert) — covered by m.
- `git status --short` lists only: `pyproject.toml`, `uv.lock`, `src/patchbay/__init__.py`,
  `tests/`, `scripts/gate.sh`, `scripts/gate-negative-tests.sh`, `.pre-commit-config.yaml`,
  `.github/workflows/gate.yml`, `README.md`, `CLAUDE.md`, `CHANGELOG.md`,
  `.claude/commands/agent-os/shape-spec.md`, `agent-os/product/tech-stack.md`, the spec folder.

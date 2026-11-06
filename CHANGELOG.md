# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The base standards under `agent-os/standards/base/` are pinned to the commit in `base/.version`;
a sync forward is recorded here as its own entry.

## [Unreleased]

### Added

- Third spec, `agent-os/specs/2026-11-05-2018-toolchain-ruff-mypy-pytest-full-gate/` (issue #2):
  the Python toolchain, configured in `pyproject.toml` and nowhere else, and the gate given real
  steps. Every configuration choice is a Decision in the spec's `shape.md`; this is the code the
  toolchain base standard (patchbay-standards issue #4) is verified against.
  - `pyproject.toml`: version 0.0.1 (the first deliberate number; uv's scaffold said 0.1.0),
    `license = "MIT"` with `license-files = ["LICENSE"]`, `[tool.uv] required-version =
    "==0.13.7"` pinning uv itself, and `[dependency-groups] dev` pinned exactly with publish
    dates: ruff 0.17.4, mypy 2.4.1, pytest 9.2.0, hypothesis 6.170.14, pre-commit 4.7.0, resolved
    in `uv.lock`. `[tool.ruff]` (py312, line length 100, `select = ["ALL"]`, the ignores the tree
    tripped with a comment each: D203, D213, COM812, CPY001; `tests/**` ignoring S101 and INP001),
    `[tool.mypy]` (strict over `src` and `tests`, `warn_unreachable`, `implicit_reexport = false`,
    3.12), `[tool.pytest.ini_options]` (`tests`, `-q --strict-markers --strict-config`, the
    `integration` marker). The header names the `[tool.*]` sections as the gate's: the uv pin and
    the rule set.
  - `src/patchbay/__init__.py` exports `__version__` from the installed metadata and nothing else,
    and is imported installed; `tests/unit/test_version.py` holds the version test against
    `pyproject.toml` and the hypothesis properties of the release-segment pattern it uses;
    `tests/unit/test_package.py` holds the package's surface to `__all__` and its metadata to the
    shipped `LICENSE`.
  - `scripts/gate.sh`: six steps, `bash -n`, `uv sync --locked` then `uv run --locked ruff format
    --check .`, `uv run --locked ruff check .`, `uv run --locked mypy`, `uv run --locked pytest`,
    then `scripts/sync-standards.sh --check`; the header says the pins are the dev group's and
    uv's is `[tool.uv]`'s, and that step 2's sync fails by name on a stale lockfile, which is
    never rewritten, or the wrong uv. `scripts/gate-negative-tests.sh` copies the package files
    into each scratch case and gains h (a misformatted module), i (an unused import), k (`Any`
    returned as `int`, a strict-only error), l (a failing test), m (a changed `line-length`
    applied; a value ruff refuses; TOML uv refuses), n (a pin edited without re-locking) and o (a
    `required-version` the running uv does not satisfy); j replays the workflow's
    `uv sync --locked` step.
  - `.pre-commit-config.yaml`: local hooks `ruff check --fix` then `ruff format` through `uv run
    --locked`, so ruff has one pin and one rule set; never mypy or pytest.
  - `.github/workflows/gate.yml`: `astral-sh/setup-uv` v10.3.3 pinned by commit, installing the uv
    `[tool.uv] required-version` pins, the cache on and keyed on `uv.lock`, `uv sync --locked`
    from `patchbay/`, then the gate.
  - `README.md` (install, the six steps, pre-commit, the one-config-file rule),
    `agent-os/product/tech-stack.md` (`uv run --locked` and the lockfile as the pin, correcting
    issue #1's `uvx`), `CLAUDE.md` and `shape-spec.md`'s gate task (the six steps).

- First spec, `agent-os/specs/2026-11-05-1733-bootstrap-shape-spec-gate-ci-docs/` (issue #1): the
  frame every later spec lands in, before any Python tooling.
  - `.claude/commands/agent-os/shape-spec.md` customized for a consuming project: the two kinds of
    standards, an empty Step 5a tier that the toolchain, layout and typing standards will fill,
    the snapshot paragraph, the rule that a base standard is never edited here but proposed in
    `shape.md` and sent to `patchbay-standards` as a pull request, and the final verification-gate
    task with this repository's steps followed by Docs, Version and the standards retrospective.
    The other four commands stay stock.
  - `CLAUDE.md`: Git, No AI attribution and Ownership as `patchbay-standards` has them (the
    sibling's uv history dropped and the base pointer resolving here), the consuming-project line,
    and the Specs section naming `scripts/gate.sh` as the definition of done and the gate's own
    files.
  - `scripts/gate.sh`: two runnable steps, `bash -n` on every shell script under `scripts/` as git
    lists them (any other file there fails the step by name) and `scripts/sync-standards.sh
    --check` against `../patchbay-standards` at the pinned commit; stops
    at the first failure naming the step on stderr, exit 1; exit 2 on usage; no tool pin yet, the
    place for them marked for the toolchain spec.
  - `.github/workflows/gate.yml`: one job on every pull request and every push to `main`, which
    checks this repository out into `patchbay/`, reads the commit pinned in
    `agent-os/standards/base/.version` and checks `fromtheoutfit/patchbay-standards` out beside it
    at that commit, then runs `scripts/gate.sh` from `patchbay/`. `actions/checkout` v7.0.1 pinned
    by commit, `ubuntu-24.04`, a ten-minute timeout, no persisted credential, no cache, no runner
    installed until a step needs one.
  - `scripts/gate-negative-tests.sh`: a (an unparsable script), b (a one-byte edit under
    `agent-os/standards/base/`), c (a hand-edited `base:` entry), d (the sibling checkout
    missing), e (the synced script edited), f (an extra file under `base/`), g (step 1's file
    list), u (usage, and the clean copy passing) and j (the CI replay of the workflow's run
    steps), each on a scratch copy beside a scratch clone of `patchbay-standards`, each run
    asserting its expected status. Transcripts in the spec that last changed a gate file.
  - `README.md`: what patchbay is and is not, the names, the layout, the gate, the sync.
  - `pyproject.toml`: the description, in place of the scaffold's placeholder.
  - `agent-os/product/mission.md` and `tech-stack.md`: what core is and is not, and the
    toolchain decisions the next spec implements.
  - This file.

### Changed

- Fourth spec, `agent-os/specs/2026-11-05-2057-toolchain-revision-after-pr-4-review/`, the gate's
  spec for the revision after the owner's review of PR 4 (eleven findings, each with its
  disposition in the spec's `plan.md`): `pyproject.toml` sets `license-files = ["LICENSE"]`, so
  the wheel ships the MIT text it names, and pins uv in `[tool.uv] required-version`, which
  `.github/workflows/gate.yml`'s setup-uv now reads instead of a second copy of the version;
  `scripts/gate.sh` step 2 opens with `uv sync --locked` and its own failure reason, so a stale
  lockfile or the wrong uv is no longer reported as a formatting failure;
  `scripts/gate-negative-tests.sh` gains o (a `required-version` the running uv does not
  satisfy), n and m name the sync, and its header is re-wrapped; `src/patchbay/__init__.py`
  imports `importlib.metadata` under a private alias, so `version` no longer leaks onto the
  package, and says it is imported installed; `tests/unit/test_version.py` holds the version to
  ASCII digits (`[0-9]`, not `\d`), generates only single non-numeric segments, and reads
  `pyproject.toml` from pytest's rootdir; `tests/unit/test_package.py` is new; `tests/conftest.py`
  is removed until a fixture is shared; `CLAUDE.md` and `shape-spec.md` name the base proposals'
  heading as the template has it, `### Standards retrospective (proposed, base)`.

- Second spec, `agent-os/specs/2026-11-05-1759-gate-revision-after-pr-3-review/`, the gate's spec
  for the revision after the owner's review of PR 3 (ten findings, each with its disposition in
  the spec's `plan.md`): `scripts/gate.sh` step 1 lists files with git and parses shell scripts
  only, refusing any other file, a tracked file missing from the disk and a tree that is not a
  work tree, each by name; `.github/workflows/gate.yml` checks `patchbay-standards` out at the
  commit in `.version` through a pin step instead of `main` with full history, and no longer
  installs uv; `scripts/gate-negative-tests.sh` refuses a scratch directory it did not get from
  `mktemp` or that lies inside the repository, dies on any setup failure, asserts every run's
  exit status and exits 1 on a mismatch, and gains e, f and g; the hosted run 42124784656 is
  recorded in the spec's `verification/ci-negative-test.txt`; `shape-spec.md`'s Step 5a names the
  template's heading and Step 5b the reserved `root` section; `pyproject.toml` carries the
  README's description; `.gitignore` ignores `.DS_Store`.

The scaffold predates the first spec: the `patchbay-core` package (`src/patchbay/`, Python 3.12,
`uv_build`, the lockfile), the base standards synced in at `b3fc2fe` with
`scripts/sync-standards.sh` and the `base:` section of `agent-os/standards/index.yml`, and the
stock Agent OS commands.

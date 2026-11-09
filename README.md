# patchbay

Headless control of software instruments from Python: the contracts, host and CLI that
`patchbay-<instrument>` adapters plug into.

This is an experiment, not a product. The distribution name is `patchbay-core` and the import
name is `patchbay`. Nothing synth-specific lives here; core grows only when a second adapter needs
the same thing (`agent-os/product/mission.md`).

## Layout

- `src/patchbay/`: the package, src layout, typed (`py.typed`).
  - `contracts.py`: the `Instrument` protocol every adapter implements, and the `Subscriber` its
    events reach.
  - `models.py`: the frozen, strict pydantic models that cross a boundary (`Quantity`,
    `Parameter`, `Patch`, `Pattern`, `RenderRequest`, `RenderResult` and the rest), all built on
    `PatchbayModel`, which takes data in JSON's form (as `json.loads`, YAML or TOML give it)
    through `from_json_data`. `RenderRequest.samples` is the one count of a render's samples.
  - `events.py`: the events (`ParameterChanged`, `PatchLoaded`, `RenderCompleted`) and the
    synchronous, in-process `EventBus`, whose `subscribe` returns a `Subscription` that
    `cancel()` ends.
  - `errors.py`: `PatchbayError` and the errors under it; no built-in exception leaves a public
    method.
  - `testing/`: what an adapter's tests use: `CONTRACT_TESTS`, thirteen contract tests named
    without a `test_` prefix, so pytest never collects one an adapter imports; the reference
    `FakeInstrument`; and `RecordingSubscriber`.

  `__init__.py` re-exports the first four, and `__version__`, read from the installed package's
  metadata so `pyproject.toml` is the one place the version is written. The package is imported
  installed (`uv sync`): from a bare `src/` on `sys.path` the import fails rather than invent a
  version. The runtime dependencies are pydantic, numpy and pydantic-core, which pydantic brings
  and which is declared since `errors.py` imports it, each a range in `[project] dependencies`.
- `tests/`: pytest's tree, `unit/` for now, mirroring `src/` one test module per source module;
  `unit/testing/conftest.py` holds the `bus` and `instrument` fixtures an adapter's own
  `conftest.py` copies to run the contract tests. Not a package (no `__init__.py`), so one basename
  per test file across it, which mypy holds.
- `pyproject.toml`: the one configuration file. Every tool the gate runs is configured under
  `[tool.*]` there and nowhere else, with no `setup.py`, `setup.cfg`, `requirements*.txt`,
  `tox.ini`, `.flake8`, `mypy.ini`, `pytest.ini` or `.ruff.toml`. The `[tool.*]` sections (the rule
  set, and `[tool.uv]`, which pins uv itself) and the dev group's pins of the tools the gate runs
  (ruff, mypy and pytest), with what `uv.lock` resolves for them, are the gate's and change only in
  the gate's own spec; `[project]`, `[build-system]` and the dev group's other entries (hypothesis
  and pre-commit) are the package's. `uv.lock` is the resolution of the pins. The wheel carries
  `LICENSE` (`license-files`).
- `.pre-commit-config.yaml`: hook registration only, the one file pre-commit cannot do without;
  it configures no tool.
- `scripts/`: `gate.sh` (the verification gate), `gate-negative-tests.sh` (the tests that prove
  each gate step can fail, not run by the gate) and `sync-standards.sh` (installed and replaced by
  the standards sync, never hand-edited).
- `agent-os/product/`: `mission.md` and `tech-stack.md`, the decisions the specs implement.
- `agent-os/standards/`: `base/`, the base standards synced from `patchbay-standards` and pinned
  to the commit in `base/.version`, read-only here; `index.yml`, whose `base:` section is the
  sync's and whose other sections are this repository's own.
- `agent-os/specs/`: one folder per spec, with its plan, shaping notes, the standards as they
  read when it was shaped, and `verification/` holding the gate transcripts.
- `.claude/commands/agent-os/`: the Agent OS commands; `shape-spec.md` is customized for this
  repository's gate, the rest are stock.
- `.github/workflows/gate.yml`: CI, which runs the gate and nothing else.
- `CLAUDE.md`: the rules for an agent working here, ownership first.

## Install

```sh
uv sync
```

uv is the one tool this repository assumes, at 0.13.7: `pyproject.toml`'s `[tool.uv]
required-version` pins it, so any other uv refuses every command that reads this project's
settings (`uv sync` and `uv run` among them), and CI's setup-uv reads the same key to install it.
`uv sync` reads `.python-version` (3.12), fetches that interpreter into uv's cache if it is not
there, creates `.venv/` and installs into it the package with its dependencies, pydantic,
pydantic-core and numpy, and the locked dev toolchain: ruff, mypy, pytest, hypothesis and
pre-commit, each pinned exactly in `pyproject.toml`'s `[dependency-groups] dev` with the date it
was published. `uv.lock` resolves both. Nothing is installed outside the repository.
Run a tool as `uv run --locked <tool>`, as the gate does.

## The gate

```sh
scripts/gate.sh
```

Six runnable steps, in order, stopping at the first failure (exit 1; exit 2 on usage or when the
script cannot enter the repository root):

1. `bash -n` on every shell script under `scripts/` as git lists them, tracked or untracked and
   not ignored, at a work-tree top that is the repository root; a tracked file a step reads that a
   `.gitignore` ignores, a file there that is neither `.sh` nor bash-shebanged, a listed path missing from the
   disk, a symlink to nothing and a listing git cannot make (a corrupt index) each fail the step
   by name.
2. `uv sync --locked`, then `uv run --locked ruff format --check` over the `.py` and `.pyi` files
   git lists: the locked toolchain syncs, and every file is formatted as ruff format writes it.
3. `uv run --locked ruff check` over the same files: no violation of `[tool.ruff.lint]`, which
   selects every rule and ignores only what this tree proved wrong, each with its reason.
4. `uv run --locked mypy` over the `.py` and `.pyi` files git lists under `src/` and `tests/`: no
   type error under `strict`.
5. `uv run --locked pytest`: every test under `tests/` passes, once no `.py` file there, and no
   `conftest.py` at the root, is one git ignores.
6. `scripts/sync-standards.sh --check`: `agent-os/standards/base/`, the `base:` section of
   `agent-os/standards/index.yml` and the sync script itself are byte-identical to
   `patchbay-standards` at the pinned commit.

Step 2 opens with `uv sync --locked`, which installs exactly what `uv.lock` names and fails the step
as the sync, before any tool runs, when a pin was edited in `pyproject.toml` without `uv lock` (the
lockfile is never rewritten), when uv cannot read either file or build the package from them, or
when the running uv is not the required one; so the gate writes nothing but the ignored `.venv/` and
caches. A `uv.toml` at the root fails the step by name before uv runs, since uv would read it ahead of
`[tool.uv]`. Steps 2 to 5 then run each tool under `--locked`, the one `uv.lock` names, told by flag
to read `pyproject.toml` alone, so a `ruff.toml`, `mypy.ini` or `pytest.ini` beside it, tracked or
not, cannot replace the rule set, and read only the files git lists: ruff and mypy are given git's list itself, so git alone decides what is
ignored; pytest, which loads the `conftest.py` of
every directory it collects from, walks `tests/` only once nothing it would read is ignored, and
reads no `.txt` (`-p no:doctest`). Step 6 reads the sibling checkout at `../patchbay-standards`, so
clone `patchbay-standards` beside this repository first; CI checks it out there at the pinned
commit, installs uv with `astral-sh/setup-uv` at the version `[tool.uv] required-version` pins,
runs `uv sync --locked` and then the script. Three
judgment steps follow the script and are recorded in each spec's `shape.md`: Docs, Version and the
standards retrospective. The rule is `agent-os/standards/base/process/verification-gate.md`.

`scripts/gate-negative-tests.sh` runs each failure case on a scratch copy (`all` adds the CI
replay); its transcripts live in the spec that last changed a gate file.

## pre-commit

```sh
uv run --locked pre-commit install           # once, to run the hooks on every commit
uv run --locked pre-commit run --all-files   # the hooks over the tree, with or without the git hook
```

The hooks are `ruff check --fix` and `ruff format`, run through `uv run --locked`, so they are the
gate's ruff with the gate's rules; never mypy or pytest, which are the gate's. The hook is a
convenience for the person committing; `scripts/gate.sh` is the check.

## Syncing the standards

```sh
scripts/sync-standards.sh                 # move the pin to patchbay-standards' origin/main
scripts/sync-standards.sh --check         # the drift check, as the gate runs it
scripts/sync-standards.sh --index-only    # regenerate the base: section of index.yml alone
```

The pin is the commit in `agent-os/standards/base/.version`. A sync forward is its own change
set, titled `chore: sync base standards to <sha>`. No file under `base/` and no `base:` entry is
edited here: a change to a base standard is proposed in a spec's retrospective, presented to the
owner, and filed as an issue on `patchbay-standards`, whose own spec lands it as a pull request.
The rule is `agent-os/standards/base/process/standards-sync.md`.

## Specs

Work is shaped with `/agent-os:shape-spec` in plan mode and ends with the gate. `CLAUDE.md`
holds the rules an agent follows here, `## Ownership` first: a person owns every commit, pull
request and merge.

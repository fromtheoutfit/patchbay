# Toolchain setup: pyproject.toml as the only config, ruff, mypy, pytest, hypothesis, pre-commit, the full gate — Shaping Notes

Shaped 2026-11-05 in plan mode with this repository's customized `/agent-os:shape-spec`, the Step
1–5 questions and four design choices asked and answered by the owner (recorded under Shaping
answers and Decisions). The first spec with Python in it, and the code the toolchain base standard
(patchbay-standards issue #4) is verified against: every configuration choice below is a Decision
with its reason.

## Core Architecture (Non-Negotiable)

None yet; see Step 5a of `.claude/commands/agent-os/shape-spec.md`. The toolchain, layout and
typing standards will fill this tier; they are written in `patchbay-standards` from the code this
spec ships, not here.

## Scope

GitHub issue #2, "Toolchain setup: pyproject.toml as the only config, ruff, mypy, pytest,
hypothesis, pre-commit, the full gate". Configure the Python toolchain this repository and every
patchbay repository will use, and give every gate step something real to run: `pyproject.toml` as
the one configuration file, the dev dependency group resolved in `uv.lock`, the package exporting
`__version__`, the two tests, four new gate steps each with a negative test, pre-commit, and CI
with setup-uv back, pinned, with `uv sync` and caching. Built in the owner's order with the gate
green after each stage: pyproject.toml and the lockfile; the package and the tests; the gate steps
and their negative tests; pre-commit; CI. Gate green, `verification/gate-run.txt` with date and
branch; no commit, PR or push by an agent.

## Shaping answers

- **Step 1, scope:** issue #2 as written. The one conflict settled: the issue's `uv run` with pins
  in the dev group and `uv.lock` wins over `tech-stack.md`'s and the base gate standard's "pinned
  in the script, run through `uvx`". Owner: "For a Python package the lockfile is the pin, and mypy
  and pytest can't work from uvx anyway because they need the project installed. The base
  standard's 'pins in the script' was written from the standards repo, where there's no project —
  this is exactly the kind of rule a second consumer corrects. Propose upstream: 'pins live in the
  script when the repository has no package manifest, otherwise in the lockfile the gate runs under
  --locked.'"
- **Step 2, visuals:** none.
- **Step 3, references:** this repository's gate files and the sibling's `gate.sh` and workflow;
  see `references.md`.
- **Step 4, product context:** `tech-stack.md`'s decisions hold, its `uvx` line corrected in Docs.
  Version: `0.0.1` as the issue says; owner: "0.0.1 says 'nothing here yet' more honestly than
  uv's default, and the first deliberate version choice should be a deliberate number."
- **Step 5, standards:** all five base standards, feature-specific; the Step 5a tier is empty.
- **pre-commit:** `.pre-commit-config.yaml` is the one file beside `pyproject.toml`, holding hook
  registration only, with `repo: local` hooks that run ruff through `uv run --locked`, so ruff has
  one pin and one rule set (owner's choice over the `ruff-pre-commit` mirror, which would state
  the version a second time).
- **Ruff ignores:** fix the code when the rule is right; ignore only when the rule is wrong for
  this tree, one comment per rule, from an actual `select = ["ALL"]` run (owner's choice over
  ignoring everything the first run tripped).
- **Hypothesis:** the property test exercises the version check's own pattern (owner's choice
  over a bare smoke property).

## Decisions

Every configuration choice, with its reason. The configuration itself is `pyproject.toml`; the
comments there say the same things in fewer words.

- **GitHub issue #2 is the scope.** Its sections (pyproject.toml, code and tests, scripts/gate.sh,
  pre-commit, CI, Docs) are the tasks; its "Rules" paragraph is this spec's definition of done.
  Nothing outside it changes but this spec folder, `CHANGELOG.md`, `agent-os/product/tech-stack.md`
  and the gate task text in `shape-spec.md`, a gate file this gate spec may change.
- **This is a consuming project.** No file under `agent-os/standards/base/` and no line of the
  `base:` section of `index.yml` is edited; `scripts/sync-standards.sh` is the synced copy. What
  this spec teaches a base standard is proposed below.
- **Every tool runs as `uv run --locked <tool>`; the lockfile is the pin** (owner). mypy and pytest
  need the package installed, which `uvx` cannot give them; a package's lockfile is already its
  pin, so a second pin in the script would be a copy to keep equal. `--locked` makes the lockfile
  authoritative: a pin edited in `pyproject.toml` without `uv lock` fails the step with uv naming
  the stale lockfile (test n) instead of being rewritten, so the gate writes nothing but the
  ignored `.venv/` and caches. This deviates from `verification-gate.md` "Pinned" as it reads
  ("pinned in the script ... without installing it into the project") and from `tech-stack.md`'s
  `uvx` line; the first is proposed below in the owner's words, the second corrected.
- **The dev group pins exactly, with the publish date beside each**, in `[dependency-groups] dev`:
  `ruff==0.17.4` (published 2026-11-05), `mypy==2.4.1` (2026-10-28), `pytest==9.2.0`
  (2026-10-27), `hypothesis==6.170.14` (2026-10-30), `pre-commit==4.7.0` (2026-10-12). Each
  verified to exist on PyPI on 2026-11-05 (the JSON API's `info.version` and earliest upload
  time); ruff's was published that day, and the `ruff-pre-commit` mirror carried the same tag.
  `==` rather than a range because the comment beside the pin is then the version a reader sees,
  and `uv.lock` resolves to it either way. `uv lock` resolved 26 packages; `uv lock --check` is
  clean.
- **Each dependency, as the issue asks** (what it does, why the standard library cannot, its
  license). ruff: lints and formats; the standard library has no linter or formatter (MIT). mypy:
  checks the types the code declares; `typing` declares them and checks nothing (MIT). pytest:
  discovers and runs tests with plain `assert`, rewriting it to report values; `unittest` needs
  classes and `self.assert*` and has no fixtures or markers (MIT). hypothesis: property-based tests
  with generated, shrunk inputs; nothing in the standard library generates or shrinks (MPL-2.0).
  pre-commit: runs hooks from `.pre-commit-config.yaml` on the staged files at commit; a hand-written
  `.git/hooks/pre-commit` is unversioned and per-clone (MIT). pydantic and typer, named in
  `tech-stack.md`, are not added: nothing here crosses a boundary or has a CLI yet, and a
  dependency is added by the spec that uses it.
- **`version = "0.0.1"`** (owner): the first deliberate number; uv's scaffold said 0.1.0 and the
  last two specs left it, this one chooses. `uv.lock` records it. `tests/unit/test_version.py`
  holds `__version__` to whatever `pyproject.toml` says, so a later bump is one edit.
- **`license = "MIT"`**, the PEP 639 SPDX string, since `LICENSE` is MIT and `uv_build` accepts the
  form (the lock and the editable build both succeeded with it). No `license-files`: the default
  glob finds `LICENSE`.
- **`pyproject.toml` is the one configuration file**, and says so in its header: no `setup.py`,
  `setup.cfg`, `requirements*.txt`, `tox.ini`, `.flake8`, `mypy.ini`, `pytest.ini` or `.ruff.toml`.
  Two kinds of section: `[project]`, `[build-system]` and `[dependency-groups]` are the package's
  and change in any spec (adding a dependency is a Decision there); the `[tool.*]` sections are
  the rule set gate steps 2–5 read and are gate files, changed only in the gate's own spec. That
  split is what lets a file the gate standard says "changes only in the gate's own spec" also carry
  the project's metadata; proposed below. The one file beside it is `.pre-commit-config.yaml`,
  because pre-commit cannot read hooks from `pyproject.toml`; it registers hooks and configures no
  tool, and the issue names it.
- **ruff: `target-version = "py312"`**, the floor of `requires-python`, stated so the rule set never
  silently follows a raised floor; **`line-length = 100`**, wide enough that a typed signature or a
  pydantic field with its description stays on one line, narrow enough for a split editor and a
  GitHub diff; **`select = ["ALL"]`**. `ruff format` is the formatter; no black.
- **The ignore list is what the tree tripped, nothing copied from memory.** The code and tests were
  written with docstrings, so no D1 rule tripped (writing the docstring is the fix the rule asks
  for, not an ignore). The `ALL` run then produced exactly: ruff's own warnings that D203/D211 and
  D212/D213 are incompatible (ruff drops D203 and D213 itself; ignoring them makes the choice
  explicit, no blank line before a class docstring and the summary on the first line) and that
  COM812 conflicts with the formatter, which owns trailing commas; CPY001 on every file (the
  license is the repository's `LICENSE`; a copyright header per file is noise every diff pays
  for); INP001 on the tests (below); and S101 on every assert in the tests (assert is how a pytest
  test states its expectation). Four ignores and two per-file ignores, each with its comment.
  Expected from experience and **not** tripped, so **not** added: ISC001 (ruff 0.17.4 no longer
  warns of it) and PLR2004 (the tests have no magic number). The rerun under the written list is
  clean with no warning.
- **`tests/` is not a package** (INP001 ignored for `tests/**`): pytest collects it from
  `testpaths` and nothing imports it, so an `__init__.py` would make it a package for no reader.
  The convention this rests on is one basename per test file across `tests/`, which mypy
  (`files = ["src", "tests"]`) refuses to break as a duplicate module; the README says so.
- **mypy: `strict = true`**, `files = ["src", "tests"]` so the tests are typed to the same bar as
  the package, `python_version = "3.12"` the floor, `warn_unreachable = true` (code the checker
  proves unreachable is a bug; strict does not turn it on), `implicit_reexport = false` (strict
  implies it; stated because the issue names it, so the package's surface is `__all__`). No
  `[[tool.mypy.overrides]]`: nothing untyped is imported; the comment says one goes there per
  package with its reason, never a global `ignore_missing_imports`. Test k shows a strict-only
  check applied: `no-any-return` on a function returning `json.loads(...)` as `int`, which ruff
  passes.
- **pytest: `testpaths = ["tests"]`**, `addopts = "-q --strict-markers --strict-config"` (`-q`
  because a person reads the gate's transcript; `--strict-markers` so an unregistered marker is a
  failure, not a typo that silently selects nothing; `--strict-config` so a key pytest does not know
  fails the run, as the gate standard asks of a rule-set config), and the `integration` marker
  registered with its meaning (needs a running instrument; not selected by the gate until a spec
  says so). Nothing else: `filterwarnings` and `xfail_strict` wait for a spec that needs them.
- **hypothesis has no section**: it reads no `pyproject.toml` settings; profiles are code, and the
  defaults serve two small properties. `.hypothesis/` was already in `.gitignore`.
- **`src/patchbay/__init__.py` exports `__version__`** read with `importlib.metadata.version`
  from the installed distribution, so `pyproject.toml` is the one place the version is written,
  and `__all__ = ["__version__"]`; nothing else. `py.typed` stays.
- **The two tests** in `tests/unit/test_version.py`: `__version__` equals `[project].version` read
  with `tomllib` from the repository's `pyproject.toml` (the path from the test file, so the test
  reads the tree it runs in); `__version__` fullmatches the release-segment pattern
  `\d+(\.\d+)*`; and two hypothesis properties of that pattern (owner's choice): every dotted
  triple of non-negative integers matches, and a segment that is not all digits does not, alone or
  after `1.0.`. The properties exercise hypothesis under `mypy --strict` and say something true
  about the check the plain test applies. `tests/conftest.py` holds a docstring and no fixture.
- **Six gate steps, in the issue's order**: `bash -n` as before; `uv run --locked ruff format
  --check .`; `uv run --locked ruff check .`; `uv run --locked mypy`; `uv run --locked pytest`;
  `scripts/sync-standards.sh --check` as before. Format before lint so a formatting failure is
  reported before a lint failure the formatter would have changed; lint before types because it is
  faster and its findings are cheaper; tests last among the tools because a type error usually
  explains a test failure. Step 2 first checks `uv` is on PATH and fails by name if not. Each step's
  `fail` reason names what the tool reports above it. The exit contract is unchanged: 1 at a failed
  step after `FAIL  step N/6: <reason>` on stderr, 2 on usage. The header names the pins' home, the
  rule set and what each step needs.
- **Six new negative tests**, h (a misformatted module: step 2 names it, `3/6` never printed), i (a
  formatted module with an unused import: step 3 reports F401), k (a function returning `Any` as
  `int`: step 4 reports `no-any-return`, strict's), l (a test asserting the wrong version: step 5
  reports the failure, `6/6` never printed), m (the rule set is `pyproject.toml`'s: `line-length`
  lowered to 40 makes the clean tree fail step 2, a changed value applied; `line-length = "wide"`
  is refused by ruff; a stray `[` is refused by uv) and n (`ruff==0.17.3` without re-locking: uv
  names the stale lockfile at step 2). `mk` now copies `pyproject.toml`, `uv.lock`,
  `.python-version`, `README.md` (the build backend reads it), `src/` and `tests/`; a copy that
  reaches step 2 syncs its own `.venv` from uv's cache, so the default set takes under a minute.
  The headers of b to f say step 6; j's prose names setup-uv among the `uses` steps the replay
  stands in for.
- **pre-commit** (owner): two `repo: local` hooks, `ruff check --fix` then `ruff format` (ruff's
  recommended order, since a fix can change formatting), each `entry: uv run --locked ruff ...`
  with `language: system` and `types_or: [python, pyi]`, so the hook runs the gate's ruff with the
  gate's rules and the version is pinned once, in `uv.lock`. `require_serial: true` because two
  `uv run` calls syncing the same `.venv` would race. `minimum_pre_commit_version: "4.7.0"`, the
  dev-group pin. Never mypy or pytest: the hook is for what a commit can fix in a second; the gate
  is the check. `pre-commit validate-config` and `pre-commit run --all-files` both pass; the git
  hook is not installed by the agent (`uv run pre-commit install` is the owner's, the README says
  how).
- **CI**: `astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3`, the tag
  resolved to that commit through the GitHub API on 2026-11-05 (the tag object points at the
  commit directly) and the latest release that day; `version: "0.13.7"`, the uv the gate was proven
  with locally and the lower bound of `[build-system] requires`; `working-directory: patchbay`,
  since the repository is checked out into a subdirectory; `enable-cache: true` with
  `cache-dependency-glob: uv.lock`, which setup-uv's `action.yml` at that commit resolves relative
  to the working directory (the first draft said `patchbay/uv.lock`, corrected after reading the
  action). The cache holds uv's download cache keyed on the lockfile: the same key resolves to the
  same packages, so it is not a moving part, and a changed lockfile misses it. Then `uv sync
  --locked` from `patchbay/`, so the environment is built as its own step before the gate runs,
  and the gate as before. This deviates from `verification-gate.md` "CI" ("caches nothing") and is
  proposed below; the issue asked for the cache. `actions/checkout` stays at v7.0.1, still the
  latest release.
- **`.python-version` stays 3.12.** A uv-managed CPython 3.12.16 was already present on this
  machine, so nothing was downloaded or installed outside the repository to run the gate; uv's
  cache and `.venv/` are the only writes. CI fetches the interpreter through setup-uv.
- **Docs**: `README.md` rewritten (layout, install, the six steps and `--locked`, pre-commit, the
  one-config-file rule and its exception); `CLAUDE.md` Specs (the six steps, CI's uv steps, the
  `[tool.*]` sections in the gate's own files); `shape-spec.md`'s gate task, Step 8, Step 9 and
  the `shape.md` template renumbered to steps 1–6 runnable and 7–9 judgment (a gate file; this is
  a gate spec); `tech-stack.md`'s runner line and introduction corrected.

## Context

- **Visuals:** None.
- **References:** `references.md`.
- **Product alignment:** `agent-os/product/tech-stack.md`: uv and `uv_build`, Python >= 3.12,
  ruff `ALL` with every disabled rule named, `mypy --strict` over package and tests, pytest and
  hypothesis, src layout, all implemented here; its `uvx` line corrected to `uv run --locked` with
  the lockfile as the pin. pydantic and typer wait for the spec that needs them. `mission.md`
  untouched.

## Standards Applied

**Core (always applied):**
- none yet (Step 5a)

**Feature-specific:**
- `base/process/verification-gate` — the gate's own spec: four steps added, each with its negative
  test and the config shown applied (m); the pins and the rule-set config, where this spec deviates
  and proposes; CI (one job, the runner the script assumes, every action pinned, the replay before
  any push, the hosted run recorded by the owner); the gate task text changed here.
- `base/process/standards-sync` — step 6 unchanged; the CI layout kept, uv added beside it.
- `base/process/ownership` — no commit, stage, push, PR, approval or merge by an agent; nothing
  installed outside the repository (uv was present; the interpreter was already uv-managed).
- `base/process/standards-index` — `index.yml` untouched; no project standard written here.
- `base/process/standards-retrospective` — governs the closing step; base changes proposed, not
  edited.

## Verification Gate

Spec is not complete until `scripts/gate.sh` passes — `bash -n` on every shell script under
`scripts/` as git lists them; `uv run --locked ruff format --check .`, `uv run --locked ruff check
.`, `uv run --locked mypy` and `uv run --locked pytest` under `pyproject.toml`'s `[tool.*]` rule
set and `uv.lock`'s pins; and `scripts/sync-standards.sh --check` against `../patchbay-standards`
at the commit in `agent-os/standards/base/.version` — and the three judgment steps are recorded,
in this order: Docs, Version, then the standards retrospective below.

**Results (2026-11-05):** `scripts/gate.sh` exit 0 on the tree, six steps, run as the last act
before hand-over on branch
`feature/2-toolchain-setup-pyprojecttoml-as-the-only-config-ruff-mypy-pytest-hypothesis-pre-commit-the-full-gate`;
`verification/gate-run.txt` holds the transcript with the date and branch on its first line. The
gate was run green after each of the first three stages (two steps after pyproject.toml and after
the code, six after the gate steps landed); the run recorded here, after pre-commit and CI, is the
one that covers all five. Every gate file changed in this spec, so every negative test ran after the last edit to any
of them, each run asserting its expected status: `verification/gate-negative-tests.txt` holds a to
n and u, 28 runs, 0 unexpected (a: step 1 names `scripts/broken.sh`; b to f: step 6 after steps
1–5 pass; g: step 1's file list; h: `src/patchbay/_broken.py` would be reformatted, `3/6` never
printed; i: F401 in `src/patchbay/_unused.py`; k: `no-any-return` in
`tests/unit/test_broken_types.py`; l: `assert '0.0.1' == '9.9.9'`, `6/6` never printed; m:
`line-length = 40` reformats `test_version.py`, `"wide"` is `invalid type: string ... expected
i64` from ruff, a stray `[` is a TOML parse error from uv; n: `The lockfile at uv.lock needs to be
updated, but --locked was provided`; u: usage exits 2, the clean copy passes all six).
`verification/ci-negative-test.txt` holds j, 3 runs, 0 unexpected: the pin step writes the sha in
`.version`; `uv sync --locked` and the gate pass from `working-directory: patchbay` on the clean
copy, and the job fails at step 6 (the gate) with exit 1 on the copy with `broken.sh`; setup-uv is
printed, not run. The hosted run on the pull request is the proof of the workflow itself
(setup-uv, the cache, ubuntu); the owner records its id and conclusion at the end of
`ci-negative-test.txt` after the push.

Revised after the review of PR 4 in `agent-os/specs/2026-11-05-2057-toolchain-revision-after-pr-4-review/`,
which corrects the `license-files` Decision above; the transcripts here are the first round's.

**Docs (step 7):** `README.md` read against the tree: the layout lists `tests/`,
`.pre-commit-config.yaml` and what `pyproject.toml` is; Install matches `uv sync` and the dev
group; the six steps match `scripts/gate.sh`'s banners and `--locked` behaviour; pre-commit
matches the two hooks; CI's description matches `gate.yml`. `CLAUDE.md` Specs names the six steps,
the `[tool.*]` sections as the rule set and CI's uv steps, and the gate's own files list carries
the `[tool.*]` sections; `## Ownership` unchanged. `pyproject.toml`'s header says which sections are
whose and which step reads the `[tool.*]` sections, read against `scripts/gate.sh`; every ignore
has its comment and each matches a finding of the recorded run. `scripts/gate.sh`'s header names
steps 1–6 and 7–9, the pins' home, `--locked`, the rule set and what each step needs, each read
against the code below. `scripts/gate-negative-tests.sh`'s header names fifteen cases, what `mk`
copies and the per-case sync; j's prose names three `uses` steps. `.github/workflows/gate.yml`'s
header says why uv returns, what the cache is keyed on, `uv sync --locked`, the pins and the
layout, read against the steps. `.pre-commit-config.yaml`'s header says what the file is and is
not. `.claude/commands/agent-os/shape-spec.md`: the gate task lists steps 1–9 as the script and
this file have them; Step 8, Step 9 and the template say six runnable steps and steps 7–9.
`agent-os/product/tech-stack.md` reads true: the runner line and the introduction. `CHANGELOG.md`
describes the shipped files. Standards that name these files: `verification-gate.md` "In a
consuming project" ("its `shape-spec.md` lists those steps in the gate task", "its gate workflow
runs the script and nothing else", "its `CLAUDE.md` names the script as the definition of done")
read true, with `uv sync --locked` as the install of the runner the script assumes; "Pinned" and
"CI" do not read true of this tree in two sentences, recorded as deviations and proposed below.
`standards-sync.md` "In a consuming project" reads true (layout, the pin step). `ownership.md`
reads true (nothing installed). `agent-os/standards/index.yml` unchanged.

**Version (step 8):** recorded under `[Unreleased]` in `CHANGELOG.md` as an Added entry for this
spec, naming each file, every pin, the six steps, the six negative tests, pre-commit and CI.
`pyproject.toml`'s version is set to `0.0.1` (the issue's number, the first deliberate one); it is
not a release bump, nothing is released, and `uv.lock` records it.

**Not done by the agent, by rule:** no file staged, committed or pushed; no pull request opened;
the pre-commit git hook not installed; the owner reads the diff at commit time.

## Standards Retrospective

Step 9, always last. Per `agent-os/standards/base/process/standards-retrospective.md`. Applied
2026-11-05 from the shipped diff against `0916b55` (`pyproject.toml`, `uv.lock`,
`src/patchbay/__init__.py`, `tests/`, `scripts/gate.sh`, `scripts/gate-negative-tests.sh`,
`.pre-commit-config.yaml`, `.github/workflows/gate.yml`, `README.md`, `CLAUDE.md`,
`CHANGELOG.md`, `.claude/commands/agent-os/shape-spec.md`, `agent-os/product/tech-stack.md` and
this spec folder). No base file and no line of the `base:` section is touched; this repository has
no project standard, so there is nothing to edit in place and `index.yml` is unchanged. The
toolchain, layout and typing standards this code establishes are base standards, written in
`patchbay-standards` (issue #4 there) from this tree, which is why the Step 5a tier stays empty
here rather than being filled with a local copy that the sync would then duplicate.

1. *A pattern no standard covers?* Four, all for the gate standard and all proposed below. Where a
   pin lives when the repository has a package manifest (the lockfile, run under `--locked`),
   verified by `pyproject.toml`, `scripts/gate.sh` steps 2–5 and test n. The rule-set config being
   the `[tool.*]` sections of a file whose other sections change in any spec, verified by
   `pyproject.toml`'s header, `CLAUDE.md`'s gate-files list and test m. A cache keyed on the
   lockfile in the gate's workflow, verified by `.github/workflows/gate.yml`. And what "install the
   runner the script already assumes" is for a Python package: setup-uv pinned plus
   `uv sync --locked`, verified by the workflow and test j. Also new, and not a standards matter:
   the method for the ignore list (run `ALL`, fix what the rule is right about, ignore what it is
   wrong about with a comment, add nothing from memory), recorded in `pyproject.toml`'s comment
   and under Decisions for the toolchain standard to take up.
2. *A standard wrong or stale?* `verification-gate.md` "Pinned" is written from a repository with
   no package manifest, as the owner said at shaping: "run through a runner that executes it
   without installing it into the project" cannot hold for a type checker or a test runner, which
   need the project installed. Not wrong there, stale for a second consumer; proposed below.
   `tech-stack.md`'s `uvx` line was the same assumption in a product doc, corrected in Docs.
3. *A deliberate deviation?* Two from the base gate standard as it reads, each a proposal below so
   the standard grows the condition rather than the deviation staying a one-off: pins in the
   lockfile, not the script; a cache in the workflow, keyed on the lockfile. One from the issue's
   own "only config" rule, recorded as a Decision and not a standards matter:
   `.pre-commit-config.yaml` exists because pre-commit cannot read hooks from `pyproject.toml`,
   and it configures no tool. The gate files changed in this spec, whose feature is the gate.
4. *A moved pointer?* The gate's step numbers: `shape-spec.md`'s gate task, Step 8, Step 9 and
   template, `CLAUDE.md`, `README.md` and the harness's case headers now say steps 1–6 and 7–9,
   each read against `scripts/gate.sh`. `tech-stack.md` pointed at `scripts/gate.sh` for the pins;
   it now points at `pyproject.toml`'s dev group. No standard pointed at a file this spec renamed.

### Standards retrospective (proposed, base)

- `base/process/verification-gate.md` — "Pinned": in the owner's words, "pins live in the script
  when the repository has no package manifest, otherwise in the lockfile the gate runs under
  `--locked`", each pin exact with its publish date beside it, and `--locked` so a pin edited
  without re-locking fails the step instead of rewriting the lockfile. Verified against
  `pyproject.toml`'s `[dependency-groups] dev`, `scripts/gate.sh` steps 2–5 and test n. The
  sibling, with no manifest, keeps its pins in the script. Proposed, not applied.
- `base/process/verification-gate.md` — "Pinned": the rule-set config may be the `[tool.*]`
  sections of the package manifest, in which case those sections are the gate file and the
  manifest's other sections change in any spec; the file's header says which sections are which.
  Verified against `pyproject.toml`'s header, `CLAUDE.md`'s gate-files list and test m (a changed
  value applied; a value the tool refuses; a file uv refuses). Proposed, not applied.
- `base/process/verification-gate.md` — "CI": "install the runner the script already assumes" is,
  for a package, the pinned setup-uv action and `uv sync --locked` from the project directory
  before the gate; and "caches nothing" admits a cache keyed on the lockfile, since the same key
  resolves to the same packages and a changed lockfile misses it. Verified against
  `.github/workflows/gate.yml` and test j (the replay runs the sync step; the `uses` steps stand
  in). Proposed, not applied.
- `base/process/verification-gate.md` — "Every step that can fail is proven to fail": a step that
  reads a lockfile is proven with a pin edited and the lockfile left (test n), beside the changed
  value, the unparsable value and the unparsable file for the rule set (test m). Verified against
  `scripts/gate-negative-tests.sh`. Proposed, not applied.

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The base standards under `agent-os/standards/base/` are pinned to the commit in `base/.version`;
a sync forward is recorded here by the sync's own commit, one entry naming the old commit and the
new as the sync's report gives them. The script writes no `CHANGELOG.md`: the person who syncs
writes the entry, in that commit
(`agent-os/standards/base/process/standards-sync.md`, "Pinned, not tracking").

## [Unreleased]

### Changed

- sync base standards: 11ceffdbd088bfb753dc54efa198dcb1ad6af0c9 ->
  e31f7dbfb474752339a43fe08a37ab26c7956f5c. Written by the spec after it
  (`agent-os/specs/2026-11-09-0802-gate-after-sync-and-event-utc-offset/`), since the sync's commit
  `4b1b3e2` (PR #14) merged without its entry.

- Ninth spec, `agent-os/specs/2026-11-09-0802-gate-after-sync-and-event-utc-offset/` (issues #12
  and #13): the gate's spec after the sync to `e31f7db`, and `Event.at`'s offset. Every departure
  from the issues' text is a Decision in the spec's `shape.md`. The version stays 0.0.1.
  - `scripts/gate.sh` takes the skeleton it shares with `patchbay-standards` at `e31f7db`: the root
    guard asks git `--is-inside-work-tree` as well as `--show-cdup`, so a copy under another
    repository's `.git/` or in a bare repository is refused by name; each listing goes to a file in
    a temporary directory with git's status checked, the empty record, the `ok=` flags and the
    dependence on `pipefail` gone; step 1 refuses every tracked file a committed `.gitignore`
    matches, naming each under one FAIL line. `verification/gate-sh-diff.txt` shows the two scripts
    differing only in step lists, pins, paths and the refusal's pathspec.
  - Step 5 refuses, before pytest walks, an ignored root `pytest.toml`, `.pytest.toml`, `pytest.ini`
    or `.pytest.ini`, each read in place of `pyproject.toml` (one holding `addopts` deselected a
    tracked failing test and the gate passed), and an ignored `test*.txt` under `tests/`, which
    pytest collects as a doctest (`verification/probes.txt`).
  - `scripts/gate-negative-tests.sh`: p's force-added file moves to step 1, and p shows the
    machine's own excludes do not count; g gains the refusal's listing, a git that refuses the
    listing of `scripts/`, a `mktemp` that makes nothing, a copy under `.git/` and one in a bare
    repository, and its upper-case run now passes step 6; q gains each configuration file and the
    doctest; r's shims are narrowed past step 1's refusal; `named` holds the entries under a FAIL
    line; `shim`, `upper` and `upper_run` are the sibling's. p's file count and q's scratch conftest,
    stale since the contracts spec, no longer rest on what the tree holds or on a name it now uses.
    98 runs, 0 unexpected; `verification/guard-mutations.txt`: each guard's mutation caught.
  - `.claude/commands/agent-os/shape-spec.md`: Step 5a lists `base/python/layout`, `typing`, `models`
    and `errors` beside `toolchain`; the gate task and its template, like `CLAUDE.md` and
    `README.md`, name step 1's refusal and step 5's new scope.
  - `src/patchbay/events.py`: `Event.at` also refuses a time whose offset at its own instant is not
    zero, so a `tzinfo` answering zero for no instant and +01:00 at a real one is refused
    (issue #13); `tests/unit/test_events.py` holds it.
  - `agent-os/product/tech-stack.md` cites `base/python/models.md` beside its pydantic line.

### Added

- Seventh spec, `agent-os/specs/2026-11-07-0806-contracts-models-events-errors-fake/` (issue #10):
  the first code in core, the contracts every adapter implements. Every departure from the
  issue's text is a Decision in the spec's `shape.md`, each the owner's; what pydantic, numpy and
  mypy do that the design rests on is its `verification/probes.txt`. The version stays 0.0.1.
  - `src/patchbay/errors.py`: `PatchbayError` and, under it, `ParameterNotFoundError`,
    `UnitMismatchError`, `ValueOutOfRangeError` (new, against the issue's list),
    `PatchRejectedError`, `RenderFailedError`, `SubscriberFailedError` and
    `PatchbayValidationError`; the issue's names take the `Error` suffix ruff's N818 asks. Each
    carries its fields as attributes and `args`, and builds its message from them.
  - `src/patchbay/models.py`: `ParameterId` and `PresetKey`, `Unit`, and the models on
    `PatchbayModel`: frozen (written on each class line, where mypy reads it), closed, finite and
    strict, and raising `PatchbayValidationError` from the constructor, the three
    `model_validate*` methods, assignment and deletion. `Quantity`, `Parameter` (with `check`,
    the rule a value meets), `Patch` (read-only mappings, sorted, opaque bytes as base64 in
    JSON), `Note`, `Pattern`, `RenderRequest` and `RenderResult` (a read-only float32
    `(channels, samples)` copy, `elapsed_seconds` in place of the issue's `duration_seconds`,
    `audio_seconds` computed).
  - `src/patchbay/events.py`: `Event` (stamped in UTC when built), `ParameterChanged`,
    `PatchLoaded`, `RenderCompleted` (carrying `elapsed_seconds` and `audio_seconds`), the
    generic `Subscriber` protocol and the synchronous `EventBus`, which runs every subscriber
    before raising `SubscriberFailedError`.
  - `src/patchbay/contracts.py`: the runtime-checkable `Instrument` protocol, positional-only, and
    `Subscriber` re-exported from `events.py`, where it moved from the issue's place.
  - `src/patchbay/testing/`: `FakeInstrument`, the reference implementation (eight parameters,
    a sine voice, a clip warning); `RecordingSubscriber`; `contract_tests.py`, the contract tests
    listed in `CONTRACT_TESTS`, failing with `ContractViolationError` and importing no pytest, in
    the names and number the revision after the review of PR 11 (the eighth spec, below) settled.
  - `src/patchbay/__init__.py` re-exports the contracts, models, events and errors beside
    `__version__`.
  - `tests/unit/`: a test module per source module, hypothesis properties of the `Quantity`,
    `Note` and `Pattern` validators and of a `Patch`'s JSON round trip with arbitrary opaque
    bytes; `tests/unit/testing/conftest.py`, the fixtures an adapter copies; every contract test
    run against FakeInstrument and, each, against a fake broken its way.
    `tests/unit/test_package.py` leaves submodules out of the names held to `__all__` and holds
    every exported name to the object its module defines.
  - `pyproject.toml`: `numpy>=2.5.4,<3` and `pydantic>=2.14.3,<3` in `[project] dependencies`;
    `uv.lock` gains them and their dependencies and changes nothing else
    (`verification/uv-lock-diff.txt`).
  - `README.md` (the layout, what `uv sync` installs) and `agent-os/product/tech-stack.md`
    (pydantic in use, numpy's line).

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

- Eighth spec, `agent-os/specs/2026-11-07-1432-contracts-revision-after-pr-11-review/`, the
  revision after the owner's review of PR 11: seventeen findings and three more of the same kind
  the probes found, each with its disposition in the spec's `plan.md`, each reproduced at
  `6f4e7a8` in its `verification/probes.txt`. The version stays 0.0.1.
  - `src/patchbay/models.py`: `PatchbayModel.from_json_data` validates data in JSON's form (as
    `json.loads`, YAML or TOML give it) by pydantic's JSON rules, and `model_validate` stays as
    strict as it was. The three `model_validate*` wrap pydantic's own methods rather than restate
    their signatures, so every keyword passes through and the three `noqa: PLR0913` go. The
    `PatchbayValidationError` promise is narrowed to a model's own entry points: a `TypeAdapter`,
    or a plain `BaseModel` holding a patchbay model, raises pydantic's error.
    `RenderRequest.samples` and `sample_at`, in exact arithmetic, are the one rule for where a
    render's samples fall.
    `RenderResult` refuses audio that is not finite, and its `audio_seconds` holds at any rate. A
    `Patch.values` key is never empty.
  - `src/patchbay/events.py`: `subscribe` returns a `Subscription` (`cancel()`, a context manager)
    and refuses a type that is not an event, or a subscriber that cannot be called, with the new
    `SubscriptionRejectedError`, where a bad subscription broke every publish after it. `Event.at`
    is refused unless its zone is UTC at every instant (Europe/London was accepted in January and
    refused in July) and is held as `datetime.UTC`. `ParameterChanged.id` is never empty.
  - `src/patchbay/errors.py`: `SubscriptionRejectedError`; `PatchbayValidationError.errors` is
    `.details`, since pydantic's `errors` is a method, and `SubscriberFailedError.errors` is
    `.exceptions`. `pydantic-core>=2.50.4,<3` joins `[project] dependencies`, since `errors.py`
    imports its `ErrorDetails`; `uv.lock` changes only patchbay-core's own entry
    (`verification/uv-lock-diff.txt`).
  - `src/patchbay/testing/`: `FakeInstrument` refuses a render past `MAX_SAMPLES` or
    `MAX_SAMPLE_RATE` with `RenderFailedError` before allocating anything, where valid extreme
    requests raised built-in exceptions or ran out of memory. It mixes into one float32 buffer,
    raises `PatchRejectedError` from the error that refused a patch, and reads its parameters
    through `parameters()`. The contract tests drop their `test_` prefix, so pytest never collects
    one an adapter imports by name, refuse a value one float past each bound, and gain
    `a_patch_refused_part_way_changes_nothing` and `an_impossible_render_raises_render_failed`:
    thirteen.
  - `tests/unit/`: a test for each change. A fake with bounds at 2**53 and at the largest float
    passes every contract test, and fails two with the old bound arithmetic put back
    (`verification/mutations.txt`).
  - `README.md`: the JSON-data entry point, subscriptions, the thirteen contract tests and
    pydantic-core.

- Sixth spec, `agent-os/specs/2026-11-07-0711-gate-revision-after-pr-9-review/`, the gate's spec
  for the revision after the owner's review of PR 9 (nine findings, each with its disposition in
  the spec's `plan.md`).
  - `scripts/gate.sh` steps 2-4 give ruff and mypy git's list of `.py` and `.pyi` files as
    explicit paths, each checked on the disk, so a tracked file `.gitignore` matches is read and
    git alone decides what `.git/info/exclude` hides, in a linked worktree too; `[tool.mypy]`
    loses `exclude_gitignore`. Step 5 lets pytest walk `tests/` only once no `.py` file there, and
    no `conftest.py` at the root, is one git ignores, since pytest loads an ignored conftest
    whatever `--ignore` says; the `--ignore` arguments are gone.
  - The skeleton is fixed ahead of `patchbay-standards`: step 1's root guard asks git whether this
    is the top (`git rev-parse --show-cdup`) instead of comparing paths, which a path typed in
    another case broke; `listed` lists a path in merge conflict once (`sort -zu`) and ends in an
    empty record only when git listed, so a listing git cannot make fails its step by name.
    `verification/gate-sh-diff.txt` names these hunks as the deviation until the sync; they go
    upstream with `sync-standards.sh`'s own root check.
  - `scripts/gate-negative-tests.sh`: `holds` and `times` assert a passing run's lines and a
    line's exact count, and the header no longer says `run` takes text on a passing run. g gains
    the copy entered in upper case, a script in a three-way merge conflict and a corrupt index,
    the gate at `6adf50e` shown on each; p and q are rewritten for the new steps 2-5, p with a
    linked worktree; r refuses the listing of steps 2, 4 and 5 in turn through a git on `PATH`
    that refuses one call. 68 runs, 0 unexpected; `verification/reason-assertion-mutations.txt`
    shows each new guard caught.
  - `README.md`, `CLAUDE.md` and the gate task in `shape-spec.md` describe the new steps 2-5.

- Fifth spec, `agent-os/specs/2026-11-06-1527-gate-skeleton-dev-pins-toolchain-tier/` (issues #5,
  #6 and #7), the gate's spec after the sync to `11ceffd`: what the base standards now pinned ask
  of this repository's own gate files, one spec since all three change them.
  - `scripts/gate.sh` takes the skeleton it shares with `patchbay-standards` at `11ceffd`: the
    header's exit and listing paragraphs; a `cd` into the repository root that fails with exit 2
    and a line on stderr; `listed`, one `git ls-files -z` call, and `present`, which names a
    symlink to nothing as one; step 1's root guard, so a copy nested in another repository's work
    tree is refused rather than listed against the outer one. Steps 2-5 read only the files git
    lists, in the form the revision after the review of PR 9 (the sixth spec, above) settled.
    `verification/gate-sh-diff.txt` shows the diff against the sibling's `gate.sh` holding only
    step lists, pins and paths; `verification/probes.txt` holds the probes of ruff, mypy, pytest
    and uv the changes rest on.
  - `scripts/gate-negative-tests.sh` takes the harness shape: every failing run names the lines its
    output must hold, the gate's `FAIL` line last, and is held to no later step banner; `only`
    holds step 6's drift report to exactly the lines b, c, e and f name; every setup step ends in
    `|| die`; the fixture's wording is corrected (a local clone holds the pin whichever ref reaches
    it); a kept transcript holds one run. New cases: g's tracked symlink to nothing and the copy
    nested in another repository, with the gate at `92cd215` shown on both; u's failed `cd`; p
    and q (steps 2-5 read what git lists, rewritten by the sixth spec).
    `verification/reason-assertion-mutations.txt`: three mutations, each caught only by the
    reason or by `only`.
  - `pyproject.toml`: the header and the dev group's comment name the pins of the tools the gate
    runs (ruff, mypy, pytest), with what `uv.lock` resolves for them, as gate files, and
    hypothesis and pre-commit as the package's (#6); the `[tool.uv]` comment says another uv
    refuses every command that reads the project's settings, not every command (probed); the
    `--strict-config` comment cites `toolchain.md` instead of a rule the gate standard does not
    have (#7). `CLAUDE.md`'s list of the gate's files follows.
  - `.claude/commands/agent-os/shape-spec.md`: Step 5a lists `base/python/toolchain`, included in
    every spec with its full text (#7); the gate task names step 1's root guard, steps 4-5's
    listing and the exit statuses, and gains the step that presents base proposals to the owner
    and files the approved ones upstream, with `Proposals sent upstream:` always recorded; the
    `shape.md` template follows; a base proposal's route is owner, issue, then pull request.
  - `agent-os/product/tech-stack.md` cites the toolchain standard; `README.md` and the header of
    `.pre-commit-config.yaml` run pre-commit through `uv run --locked`; `README.md` and
    `CLAUDE.md` name the exit statuses, the root guard, the listing, the gate's tool pins and the
    route a base proposal takes.

- Base standards synced from `b3fc2fe` to `11ceffd` (`ae58aac`, PR #8): `base/python/toolchain.md`
  is new; `verification-gate.md`, `standards-retrospective.md` and `standards-sync.md` are revised;
  the `base:` section of `agent-os/standards/index.yml` is regenerated. Recorded here by the spec
  after it, as the header says; the work the sync asked of this repository is the fifth spec above.

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

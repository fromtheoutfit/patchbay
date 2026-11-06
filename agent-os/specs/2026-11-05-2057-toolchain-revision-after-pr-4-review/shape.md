# Toolchain revision after the review of PR 4 — Shaping Notes

Shaped 2026-11-05 in plan mode with this repository's customized `/agent-os:shape-spec`, the Step
1–5 questions and three design choices asked and answered by the owner (recorded under Shaping
answers and Decisions).

## Core Architecture (Non-Negotiable)

None yet; see Step 5a of `.claude/commands/agent-os/shape-spec.md`. The toolchain, layout and
typing standards will fill this tier.

## Scope

The owner's review of PR 4 at commit `92c2ec2`, eleven findings, none of which makes the gate
fail: (1) the wheel ships without the LICENSE text, (2) the non-numeric hypothesis property is not
true of dotted numeric strings, (3) the release pattern accepts non-ASCII digits, (4) uv is pinned
only in CI, (5) a stale lockfile is reported as a formatting failure, (6) importing the package
uninstalled fails, (7) `patchbay.version` leaks as a public attribute, (8) a 160-character header
line in the harness, (9) the heading level CLAUDE.md names for the base proposals, (10)
`tests/conftest.py` holds only a docstring, (11) the test file's depth hard-coded in
`Path(__file__).parents[2]`. The review marks 1–4 worth fixing before merge and 5–11 cleanups.
The hosted `gate` run 42145584983 passed on that commit. This is the gate's own spec: a
`[tool.*]` section, `scripts/gate.sh`, the harness, the workflow and the gate task in
`shape-spec.md` change here, with the negative test for each changed step, on the same branch so
PR 4 carries the fix.

## Shaping answers

- **Step 1, scope:** all eleven findings, in a new spec folder on the same branch, as the revision
  after PR 3 did.
- **Step 2, visuals:** none.
- **Step 3, references:** the revision after PR 3 and this branch's files at `92c2ec2`; see
  `references.md`.
- **Step 4, product context:** aligned; `tech-stack.md` is read in Docs.
- **Step 5, standards:** all five base standards, the snapshot unchanged from the toolchain spec's.
- **Finding 5** (owner): step 2 opens with `uv sync --locked` and its own failure reason; every tool
  still runs as `uv run --locked <tool>`, the toolchain spec's owner Decision, so the docs that say
  so stay true. Chosen over the review's `--no-sync` option and over a seventh step.
- **Finding 6** (owner): no fallback; the import keeps failing uninstalled, and the docs say so.
- **Finding 10** (owner): `tests/conftest.py` is deleted.

## Decisions

- **The review on PR 4 is the scope.** Eleven findings, each with its disposition in `plan.md`'s
  table, all accepted; the shape of 5, 6 and 10 the owner's. Nothing outside them changes but this
  spec folder, `CHANGELOG.md`, the docs that name what changed, and one pointer line in the
  toolchain spec's `shape.md`.
- **`license-files = ["LICENSE"]`, explicit.** `uv_build` does not apply a default license glob: the
  wheel built from `92c2ec2` carries `License-Expression: MIT` in its METADATA and no license file
  in its `dist-info` (`verification/wheel-license.txt`), so the toolchain spec's Decision "No
  `license-files`: the default glob finds `LICENSE`" was wrong, and the MIT notice never reached
  anyone who installed the package. The pointer line in that spec says so.
- **uv is pinned once, in `[tool.uv] required-version = "==0.13.7"`.** Every `uv` command in this
  repository refuses another uv, so a local `--locked` run and CI's read `uv.lock` with the same
  uv. setup-uv reads the same key (`references.md`), so the workflow's `version:` line is removed
  and the version is written once. If the lookup ever failed, setup-uv would install the latest uv,
  which `required-version` would then refuse: the failure is loud, not a silent drift. `==` and not
  a range, as the dev group's pins are. A `[tool.*]` section, so it changes only in the gate's own
  spec, and test o proves a different uv fails step 2.
- **Step 2 opens with `uv sync --locked`, with its own failure reason** (owner): a stale lockfile,
  a `pyproject.toml` or `uv.lock` uv cannot read, and a uv that is not the required version each
  fail the step as the sync, before any tool runs; only then does `ruff format --check` run, with a
  reason that is now only about formatting. The sync is exact, `uv sync`'s default and what CI's
  sync does: a package in `.venv` the lock does not name is removed, so the gate checks the
  environment CI checks. The tools stay `uv run --locked` (owner): after the sync their lock
  checks are no-ops, and every document that says the gate runs `uv run --locked <tool>` stays
  true. CI's own `uv sync --locked` step stays, since issue #2 asked for it; the gate's sync is a
  no-op after it.
- **The import fails uninstalled, by design** (owner). src layout means the package is imported
  installed; from a bare `src/` on `sys.path` there is no distribution to read, and
  `importlib.metadata` raising `PackageNotFoundError` is truer than a made-up version. The module
  docstring and the README's layout line say so. No fallback, so no untested branch.
- **`import importlib.metadata as _metadata`.** `from importlib.metadata import version` bound
  `version` on the package; the review's first option, `import importlib.metadata`, would bind
  `importlib` instead. The aliased import binds one private name. A test now holds the surface:
  every name the package binds without a leading underscore is in `__all__`, which fails on
  `92c2ec2` naming `version`.
- **The release pattern is `[0-9]+(\.[0-9]+)*`.** `\d` matches any Unicode decimal digit
  (`"١.٠.٠"` matched); a PEP 440 release segment is ASCII digits. `[0-9]` rather than `re.ASCII`
  so the pattern reads as the grammar it states.
- **The non-numeric property generates one segment.** The strategy is text of at least one
  character with no `.` that is not all ASCII digits, so the property ("not a release segment,
  alone or after `1.0.`") holds by construction; the old filter, `not s.isdigit()`, admitted
  `"0.0"` and `"1.0.0.0"`, which the pattern matches. `@example("١٠")` (Arabic-Indic ten) runs on
  every pass, so a pattern that took `\d` again fails the test whatever hypothesis generates.
- **`pytestconfig.rootpath / "pyproject.toml"`.** pytest's rootdir is the directory of the
  `pyproject.toml` it read its own configuration from, so the test reads the file of the tree it
  runs in wherever the test file sits.
- **`tests/conftest.py` is deleted** (owner). pytest collects `tests/` without it, and a docstring
  saying "none yet" is one more thing to keep true; it returns with the first shared fixture. This
  departs from issue #2's file list ("tests/conftest.py (empty is fine)"), deliberately.
- **The proposals heading is `### Standards retrospective (proposed, base)`**, in CLAUDE.md and in
  `shape-spec.md`'s Step 5 and gate step 9, as the `shape.md` template and all three earlier specs
  have it. The base `standards-retrospective.md` says `##` in its prose and `###` in its own
  template; proposed below rather than edited.
- **A new spec folder on the same branch**, as after PR 3: the toolchain spec's record and
  transcripts stay as committed, with one line pointing here; this folder holds the current
  transcripts.

Found while implementing, beyond `plan.md`:

- **The harness copies `LICENSE` into each scratch case.** With `license-files = ["LICENSE"]`, a
  tree without the file no longer builds (`project.license-files glob LICENSE did not match any
  files`), so the first harness run after the change failed b, c, e, f, g, h to o and u at step 2's
  sync, two of them unexpectedly. `mk` now copies `LICENSE` beside `README.md`, both build inputs,
  and the harness header says so. The sync's failure reason was widened to name the build ("uv
  could not read them or build the package"), and the gate header and README with it, since a
  build failure is now reported there rather than at ruff.
- **`[tool.uv.build-backend]` stays a gate file.** It names the module the build installs, not a
  rule, but `CLAUDE.md`'s list of the gate's own files says "the `[tool.*]` sections", and loosening
  that list is a rule change this review did not ask for. `pyproject.toml`'s header now says what
  the section is, under the gate's sections, so the header reads true.
- **The Arabic-Indic example is written as escapes**, `"١٠"`, and the comment names
  U+0661: ruff's RUF001 and RUF003 flag the literal digits as confusable with `l` and `.`, and they
  are right that a reader cannot tell what the string holds.

Each fix checked against the reviewed code, before and after (2026-11-05, `uv run --locked
python`, the test functions imported and called directly; nothing in the tree changed for it):

- Finding 2: the old filter `not s.isdigit()` admits `"0.0"` and `"1.0.0.0"`, which the pattern
  matches; the new filter admits neither.
- Finding 3: `\d+(\.\d+)*` fullmatches `"١.٠.٠"` and `"١٠"`; `[0-9]+(\.[0-9]+)*` matches neither;
  `test_release_pattern_rejects_a_non_numeric_segment` fails with the `\d` pattern (the explicit
  example) and passes with `[0-9]`.
- Finding 7: on `92c2ec2` the package's public names were `['version']`; with `patchbay.version`
  bound, `test_public_names_are_in_all` fails; on the shipped module the public names are `[]` and
  it passes.
- Finding 1: `verification/wheel-license.txt`, the wheel from `92c2ec2` (no license file) and the
  wheel from this tree (`dist-info/licenses/LICENSE`, byte-identical to `LICENSE`,
  `License-File: LICENSE`). The synced editable install's METADATA carries `License-File: LICENSE`
  too, so `test_distribution_names_its_license_file` holds it at every gate run.
- Findings 4 and 5: tests o and n in `verification/gate-negative-tests.txt`.

## Context

- **Visuals:** None.
- **References:** `references.md`.
- **Product alignment:** `agent-os/product/tech-stack.md` (uv and `uv_build`, the lockfile as the
  pin, run through `uv run --locked`); `mission.md` untouched.

## Standards Applied

**Core (always applied):**
- none yet (Step 5a)

**Feature-specific:**
- `base/process/verification-gate` — the gate's own spec: step 2 changes and gains a failure
  reason, a `[tool.*]` section is added, each with its negative test (n, m and o rerun or added);
  CI (the runner the script assumes, now at the version the manifest pins; every action pinned;
  the replay before any push; the hosted run recorded).
- `base/process/standards-sync` — step 6 unchanged; the CI layout unchanged.
- `base/process/ownership` — no commit, stage, push, PR, approval or merge by an agent; nothing
  installed outside the repository (uv 0.13.7 was already on PATH).
- `base/process/standards-index` — `index.yml` untouched unless the retrospective writes a project
  standard.
- `base/process/standards-retrospective` — governs the closing step; base changes proposed, not
  edited; finding 9 touches this standard's own wording.

## Verification Gate

Spec is not complete until `scripts/gate.sh` passes — `bash -n` on every shell script under
`scripts/` as git lists them; `uv sync --locked`, then `uv run --locked ruff format --check .`,
`uv run --locked ruff check .`, `uv run --locked mypy` and `uv run --locked pytest` under
`pyproject.toml`'s `[tool.*]` rule set and `uv.lock`'s pins; and `scripts/sync-standards.sh
--check` against `../patchbay-standards` at the commit in `agent-os/standards/base/.version` —
and the three judgment steps are recorded, in this order: Docs, Version, then the standards
retrospective below.

**Results (2026-11-05):** `scripts/gate.sh` exit 0 on the tree, six steps, run as the last act
before hand-over on branch
`feature/2-toolchain-setup-pyprojecttoml-as-the-only-config-ruff-mypy-pytest-hypothesis-pre-commit-the-full-gate`;
`verification/gate-run.txt` holds the transcript with the date and branch on its first line. Gate
files changed in this spec (`pyproject.toml`'s `[tool.*]`, `scripts/gate.sh`, the harness, the
workflow, the gate task in `shape-spec.md`), so every negative test ran after the last edit to any
of them, each run asserting its expected status: `verification/gate-negative-tests.txt` holds a to
o and u, 30 runs, 0 unexpected. The cases this revision touches: h fails step 2 at ruff format
after `ok   the locked toolchain synced`, naming `src/patchbay/_broken.py`; m applies
`line-length = 40` and refuses `"wide"` at ruff format, and refuses the stray `[` at the sync; n
fails step 2 as the sync, `The lockfile at uv.lock needs to be updated, but --locked was
provided`, ruff never run; o fails step 2 as the sync, `Required uv version ==0.13.6 does not
match the running version 0.13.7`, `3/6` never printed. The rest behave as in the toolchain spec.
`verification/ci-negative-test.txt` holds j, 3 runs, 0 unexpected: the pin step writes the sha in
`.version`; setup-uv is printed with no `version` in its inputs; `uv sync --locked` and the gate
pass from `working-directory: patchbay` on the clean copy, and the job fails at step 6 (the gate)
with exit 1 on the copy with `broken.sh`. Hosted run 42145584983 (`success`, on `92c2ec2`, the
workflow before this revision) is recorded at its end; the revised workflow's hosted run, the
proof that setup-uv reads `required-version` on ubuntu, is read back by the owner after the push.
`verification/wheel-license.txt` holds finding 1's before and after. `uv run --locked pre-commit
run --all-files` passes (both hooks).

**Docs (step 7):** `README.md` read against the tree: the layout says the package is imported
installed and `tests/` has no `conftest.py` until a fixture is shared, that `[tool.uv]` pins uv
and the wheel carries `LICENSE`; Install says uv 0.13.7 is `[tool.uv] required-version`'s, refused
otherwise, and read by setup-uv; the six steps match `scripts/gate.sh`'s banners, step 2 naming
the sync; the paragraph after them matches step 2's two failure reasons and CI's setup-uv input.
`CLAUDE.md` Specs: step 2's sync, the uv pin and CI's setup-uv sentence read true against the
script and the workflow; the gate's own files list names `[tool.uv]`'s pin; the proposals heading
is `###`, as the `shape.md` template has it. `.claude/commands/agent-os/shape-spec.md`: Step 5 and
gate step 9 name `###`; the gate task's step 2 and its closing line, Step 8 and the template's
Verification Gate paragraph name the sync, each read against the script. `pyproject.toml`'s header
says which sections are whose and what `[tool.uv]` and `[tool.uv.build-backend]` are;
`license-files` and `[tool.uv]` carry their comments. `scripts/gate.sh`'s header names the uv pin,
the sync, its exactness and its failure reasons, read against step 2. The harness header names the
copied files (with `LICENSE`), the sync, sixteen cases and o; it has no line over 100 characters.
`.github/workflows/gate.yml`'s header says setup-uv reads `required-version` and why a failed
lookup is loud, read against the step (no `version`). `src/patchbay/__init__.py`'s docstring says
it is imported installed. `agent-os/product/tech-stack.md`'s uv line names `[tool.uv]
required-version`. `CHANGELOG.md` describes the shipped files. `.pre-commit-config.yaml` unchanged
and still true. The toolchain spec's `shape.md` carries the pointer line. Standards that name these
files: `verification-gate.md` "In a consuming project" reads true (the script's steps, the gate
task, the workflow running the script, `CLAUDE.md` naming it); "Pinned" and "CI" do not read true
of this tree in three sentences, two already proposed by the toolchain spec ("pinned in the
script", "caches nothing") and one new here: "the runner's own version is pinned through the
action's input", proposed below. `standards-sync.md` "In a consuming project" reads true (layout
and pin step unchanged). `standards-retrospective.md` line 73 names the `##` heading its own
template does not use, proposed below. `ownership.md` reads true (nothing installed).
`agent-os/standards/index.yml` unchanged.

**Version (step 8):** recorded under `[Unreleased]` in `CHANGELOG.md` as a Changed entry for this
spec naming each finding's fix, and the toolchain spec's Added bullets rewritten to the tree
(`license-files`, `[tool.uv] required-version`, `test_package.py`, no `conftest.py`, step 2's
sync, case o, setup-uv reading the pin). `pyproject.toml` stays at `0.0.1`: nothing is released.

**Not done by the agent, by rule:** no file committed or pushed; the pull request not edited and
the review not answered. One slip, corrected at once: the deletion of `tests/conftest.py` was made
with `git rm`, which staged it; it was unstaged with `git restore --staged`, so the deletion is in
the working tree only and nothing is staged. The owner reads the diff at commit time.

## Standards Retrospective

Step 9, always last. Per `agent-os/standards/base/process/standards-retrospective.md`. Applied
2026-11-05 from the shipped diff against `92c2ec2` (`pyproject.toml`, `src/patchbay/__init__.py`,
`tests/unit/test_version.py`, `tests/unit/test_package.py`, `tests/conftest.py` removed,
`scripts/gate.sh`, `scripts/gate-negative-tests.sh`, `.github/workflows/gate.yml`, `CLAUDE.md`,
`.claude/commands/agent-os/shape-spec.md`, `README.md`, `CHANGELOG.md`,
`agent-os/product/tech-stack.md`, the toolchain spec's `shape.md` and this spec folder). No base
file and no line of the `base:` section is touched; this repository has no project standard, so
there is nothing to edit in place and `index.yml` is unchanged.

1. *A pattern no standard covers?* Two for the gate standard, proposed below. The runner's own
   version pinned in the package manifest, where the runner enforces it on every command
   (`[tool.uv] required-version`) and the CI action reads it, so it is written once and a local run
   and CI use the same runner; verified by `pyproject.toml`, `.github/workflows/gate.yml` and test
   o. And the step that installs the locked toolchain fails as itself, with its own reason, before
   any tool runs; verified by `scripts/gate.sh` step 2 and tests n, m (the stray `[`) and o. For
   the toolchain standard (patchbay-standards issue #4), written there from this tree and not a
   proposal to an existing standard: `license-files` stated, since `uv_build` applies no default
   glob (`verification/wheel-license.txt`); a version pattern written with `[0-9]`, not `\d`; a
   test reading the repository's `pyproject.toml` through `pytestconfig.rootpath`, not a path
   counted up from the test file; a package-surface test (every public name is in `__all__`) and
   a metadata test (the installed distribution names its license file); a private alias for an
   import the package uses itself. Not a standards matter: the harness copies every file the
   package build reads, which is this harness's own concern.
2. *A standard wrong or stale?* Two, each proposed below. `standards-retrospective.md` names the
   proposals heading `##` in its prose and `###` in its own template, and every spec uses `###`;
   this repository's `CLAUDE.md` and `shape-spec.md` had copied the prose and are corrected here.
   `verification-gate.md` "CI": "the runner's own version is pinned through the action's input"
   is stale for a repository whose manifest pins the runner; here the input is gone and the pin is
   stronger, enforced locally too. Separately, the toolchain spec's own Decision on
   `license-files` was wrong, corrected through its pointer line; a spec record, not a standard.
3. *A deliberate deviation?* From `verification-gate.md` "CI" as it reads (the runner's version
   not passed through the action's input), proposed below so the standard grows the condition.
   From issue #2's file list (`tests/conftest.py` removed until a fixture is shared), recorded as a
   Decision and not a standards matter. The toolchain spec's two recorded deviations (pins in the
   lockfile; a cache keyed on it) stand, with their proposals. The gate files changed in this spec,
   whose feature is the gate.
4. *A moved pointer?* The proposals heading in `CLAUDE.md` and `shape-spec.md` now matches the
   template. Step 2's banner names the sync, and `CLAUDE.md`, `shape-spec.md`'s gate task, Step 8
   and template, and `README.md` say so, each read against `scripts/gate.sh`. `tests/conftest.py`
   is gone: `README.md` and `CHANGELOG.md` no longer name it; the toolchain spec's records name it
   as it was then, by rule. No standard pointed at a file this spec moved or removed.

### Standards retrospective (proposed, base)

- `base/process/standards-retrospective.md` — "Who owns which standard": the proposals heading is
  `### Standards retrospective (proposed, base)`, as the file's own "Recording the answer"
  template has it, not `##`. Verified against that template, this spec's `shape.md` and the
  three earlier specs' (all `###`), and this repository's `CLAUDE.md` and `shape-spec.md` as
  corrected here. Proposed, not applied.
- `base/process/verification-gate.md` — "CI" and "Pinned": the runner's own version may be pinned
  in the package manifest, where the runner refuses any other version on every command (for uv,
  `[tool.uv] required-version`), and the CI action reads it from there rather than taking it as an
  input, so the version is written once and the local runner is CI's; a failed lookup is then a
  loud failure, since the runner refuses itself. A negative test sets the pin to a version that is
  not running and shows the step fail by name. Verified against `pyproject.toml`'s `[tool.uv]`,
  `.github/workflows/gate.yml` (setup-uv with no `version`) and test o; the hosted run of the
  revised workflow is the owner's to record. This amends the toolchain spec's "install the runner"
  proposal: setup-uv pinned by commit, reading `required-version`, then `uv sync --locked`.
  Proposed, not applied.
- `base/process/verification-gate.md` — "Every step that can fail is proven to fail" or "One
  script": the step that installs the locked toolchain fails as itself, with its own reason,
  before any tool runs (a stale lockfile, an unreadable manifest or a package that will not build,
  the wrong runner), so a lockfile failure is never reported as the first tool's finding. Verified
  against `scripts/gate.sh` step 2 and tests n, m and o. Proposed, not applied.

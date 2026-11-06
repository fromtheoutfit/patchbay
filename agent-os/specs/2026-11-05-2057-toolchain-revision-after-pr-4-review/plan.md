# Revision after the review of PR 4: license, version pattern, uv pin, lock check, cleanups

## Context

PR 4 (branch `feature/2-toolchain-setup-…-the-full-gate`, commit `92c2ec2`) carries the toolchain
spec `agent-os/specs/2026-11-05-2018-toolchain-ruff-mypy-pytest-full-gate/`. The owner's review
comment on it lists 11 findings. None of them fails the gate. Findings 1–4 are marked "worth
fixing before merge" and 5–11 are cleanups. Hosted run 42145584983 passed on `92c2ec2`.

This revision addresses all 11 findings. It follows the PR 3 revision
(`agent-os/specs/2026-11-05-1759-gate-revision-after-pr-3-review/`):
- a new spec folder on the same branch, so PR 4 carries the fix
- the toolchain spec's record and transcripts stay as committed, and its `shape.md` gets one
  pointer line
- this is the gate's own spec, because `[tool.uv]`, `scripts/gate.sh`, the harness, the workflow
  and the gate task in `shape-spec.md` all change

Shaped 2026-11-05 in plan mode with the customized `/agent-os:shape-spec`.

**Owner's answers:**
- Scope: all 11 findings, in a new folder, with no visuals. The references are the PR 3 revision
  spec and this branch's files. All five base standards apply, with the snapshot unchanged.
- Finding 5: step 2 opens with `uv sync --locked`, which has its own failure reason. Every tool
  still runs as `uv run --locked <tool>`, as the toolchain spec's owner Decision says.
- Finding 6: the import keeps failing when the package is not installed, and the docs say so. No
  fallback.
- Finding 10: delete `tests/conftest.py`. This departs from issue #2's file list and is recorded
  as a Decision.

Base standards are read-only here: no file under `agent-os/standards/base/`, no `base:` entry, and
not `scripts/sync-standards.sh`.

## Dispositions (this table goes into the new spec's plan.md)

| # | Finding | Disposition |
|---|---|---|
| 1 | The wheel ships without LICENSE: `license = "MIT"` is set, `license-files` is not | Add `license-files = ["LICENSE"]` under `[project]`. Build the wheel before and after into the scratchpad. Record the dist-info listing and the `License-*` lines of METADATA in `verification/wheel-license.txt`. Add a test that the installed metadata says `License-File: LICENSE`, but only if the editable install carries it (check first). The toolchain spec's Decision "the default glob finds `LICENSE`" was wrong; the pointer line says so. |
| 2 | The non-numeric property is false: `"0.0"` gets through `not s.isdigit()` | The strategy generates only single segments: `"." not in s and not (s.isascii() and s.isdigit())`. The property then holds by construction. |
| 3 | `\d` matches non-ASCII digits | `_RELEASE = re.compile(r"[0-9]+(\.[0-9]+)*")`. `@example("١٠")` (Arabic-Indic) on the non-numeric property always runs that case, so a `\d` pattern fails it. |
| 4 | uv is pinned only in CI | Add `[tool.uv] required-version = "==0.13.7"`. Remove `version:` from setup-uv: with `working-directory: patchbay` it reads `required-version` from `patchbay/pyproject.toml` (checked in setup-uv's README and `action.yml` at the pinned commit). Every `uv` command here then refuses another uv. New negative test o. |
| 5 | A stale lockfile is reported as a formatting failure | Step 2 opens with `uv sync --locked \|\| fail 2/6 "<sync reason>"`. The reason covers a stale lock, an unreadable `pyproject.toml` or `uv.lock`, and the wrong uv. The tools stay `uv run --locked` (owner); after the sync their lock checks are no-ops. The sync is exact, as CI's is. Tests n, m and o show the sync's reason; test h shows the format reason. |
| 6 | `import patchbay` without installing raises `PackageNotFoundError` | No fallback (owner). The module docstring and README's layout line say the package is imported installed (`uv sync`). Without the distribution, `importlib.metadata` raises rather than the package inventing a version. |
| 7 | `patchbay.version` leaks as a public attribute | `import importlib.metadata as _metadata`, which binds one private name, and `_metadata.version(...)`. The review's literal `import importlib.metadata` would leak `importlib` instead. New test: every name in `vars(patchbay)` without a leading `_` is in `__all__`. |
| 8 | A 160-character line in the harness header | Re-wrap the paragraph under 100 characters. |
| 9 | Heading level: CLAUDE.md says `##`, while the template and all three specs use `###` | Local prose becomes `### Standards retrospective (proposed, base)`: `CLAUDE.md` (line 77) and `shape-spec.md` (lines 100 and 214). The base `standards-retrospective.md` has the same mismatch (line 73 `##`, its own template at line 126 `###`), so the retrospective proposes that fix as a base change. |
| 10 | `tests/conftest.py` holds only a docstring | Delete it (owner). It returns with the first shared fixture. This departs from issue #2's list ("empty is fine") and is recorded as a Decision. README's layout line is updated. |
| 11 | `Path(__file__).parents[2]` hard-codes the file's depth | `test_version_matches_pyproject(pytestconfig: pytest.Config)` reads `pytestconfig.rootpath / "pyproject.toml"`. pytest's rootdir is the directory of the `pyproject.toml` it read its config from. |

## Spec folder

`agent-os/specs/2026-11-05-2057-toolchain-revision-after-pr-4-review/` contains `plan.md`,
`shape.md`, `standards.md`, `references.md` and `verification/`.

## Task 1: Save spec documentation

- **`plan.md`:** this plan, with the table.
- **`shape.md`:**
  - `## Core Architecture (Non-Negotiable)`: "None yet; see Step 5a".
  - `## Scope`: the PR 4 review, its 11 findings and hosted run 42145584983.
  - `## Shaping answers`: Steps 1–5 and the three design answers above.
  - `## Decisions`, starting with "The review on PR 4 is the scope". Then:
    - `license-files` explicit
    - `required-version` pinned once and read by setup-uv
    - the sync opens step 2 and is exact
    - the tools stay `--locked`
    - no import fallback
    - the private `_metadata` alias and the public-surface test
    - `[0-9]` and the single-segment strategy
    - `rootpath`
    - `conftest.py` deleted, departing from issue #2
    - the heading level
    - a new folder on the same branch
  - `## Context`, `## Standards Applied` (all five).
  - `## Verification Gate` and `## Standards Retrospective`, filled in by the final task.
- **`standards.md`:** the toolchain spec's snapshot. The `.version` pin is unchanged. Check each
  section byte-for-byte against `agent-os/standards/base/process/*.md`, and retitle the header.
- **`references.md`:**
  - the PR 3 revision spec (the dispositions table, the pointer line, transcripts rerun, the
    hosted run recorded)
  - this branch's files at `92c2ec2`
  - setup-uv's `README.md` and `action.yml` at `68559e99…` ("If you do not specify a version …
    look for a required-version"; `working-directory` "controls where we look for
    `pyproject.toml`")
  - uv's `required-version` setting
- **Toolchain spec's `shape.md`:** one line after its Results paragraph: "Revised after the review
  of PR 4 in `agent-os/specs/2026-11-05-2057-toolchain-revision-after-pr-4-review/`, which
  corrects the `license-files` Decision above; the transcripts here are the first round's."

## Task 2: `pyproject.toml` and the wheel (findings 1, 4)

- Before editing, build the wheel into the scratchpad (`uv build --wheel --out-dir <scratch>`).
  Record `unzip -l` and METADATA's `License-*` lines in `verification/wheel-license.txt`, which
  shows the finding.
- `[project]`: add `license-files = ["LICENSE"]`.
- New `[tool.uv]` section above `[tool.uv.build-backend]`, containing `required-version =
  "==0.13.7"`. Its comment says:
  - this is the uv every `uv` command here runs under, and any other uv refuses
  - step 2's sync fails by name (test o)
  - setup-uv reads it, so the version is written once
  - it is bumped in the gate's own spec, with the gate rerun
- Header: name `[tool.uv]` (the uv the steps run under) beside the rule set. So that the touched
  header reads true, say that `[tool.uv.build-backend]` is the package's build configuration,
  not a rule.
- `uv lock --check` must be clean, since neither key is in the lock. If it is not, re-lock and
  record why.
- Rebuild the wheel and append the "after" listing: `…dist-info/licenses/LICENSE` and
  `License-File: LICENSE` are present.

## Task 3: `src/patchbay/__init__.py` (findings 6, 7)

```python
"""…(first paragraph as now)…

Import it installed (`uv sync`): the version is read from the distribution's metadata, and from a
bare src/ on sys.path there is no distribution to read, so importlib.metadata raises
PackageNotFoundError rather than the package inventing a version.
"""

import importlib.metadata as _metadata

__version__ = _metadata.version("patchbay-core")

__all__ = ["__version__"]
```

## Task 4: tests (findings 1, 2, 3, 7, 10, 11)

- **`tests/unit/test_version.py`:**
  - Use `_RELEASE = r"[0-9]+(\.[0-9]+)*"`. The comment says ASCII digits, since `\d` takes any
    Unicode decimal digit.
  - Drop `_PYPROJECT` and `Path`. `test_version_matches_pyproject(pytestconfig: pytest.Config)`
    reads `pytestconfig.rootpath / "pyproject.toml"`.
  - Non-numeric property: `@example("١٠")` plus
    `@given(st.text(min_size=1).filter(lambda s: "." not in s and not (s.isascii() and s.isdigit())))`.
    Its docstring says "one segment, not all ASCII digits".
- **New `tests/unit/test_package.py`** (a unique basename), docstring "The package's surface is
  `__all__`, and its distribution carries the license":
  - `test_public_names_are_in_all`: `{n for n in vars(patchbay) if not n.startswith("_")} <=
    set(patchbay.__all__)`. It fails on `92c2ec2` because of `version`.
  - `test_distribution_names_its_license_file`:
    `importlib.metadata.metadata("patchbay-core").get_all("License-File") == ["LICENSE"]` and
    `["License-Expression"] == "MIT"`. Add it only if the synced editable install's METADATA
    carries `License-File`, checked after Task 2. Otherwise the wheel transcript alone is the
    record, and `shape.md` says why.
- Delete `tests/conftest.py`.
- Check the findings directly with one-liners, recorded in `shape.md`:
  - the old filter admits `"0.0"` and the new one excludes it
  - `\d` matched `"١.٠.٠"` and `[0-9]` does not
  - the public-surface test fails with `from importlib.metadata import version`

## Task 5: `scripts/gate.sh` (findings 4, 5)

- **Step 2**, after the `command -v uv` check:
  - Run `uv sync --locked || fail 2/6 "uv could not sync the locked toolchain: uv.lock does not
    match pyproject.toml, uv could not read one of them, or this uv is not the version [tool.uv]
    requires (see above)"`.
  - Then `uv run --locked ruff format --check . || fail 2/6 "a file is not formatted as ruff format
    would write it, or ruff could not read its settings (see above)"`.
  - Banner: `2/6  uv sync --locked, then uv run --locked ruff format --check . (…)`.
- **Header**, steps 2–5 paragraph:
  - Step 2 first syncs. The sync is exact (a package the lock does not name is removed from
    `.venv`, as in CI). It fails by name on a stale lock, an unreadable file or the wrong uv.
  - The tools then run `uv run --locked`, a check the sync has already passed.
  - "Steps 2–5 need uv on PATH at the version `[tool.uv] required-version` pins".
- Steps 3–6, the exit contract and usage are unchanged.

## Task 6: `.github/workflows/gate.yml` (finding 4)

- Remove `version: "0.13.7"` from the setup-uv step. With `working-directory: patchbay` it reads
  `required-version` from `patchbay/pyproject.toml`.
- Keep the `uv sync --locked` step, which issue #2 asked for. The gate's own sync is then a no-op
  there.
- Header: setup-uv installs the uv that `pyproject.toml`'s `[tool.uv] required-version` pins, so
  the version is written once. If the lookup ever failed, the latest uv would refuse to run the
  gate, so the failure is loud.

## Task 7: `scripts/gate-negative-tests.sh` (findings 4, 5, 8)

- Re-wrap header lines 11–14 under 100 characters.
- **New case o:** in the copy, `required-version = "==0.13.7"` becomes `"==0.13.6"` (via `sed`,
  `|| die`). Step 2 must fail at the sync, with uv naming the required and running versions, and
  exit 1, with `3/6` never printed. Add o to the header, the usage list and the default set
  (`a … n o u`; `all` adds j).
- **Case n:** the header and `hdr` say step 2's sync names the stale lockfile with the sync's
  reason, and ruff never runs.
- **Case m:** the stray `[` is now refused by step 2's sync. The text says so; the expected status
  is unchanged.
- `mk` is unchanged: it copies `tests/`, and `conftest.py` is simply gone.

## Task 8: Docs (finding 9 and the ripple)

- **`CLAUDE.md`:**
  - Line 77: `## Standards retrospective (proposed, base)` becomes `###`.
  - The steps sentence: step 2 opens with `uv sync --locked`.
  - The CI sentence: setup-uv installs the uv `pyproject.toml` pins.
- **`.claude/commands/agent-os/shape-spec.md`:**
  - Lines 100 and 214: `##` becomes `###`.
  - Gate task step 2: "`uv sync --locked`, then `uv run --locked ruff format --check .`".
  - Line 201: the sync fails on a stale lock or the wrong uv.
  - Step 8 summary and the template's Verification Gate paragraph: add the sync.
- **`README.md`:**
  - Layout: `tests/` is `unit/` with no `conftest.py` until a shared fixture needs one, and the
    package is imported installed.
  - Install: uv 0.13.7 is enforced by `[tool.uv] required-version` (another uv refuses), and CI
    reads it from there.
  - Gate: step 2 syncs first, with its own failure.
- **`agent-os/product/tech-stack.md`:** read it. If it states uv's version or where it is pinned,
  correct that line. Otherwise leave it.
- `.pre-commit-config.yaml` is unchanged: its hooks stay `uv run --locked`, and they now also
  refuse another uv.

## Task 9: `CHANGELOG.md`

- Under `[Unreleased]` `### Changed`, add an entry for this spec: the PR 4 review, its 11
  findings, and each fix in a clause.
- Rewrite the third spec's Added bullets that no longer describe the tree:
  - `license-files`
  - `[tool.uv] required-version`
  - `conftest.py` gone
  - the new test file
  - step 2's sync
  - case o
  - setup-uv reading the pin

## Task 10 (FINAL): Verification gate

1. **Transcripts, after the last edit to any gate file.** The first line of each gives the date
   and branch.
   - `scripts/gate-negative-tests.sh` > `verification/gate-negative-tests.txt` (a–o and u, 0
     unexpected).
   - `scripts/gate-negative-tests.sh j` > `verification/ci-negative-test.txt`. Then append hosted
     run 42145584983 (`success`, on `92c2ec2`, the previous workflow), with a note that the owner
     reads the revised workflow's run back after the push.
2. **`verification/wheel-license.txt`**, before and after (Task 2).
3. **The gate.** `scripts/gate.sh` on the tree, as the last runnable act, > `verification/gate-run.txt`,
   exit 0 with six banners.
4. **Docs (step 7):** read true against the tree and record what was read:
   - README, CLAUDE.md and `shape-spec.md`
   - the headers of `pyproject.toml`, `gate.sh`, the harness, the workflow and `__init__.py`
   - `tech-stack.md`, the pointer line, and the `verification-gate.md` / `standards-sync.md`
     sections that name these files
5. **Version (step 8):** the Changed entry, with `0.0.1` unchanged (nothing is released).
6. **Standards retrospective (step 9):** the four questions, asked of the diff against
   `92c2ec2`. Expected base proposals, each verified against shipped code:
   - `standards-retrospective.md` line 73: `##` becomes `###`, matching its own template (finding 9).
   - `verification-gate.md` "Pinned": the runner's own version is pinned in the manifest
     (`[tool.uv] required-version`) and CI's installer reads it from there, written once. This
     amends the toolchain spec's "install the runner" proposal. Verified by `gate.yml` and test o.
   - `verification-gate.md` "Every step that can fail…": the lockfile check is its own failure
     reason, before any tool runs. Verified by `gate.sh` step 2 and tests n and o.
   - The test-tree patterns (`pytestconfig.rootpath`, `[0-9]` for a version pattern, the
     public-surface test) are recorded for the toolchain standard (patchbay-standards #4), not
     edited here.
   - No project standard exists, so `index.yml` is unchanged, unless the retrospective finds
     otherwise.
   - Retrospective edits are listed separately from the feature's.
7. **Stop** and print `git status --short`. No stage, commit, push or PR edit by the agent.

## Files

- **New:** the spec folder and `tests/unit/test_package.py`.
- **Changed:**
  - `pyproject.toml`, `src/patchbay/__init__.py` and `tests/unit/test_version.py`
  - `scripts/gate.sh`, `scripts/gate-negative-tests.sh` and `.github/workflows/gate.yml`
  - `CLAUDE.md`, `.claude/commands/agent-os/shape-spec.md`, `README.md` and `CHANGELOG.md`
  - possibly `agent-os/product/tech-stack.md`
  - the toolchain spec's `shape.md` (one line)
- **Deleted:** `tests/conftest.py`.
- **Untouched:** `agent-os/standards/`, `scripts/sync-standards.sh`, `uv.lock` (expected) and
  `.pre-commit-config.yaml`.

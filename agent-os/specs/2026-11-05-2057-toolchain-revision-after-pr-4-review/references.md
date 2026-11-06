# References for the toolchain revision after the review of PR 4

## Similar Implementations

### The revision after the review of PR 3

- **Location:** `agent-os/specs/2026-11-05-1759-gate-revision-after-pr-3-review/`
- **Relevance:** the record a review revision leaves in this repository: a new spec folder on the
  same branch, a dispositions table in `plan.md` (one row per finding), the first spec's
  `shape.md` given one pointer line and its transcripts left as committed, every negative test
  rerun after the last gate-file edit, and the hosted run of the reviewed commit recorded at the
  end of `ci-negative-test.txt`.
- **Key patterns:** borrowed whole: the table's three columns (#, finding, disposition), "Owner:"
  marking the owner's choices, a `### Changed` entry in `CHANGELOG.md` naming each fix, and the
  first spec's Added bullets rewritten where they no longer describe the tree.

### This branch's files as committed at `92c2ec2`

- **Location:** `pyproject.toml`, `src/patchbay/__init__.py`, `tests/unit/test_version.py`,
  `tests/conftest.py`, `scripts/gate.sh`, `scripts/gate-negative-tests.sh`,
  `.github/workflows/gate.yml`, `CLAUDE.md`, `.claude/commands/agent-os/shape-spec.md`
- **Relevance:** the files the review was made against; each finding names a line in them.
- **Key patterns:** kept: the six steps and their exit contract, `uv run --locked <tool>` for
  every tool (the toolchain spec's owner Decision), the harness's `mk`/`run`/`hdr`/`note` and its
  case-per-letter layout (test n is the shape of the new test o: one edit to the copy's
  `pyproject.toml` with `sed ... || die`, then the gate expected to fail at step 2).

### setup-uv at the pinned commit

- **Location:** `astral-sh/setup-uv` at `68559e99cc807c1eb7e9238fd43a15bba460eec2` (v10.3.3),
  `README.md` and `action.yml`, read through the GitHub API on 2026-11-05.
- **Relevance:** finding 4's single pin. `action.yml`: `version` "Defaults to the version in
  pyproject.toml or `latest`"; `working-directory` is "The directory to execute all commands in and
  look for files such as pyproject.toml". `README.md`: "If you do not specify a version, this
  action will look for a required-version in a `uv.toml` or `pyproject.toml` file", and under
  Working directory, it "controls where we look for `pyproject.toml`, `uv.toml` and
  `.python-version` files which are used to determine the version of uv and python to install".
- **Key patterns:** with `working-directory: patchbay` and no `version`, the action reads
  `[tool.uv] required-version` from `patchbay/pyproject.toml`, so the version is written once.

### uv's `required-version` setting

- **Location:** `[tool.uv] required-version` (uv's settings reference).
- **Relevance:** a version specifier the running uv must satisfy; any other uv refuses to run a
  command in the project. This is what makes the local uv the CI uv.

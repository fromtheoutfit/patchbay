# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The base standards under `agent-os/standards/base/` are pinned to the commit in `base/.version`;
a sync forward is recorded here as its own entry.

## [Unreleased]

### Added

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
  - `scripts/gate.sh`: two runnable steps, `bash -n` on every file under `scripts/` and
    `scripts/sync-standards.sh --check` against `../patchbay-standards` at the pinned commit; stops
    at the first failure naming the step on stderr, exit 1; exit 2 on usage; no tool pin yet, the
    place for them marked for the toolchain spec.
  - `.github/workflows/gate.yml`: one job on every pull request and every push to `main`, which
    checks this repository out into `patchbay/` and `fromtheoutfit/patchbay-standards` beside it
    at `main` with full history, installs uv 0.13.7 and runs `scripts/gate.sh` from `patchbay/`.
    `actions/checkout` v7.0.1 and `astral-sh/setup-uv` v10.3.3 pinned by commit, `ubuntu-24.04`,
    a ten-minute timeout, no persisted credential, no cache.
  - `scripts/gate-negative-tests.sh`: a (an unparsable script), b (a one-byte edit under
    `agent-os/standards/base/`), c (a hand-edited `base:` entry), d (the sibling checkout
    missing), u (usage, and the clean copy passing) and j (the CI replay of the workflow's run
    steps), each on a scratch copy beside a scratch clone of `patchbay-standards`. Transcripts in
    the spec's `verification/`.
  - `README.md`: what patchbay is and is not, the names, the layout, the gate, the sync.
  - `agent-os/product/mission.md` and `tech-stack.md`: what core is and is not, and the
    toolchain decisions the next spec implements.
  - This file.

The scaffold predates the first spec: the `patchbay-core` package (`src/patchbay/`, Python 3.12,
`uv_build`, the lockfile), the base standards synced in at `b3fc2fe` with
`scripts/sync-standards.sh` and the `base:` section of `agent-os/standards/index.yml`, and the
stock Agent OS commands.

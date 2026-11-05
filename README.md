# patchbay

Headless control of software instruments from Python: the contracts, host and CLI that
`patchbay-<instrument>` adapters plug into.

This is an experiment, not a product. The distribution name is `patchbay-core` and the import
name is `patchbay`. Nothing synth-specific lives here; core grows only when a second adapter needs
the same thing (`agent-os/product/mission.md`).

## Layout

- `src/patchbay/`: the package, src layout, typed (`py.typed`). Empty until the toolchain spec.
- `scripts/`: `gate.sh` (the verification gate), `gate-negative-tests.sh` (the tests that prove
  each gate step can fail, not run by the gate) and `sync-standards.sh` (installed and replaced by
  the standards sync, never hand-edited).
- `agent-os/product/`: `mission.md` and `tech-stack.md`, the decisions the next specs implement.
- `agent-os/standards/`: `base/`, the base standards synced from `patchbay-standards` and pinned
  to the commit in `base/.version`, read-only here; `index.yml`, whose `base:` section is the
  sync's and whose other sections are this repository's own.
- `agent-os/specs/`: one folder per spec, with its plan, shaping notes, the standards as they
  read when it was shaped, and `verification/` holding the gate transcripts.
- `.claude/commands/agent-os/`: the Agent OS commands; `shape-spec.md` is customized for this
  repository's gate, the rest are stock.
- `.github/workflows/gate.yml`: CI, which runs the gate and nothing else.
- `CLAUDE.md`: the rules for an agent working here, ownership first.

## The gate

```sh
scripts/gate.sh
```

Two runnable steps, in order, stopping at the first failure (exit 1; exit 2 on usage):

1. `bash -n` on every file under `scripts/`.
2. `scripts/sync-standards.sh --check`: `agent-os/standards/base/`, the `base:` section of
   `agent-os/standards/index.yml` and the sync script itself are byte-identical to
   `patchbay-standards` at the pinned commit.

Step 2 reads the sibling checkout at `../patchbay-standards`, so clone `patchbay-standards` beside
this repository first; CI checks it out there. The toolchain spec adds ruff, mypy and pytest as
further steps, pinned in the script. Three judgment steps follow the script and are recorded in
each spec's `shape.md`: Docs, Version and the standards retrospective. The rule is
`agent-os/standards/base/process/verification-gate.md`.

`scripts/gate-negative-tests.sh` runs each failure case on a scratch copy (`all` adds the CI
replay); its transcripts live in the spec that last changed a gate file.

## Syncing the standards

```sh
scripts/sync-standards.sh                 # move the pin to patchbay-standards' origin/main
scripts/sync-standards.sh --check         # the drift check, as the gate runs it
scripts/sync-standards.sh --index-only    # regenerate the base: section of index.yml alone
```

The pin is the commit in `agent-os/standards/base/.version`. A sync forward is its own change
set, titled `chore: sync base standards to <sha>`. No file under `base/` and no `base:` entry is
edited here: a change to a base standard is a pull request to `patchbay-standards`, proposed in a
spec's retrospective. The rule is `agent-os/standards/base/process/standards-sync.md`.

## Specs

Work is shaped with `/agent-os:shape-spec` in plan mode and ends with the gate. `CLAUDE.md`
holds the rules an agent follows here, `## Ownership` first: a person owns every commit, pull
request and merge.

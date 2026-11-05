# References for the bootstrap spec (issue #1)

Everything studied lives in the sibling checkout `../patchbay-standards`, at its working tree on
2026-11-05 (branch `feature/8-...`, whose files are the ones merged as `b3fc2fe`, the commit this
repository pins). It is the reference for structure; nothing is copied without being rebuilt for
this repository's gate, except the sections the issue names as verbatim.

## Similar Implementations

### The customized shape-spec command

- **Location:** `../patchbay-standards/.claude/commands/agent-os/shape-spec.md`
- **Relevance:** the issue says to copy its structure, not its gate list.
- **Key patterns:** the two-kinds-of-standards paragraph in Step 5; the empty Step 5a tier; the
  "what you read here is a snapshot" paragraph; the always-included final gate task with the
  runnable steps first and Docs, Version, retrospective after; the `shape.md` template with
  Core Architecture, Verification Gate (Results, Docs, Version) and Standards Retrospective with
  its `(proposed, base)` subsection; the Tips. The gate list is this repository's own.

### CLAUDE.md

- **Location:** `../patchbay-standards/CLAUDE.md`
- **Relevance:** the issue says Git, No AI attribution and Ownership are copied verbatim, Specs
  adapted.
- **Key patterns:** Ownership directly under Git, as `base/process/ownership.md` requires; the
  Specs section names the gate script as the definition of done and the judgment steps in order.

### scripts/gate.sh

- **Location:** `../patchbay-standards/scripts/gate.sh`
- **Relevance:** the shape every gate takes per `verification-gate.md`.
- **Key patterns:** header naming the judgment steps and CI; `set -euo pipefail`; `cd` to the
  repository root; the `step` banner `== N/M  <what>`; `ok   <what>` per step; the pin as one
  named variable with its publish date; the closing line naming the steps that follow. Not
  borrowed: its exit status is the tool's; here a failed step is exit 1 and usage exit 2.

### scripts/gate-negative-tests.sh

- **Location:** `../patchbay-standards/scripts/gate-negative-tests.sh`
- **Relevance:** the harness shape for negative tests on a scratch copy.
- **Key patterns:** `set -uo pipefail`; `NEG=$(mktemp -d)` with a trap; `mk` (copy, `git init`,
  `git add -A`), `run` (masks the scratch path, prints `exit=N`), `hdr`, `note`; test letters as
  arguments, `all` adds j; test j's CI replay reading the workflow with pyyaml through `uv run`
  and executing each `run` step under `bash --noprofile --norc -eo pipefail`. Its cases are not
  copied: they test `check-index.sh`, pymarkdown and the sync script, none of which is a step
  here.

### .github/workflows/gate.yml

- **Location:** `../patchbay-standards/.github/workflows/gate.yml`
- **Relevance:** the pins and the job shape.
- **Key patterns:** `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1`,
  `astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2 # v10.3.3`, uv `0.13.7`,
  `ubuntu-24.04`, `timeout-minutes: 10`, `persist-credentials: false`, `enable-cache: false`,
  `permissions: contents: read`. Here the job adds the second checkout of `patchbay-standards`
  beside the project and runs the gate with `working-directory`.

### CHANGELOG.md

- **Location:** `../patchbay-standards/CHANGELOG.md`
- **Relevance:** Keep a Changelog 1.1.0 shape, one entry per spec naming its issue and folder.

### The gate spec and the sync spec

- **Location:** `../patchbay-standards/agent-os/specs/2026-11-05-1000-gate-spec-ci-docs-version/`
  and `../patchbay-standards/agent-os/specs/2026-11-05-1441-sync-script-and-standards-sync/`
- **Relevance:** the record a spec leaves: `shape.md` with Decisions whose first entry cites the
  issue, Shaping answers, Verification Gate with Results, Docs and Version, the retrospective's
  four questions answered against the diff; `verification/gate-run.txt` with the date and branch
  on line 1, `gate-negative-tests.txt` and `ci-negative-test.txt`.

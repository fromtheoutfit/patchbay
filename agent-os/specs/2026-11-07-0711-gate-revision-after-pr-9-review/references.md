# References for the gate revision after the review of PR 9

## Similar Implementations

### The owner's review of PR 9

- **Location:** the comment of 2026-11-06 on fromtheoutfit/patchbay#9, made at `6adf50e`.
- **Relevance:** the scope. Nine findings, most severe first; 1, 2 and 5 reproduced in scratch
  repositories, 3 read from mypy's source, the rest from the diff.
- **Key patterns:** each finding names a line at `6adf50e`; `plan.md`'s dispositions table answers
  each by number.

### The revision after the review of PR 4

- **Location:** `agent-os/specs/2026-11-05-2057-toolchain-revision-after-pr-4-review/`
- **Relevance:** how this repository records a review revision: a new spec folder on the same
  branch, a dispositions table in `plan.md`, one pointer line in the reviewed spec's `shape.md`,
  every negative test rerun after the last gate-file edit, the CHANGELOG bullets of the reviewed
  spec corrected where they no longer describe the tree.
- **Key patterns:** borrowed whole.

### patchbay-standards' `scripts/gate.sh` and harness at `11ceffd`

- **Location:** `git -C ../patchbay-standards show 11ceffd:scripts/gate.sh` and
  `11ceffd:scripts/gate-negative-tests.sh`.
- **Relevance:** the skeleton findings 2, 5 and 6 are bugs in. This revision fixes them here
  first, so `verification/gate-sh-diff.txt` shows the skeleton hunks as a deviation until the
  sync, and the fixes go upstream through fromtheoutfit/patchbay-standards#20. Its
  `sync-standards.sh:97` has finding 2's comparison too.
- **Key patterns:** the harness's `old_file`, run here on the gate at `6adf50e`, the head the
  review was made against, to show each bug as it was.

### The first spec's verification

- **Location:** `agent-os/specs/2026-11-06-1527-gate-skeleton-dev-pins-toolchain-tier/verification/`
- **Relevance:** the baseline: its `probes.txt` (ruff, mypy and pytest reading `.gitignore`), its
  harness transcript (53 runs) and its `gate-sh-diff.txt`, all rerun or superseded here.
- **Key patterns:** the probe layout (an export of git's list, git-inited, `.venv` synced, each
  setup shown before its result), kept.

# References for the gate revision after the review of PR 15

## Similar Implementations

### The gate and harness at 912987a

- **Location:** `scripts/gate.sh`, `scripts/gate-negative-tests.sh` (`git show 912987a:<path>`)
- **Relevance:** what the review read and reproduced against.
- **Key patterns:** the harness's cases and `old_file`, which shows the gate at `912987a` where it
  had each bug.

### The sibling's gate at e31f7db

- **Location:** `../patchbay-standards/scripts/gate.sh`
- **Relevance:** the skeleton `verification/gate-sh-diff.txt` is held against.

### The review of PR 15

- **Location:** the comment on fromtheoutfit/patchbay#15 at `912987a`, 13 findings
- **Relevance:** the scope, and the reproductions `verification/probes.txt` repeats.

### This repository's gate spec after the review of PR 9

- **Location:** `agent-os/specs/2026-11-07-0711-gate-revision-after-pr-9-review/`
- **Relevance:** the shape of a revision after a review, and the precedent for naming a hunk ahead of
  `patchbay-standards` as a deviation in `gate-sh-diff.txt`.

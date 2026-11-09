# References for the gate spec after the sync to e31f7db

## Similar Implementations

### The sibling's gate at e31f7db

- **Location:** `../patchbay-standards/scripts/gate.sh`
- **Relevance:** the shared skeleton this repository takes.
- **Key patterns:** the root guard's two questions of git; `git_list`, `listed` and `fail_list`;
  step 1's temporary directory; the refusal of a tracked file a `.gitignore` ignores.

### The sibling's harness at e31f7db

- **Location:** `../patchbay-standards/scripts/gate-negative-tests.sh`
- **Relevance:** the cases this repository's g, p and r follow.
- **Key patterns:** tests w and y; the helpers `shim`, `upper`, `upper_run`, and `only`, whose form
  this repository's `named` takes.

### The sibling's revision after the review of PR 23

- **Location:** `../patchbay-standards/agent-os/specs/2026-11-07-1518-revision-after-pr-23-review/verification/`
- **Relevance:** `gate-sh-diff.txt` names the hunks this repository takes and what may differ;
  `guard-mutations.txt` is the shape of this spec's mutation record.

### The sibling's revision after the review of PR 25

- **Location:** `../patchbay-standards/agent-os/specs/2026-11-07-2041-revision-after-pr-25-review/verification/probes.txt`
- **Relevance:** probe r, `utc_zone.py`, shows the case #13 closes; this spec reruns it at the pins.

### This repository's gate spec after the review of PR 9

- **Location:** `agent-os/specs/2026-11-07-0711-gate-revision-after-pr-9-review/`
- **Relevance:** how a gate spec here records its Decisions, its transcripts and its mutations.

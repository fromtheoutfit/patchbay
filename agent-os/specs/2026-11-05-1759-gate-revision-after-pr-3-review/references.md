# References for the gate revision after the review of PR 3

## Similar Implementations

### The sibling's revision record after the review of PR 9

- **Location:** `../patchbay-standards/agent-os/specs/2026-11-05-1441-sync-script-and-standards-sync/`
  (`plan.md` "Revision after the review of PR 9", `shape.md` "Revision after review")
- **Relevance:** the record a review revision leaves: a dispositions table, one row per finding,
  and the decisions that extend or reverse the first round's.
- **Key patterns:** the table's three columns (#, finding, disposition); "Owner:" marking the
  owner's choices; every transcript rerun after the revision and the hosted run recorded by id.

### The sibling's harness and its CI replay

- **Location:** `../patchbay-standards/scripts/gate-negative-tests.sh`
- **Relevance:** `mk`/`run`/`hdr`/`note` and test j are the shape this harness keeps.
- **Key patterns:** borrowed as before. Not borrowed, and proposed back: its scratch directory
  line `NEG=$(cd "$(mktemp -d)" && pwd -P)` has the hazard finding 1 names, and its `run` asserts
  no exit status.

### This repository's gate files as committed at `6c91362`

- **Location:** `scripts/gate.sh`, `scripts/gate-negative-tests.sh`, `.github/workflows/gate.yml`
- **Relevance:** the files the review was made against; each finding names a line in them.
- **Key patterns:** the exit contract, the step banners and the harness layout stay; the file
  list, the scratch guard, the assertions, the checkout ref and the setup-uv step change.

### The sync script's file list

- **Location:** `scripts/sync-standards.sh`, `project_files`
- **Relevance:** step 1's new list is the same rule: tracked plus untracked-not-ignored, on disk,
  `git ls-files -z` with `core.quotePath=false`, so an ignored stray is never seen and a new
  unstaged script is.

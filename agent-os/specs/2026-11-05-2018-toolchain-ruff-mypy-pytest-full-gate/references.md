# References for the toolchain spec (issue #2)

## Similar Implementations

### This repository's gate script

- **Location:** `scripts/gate.sh` (as committed at `0916b55`)
- **Relevance:** the step shape the four new steps follow.
- **Key patterns:** `step "N/M  <what>"` banner, `fail N/M "<reason>"` to stderr then exit 1,
  usage exit 2, `cd "$(dirname "$0")/.."`, the closing line naming the judgment steps, the header
  that names what each step needs and where the pins live.

### This repository's negative-test harness

- **Location:** `scripts/gate-negative-tests.sh` (as committed at `0916b55`)
- **Relevance:** the fixture shape for a test on a scratch copy.
- **Key patterns:** `mk <case>` copies the gate's inputs into `<case>/patchbay`, git-inits and adds
  them, symlinks the scratch clone of `patchbay-standards` beside it; `run <case> <expected> <cmd>`
  prints the output with the scratch path masked and asserts the exit status; `hdr`/`note`; `die`
  for setup failures; the scratch-directory guard; `broken <case>`; test j's workflow replay.

### This repository's gate workflow

- **Location:** `.github/workflows/gate.yml` (as committed at `0916b55`)
- **Relevance:** the job the setup-uv and `uv sync` steps are added to.
- **Key patterns:** both repositories under the workspace (`patchbay/`, `patchbay-standards/`),
  the pin step reading `.version` into `GITHUB_OUTPUT`, every action pinned to a commit with its
  tag beside it, `persist-credentials: false`, `working-directory: patchbay` for the gate.

### The sibling's gate script

- **Location:** `../patchbay-standards/scripts/gate.sh`
- **Relevance:** the pin-comment style ("Pinned: pymarkdownlnt 0.9.41, published 2026-10-13. Bump
  deliberately, in the gate's own spec").
- **Key patterns:** the pin named with its publish date and the bump rule beside it; here the pins
  move to `pyproject.toml`'s dev group with the same comment shape.

### The sibling's gate workflow

- **Location:** `../patchbay-standards/.github/workflows/gate.yml`
- **Relevance:** the `astral-sh/setup-uv` step as a pinned action with the uv version as an input.
- **Key patterns:** `uses: astral-sh/setup-uv@<sha> # v10.3.3`, `with: version: "0.13.7"`; here
  with the cache on, keyed on `uv.lock`, and `uv sync --locked` after it.

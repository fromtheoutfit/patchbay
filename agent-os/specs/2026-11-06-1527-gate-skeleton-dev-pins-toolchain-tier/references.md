# References for the gate spec of issues #5, #6 and #7

## Similar Implementations

### patchbay-standards' `scripts/gate.sh` at `11ceffd`

- **Location:** `git -C ../patchbay-standards show 11ceffd:scripts/gate.sh`
- **Relevance:** the skeleton `base/process/verification-gate.md` says the two repositories'
  `scripts/gate.sh` share ("In this repository", last paragraph): the `cd` and usage checks, the
  `step`, `fail`, `listed` and `present` helpers, step 1 with its root guard, and the closing line.
  #5 asks this repository to take it.
- **Key patterns:** taken word for word: the header's exit paragraph and listing paragraph, the
  guarded `cd` (exit 2, a line on stderr), `listed` (one `git ls-files -z --cached --others
  --exclude-standard` call, `LC_ALL=C sort -z`), `present` (a symlink to nothing named as one,
  before "tracked but missing from the disk"), step 1's `root=$(pwd -P)` against `git rev-parse
  --show-toplevel`. Its step 2 (pymarkdown given git's list) is the shape the listing rule's first
  form takes; this repository's steps 2–5 take the second form, and step 5 a third (see `shape.md`).

### patchbay-standards' `scripts/gate-negative-tests.sh` at `11ceffd`

- **Location:** `git -C ../patchbay-standards show 11ceffd:scripts/gate-negative-tests.sh`
- **Relevance:** the harness shape the standard's "The harness proves itself as it goes" now
  describes, and the cases #5 asks for (w: a tracked symlink to nothing, a copy without `.git`
  inside another repository; x: the `cd` failure).
- **Key patterns:** `run <name> <status> [<text>] <cmd...>`, `says` (each line of the text found in
  order, a fixed string), `later` (no `== K/M` banner past the failing step), `check` (status, then
  text, then later; a failure without text is `UNEXPECTED`), `shown` (scratch paths shortened
  into `$NEG/run.out`), `only` (the exclusive check, from the tenth spec there), `old_file` (a
  script from history run on the same copy to show the bug as it was), every setup step `|| die`,
  the j replay asserting its text.

### patchbay-standards' gate specs

- **Location:** `agent-os/specs/` in `../patchbay-standards` at `11ceffd`:
  `2026-11-05-2019-gate-spec-2-five-base-proposals/` (gate spec 2, issue #10, with
  `verification/gate-sh-diff.txt`), `2026-11-06-0721-gate-spec-3-seven-base-proposals/` (gate spec
  3, issue #12), `2026-11-06-1205-retro-proposals-upstream-and-probe-rule/` and
  `2026-11-06-1244-revision-after-pr-18-review/` (the ninth and tenth specs, gate specs as well).
- **Relevance:** gate spec 2 is where the skeleton and the reason assertion came from, and its
  `gate-sh-diff.txt` is the form this spec's diff takes (a header classifying the hunks). Gate spec
  3 added `later` and the tool pins as gate files (#6). The ninth added the present-and-file step
  (#7's comment); the tenth added `only` and split its transcript so each holds one run.
- **Key patterns:** the diff header's two kinds of hunk; one run per transcript, ending
  `harness exit=0`; the present-and-file text of its `shape-spec.md` gate step 6 and template,
  adapted here to steps 7–9 and `agent-os/standards/base/…` paths.

### Issues in patchbay-standards

- **Location:** fromtheoutfit/patchbay-standards#17 (gate spec 4: six base proposals, proposal 5
  the exclusive check) and #19 (a kept negative-test transcript holds one run).
- **Relevance:** the two harness rules the user's scope names ("the exclusive check", "one run per
  transcript") are proposals there, not yet in the synced standard; this spec follows them as the
  sibling's harness does. #17 is also the shape of the issue this spec's retrospective files.

### This repository's gate and its last transcripts

- **Location:** `scripts/gate.sh`, `scripts/gate-negative-tests.sh` at `92cd215`;
  `agent-os/specs/2026-11-05-2057-toolchain-revision-after-pr-4-review/verification/`.
- **Relevance:** the code that changes, and the exact lines each tool prints on failure (ruff's
  `Would reformat:`, `F401`, mypy's `no-any-return`, pytest's `FAILED`, uv's stale-lock and version
  lines, step 6's drift lines), which every failing run now names.
- **Key patterns:** kept: the case letters (g is step 1's list, u is "not run as the gate"), the
  `<case>/patchbay` layout beside a `<case>/patchbay-standards` symlink to one local clone, `mk`,
  `hdr`, `note`, `broken`, the j replay's Python.

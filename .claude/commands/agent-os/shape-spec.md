# Shape Spec

Gather context and structure planning for significant work. **Run this command while in plan mode.**

## Important Guidelines

- **Always use AskUserQuestion tool** when asking the user anything
- **Offer suggestions** — Present options the user can confirm, adjust, or correct
- **Keep it lightweight** — This is shaping, not exhaustive documentation

## Prerequisites

This command **must be run in plan mode**.

**Before proceeding, check if you are currently in plan mode.**

If NOT in plan mode, **stop immediately** and tell the user:

```
Shape-spec must be run in plan mode. Please enter plan mode first, then run /shape-spec again.
```

Do not proceed with any steps below until confirmed to be in plan mode.

## Process

### Step 1: Clarify What We're Building

Use AskUserQuestion to understand the scope:

```
What are we building? Please describe the feature or change.

(Be as specific as you like — I'll ask follow-up questions if needed)
```

Based on their response, ask 1-2 clarifying questions if the scope is unclear. Examples:
- "Is this a new feature or a change to existing functionality?"
- "What's the expected outcome when this is done?"
- "Are there any constraints or requirements I should know about?"

### Step 2: Gather Visuals

Use AskUserQuestion:

```
Do you have any visuals to reference?

- Mockups or wireframes
- Screenshots of similar features
- Examples from other apps

(Paste images, share file paths, or say "none")
```

If visuals are provided, note them for inclusion in the spec folder.

### Step 3: Identify Reference Implementations

Use AskUserQuestion:

```
Is there similar code in this codebase I should reference?

Examples:
- "Look at how scripts/gate.sh reports a step and stops at the first failure"
- "scripts/gate-negative-tests.sh is the fixture shape for a test on a scratch copy"
- "No existing references"

(Point me to files, folders, or features to study)
```

If references are provided, read and analyze them to inform the plan.

### Step 4: Check Product Context

Check if `agent-os/product/` exists and contains files.

If it exists, read key files (like `mission.md`, `roadmap.md`, `tech-stack.md`) and use AskUserQuestion:

```
I found product context in agent-os/product/. Should this feature align with any specific product goals or constraints?

Key points from your product docs:
- [summarize relevant points]

(Confirm alignment or note any adjustments)
```

If no product folder exists, skip this step.

### Step 5: Surface Relevant Standards

Standards come in two kinds, and the difference matters here and again in the gate:

- **Base standards** live under `agent-os/standards/base/`, synced from `patchbay-standards` by
  `scripts/sync-standards.sh` and pinned to the commit in `agent-os/standards/base/.version`. They
  are owned by `patchbay-standards`, and this repository is a consuming project: **a base standard
  is never edited here**, not during a spec and not in its retrospective. A change the spec would
  make to one is recorded in `shape.md` under `### Standards retrospective (proposed, base)` and
  presented to the owner at the end of the spec; an approved one is filed as an issue on
  `patchbay-standards` (the sibling checkout is `../patchbay-standards`), whose own spec lands it
  as a pull request, approved by a person; this repository takes it when it next moves its pin.
- **Project standards**, this repository's own files under `agent-os/standards/` outside `base/`,
  belong to this repository and change in its retrospective.

#### Step 5a: Core Architecture (always included)

The standards that apply to every spec in this repository, included without asking, with their
full content in `standards.md` and named under the `## Core Architecture (Non-Negotiable)` heading
in `shape.md`:

- **`base/python/toolchain`** — one tool per job in a uv Python package, `pyproject.toml` the only
  config file, every tool run through `uv run --locked`, and the order of the gate's tool steps
  (`agent-os/standards/base/python/toolchain.md`, "In a consuming project").
- **`base/python/layout`** — one module per concern, the `testing` subpackage, what `__init__.py`
  holds, and the one direction the modules import in.
- **`base/python/typing`** — `NewType` keys, protocols, PEP 695 generics, re-exports through
  `__all__`, and no future import where pydantic reads annotations.
- **`base/python/models`** — one frozen, closed, finite, strict base, refusing as the package,
  read-only inside, and computing alike.
- **`base/python/errors`** — one root, fields as arguments and attributes, no built-in escaping a
  public method, and the errors module the leaf the others import.

#### Step 5b: Feature-Specific Standards

Read `agent-os/standards/index.yml` to identify standards relevant to the feature being built
(in addition to the core tier above, which is included already: leave the Step 5a standards out
of the list, `python/toolchain`, `python/layout`, `python/typing`, `python/models` and
`python/errors`). Its `base:` section is synced and never
edited by hand; a key there is a path relative to `base/` without the `.md`, so
`process/verification-gate` is `agent-os/standards/base/process/verification-gate.md`. The
repository's own sections sit beside it and resolve to `agent-os/standards/<section>/<key>.md`,
except the reserved section `root`, whose keys resolve to `agent-os/standards/<key>.md`: a
standard directly under the standards folder, in no section folder.

Use AskUserQuestion to confirm:

```
The core architecture tier (Step 5a) holds base/python/toolchain, base/python/layout,
base/python/typing, base/python/models and base/python/errors, included without asking.

These standards may apply:

1. **{folder/standard}** — {what it covers}
2. **{folder/standard}** — {what it covers}

Should I include these in the spec? (yes / adjust: remove 2, add {folder/standard})
```

Read the confirmed standards files to include their content in the plan context.

**What you read here is a snapshot.** `standards.md` records the standards *as they read
when the spec was shaped*. If the work teaches them something, they change at the END of
the spec, in the retrospective (gate step 9) — not by editing `standards.md` after the fact.
If the plan needs a pattern no standard covers, that is a standards change to decide with
the user now, not an ad-hoc call to make during implementation. For a base standard that
decision is a proposal (see above), never an in-place edit.

### Step 6: Generate Spec Folder Name

Create a folder name using this format:
```
YYYY-MM-DD-HHMM-{feature-slug}/
```

Where:
- Date/time is current timestamp
- Feature slug is derived from the feature description (lowercase, hyphens, max 40 chars)

Example: `2026-01-15-1430-user-comment-system/`

**Note:** If `agent-os/specs/` doesn't exist, create it when saving the spec folder.

### Step 7: Structure the Plan

Now build the plan with **Task 1 always being "Save spec documentation"**.

Present this structure to the user:

```
Here's the plan structure. Task 1 saves all our shaping work before implementation begins.

---

## Task 1: Save Spec Documentation

Create `agent-os/specs/{folder-name}/` with:

- **plan.md** — This full plan
- **shape.md** — Shaping notes (scope, decisions, context from our conversation)
- **standards.md** — Relevant standards that apply to this work
- **references.md** — Pointers to reference implementations studied
- **visuals/** — Any mockups or screenshots provided

## Task 2: [First implementation task]

[Description based on the feature]

## Task 3: [Next task]

...

## Task N (FINAL — ALWAYS INCLUDED): Verification gate

Run the full verification gate, in order. The spec is not complete until every step passes:

1. `bash -n` on every shell script under `scripts/` as git lists them (tracked or untracked,
   not ignored), at a work-tree top that is the repository root, as git says, with no tracked
   file a `.gitignore` ignores — every script must parse; any other file there fails the step
   by name
2. `uv sync --locked`, then `uv run --locked ruff format --check` over the `.py` and `.pyi`
   files git lists — the locked toolchain syncs, and every file is formatted as ruff format
   writes it
3. `uv run --locked ruff check` over the same files — no violation of `[tool.ruff.lint]` in
   `pyproject.toml`
4. `uv run --locked mypy` over the `.py` and `.pyi` files git lists under `src/` and `tests/` —
   no type error under `[tool.mypy]` (strict)
5. `uv run --locked pytest` — every test under `tests/` passes (`[tool.pytest.ini_options]`),
   once no `.py` or `test*.txt` file under `tests/`, and no `conftest.py` at the root or root file
   pytest reads ahead of `pyproject.toml` (`pytest.toml`, `.pytest.toml`, `pytest.ini`,
   `.pytest.ini`), is one git ignores
   — steps 2–5 run the tools pinned in `pyproject.toml`'s `[dependency-groups] dev` as `uv.lock`
   resolves them, under the uv `[tool.uv] required-version` pins; step 2's sync fails, before
   any tool runs, when the lockfile no longer matches `pyproject.toml` or the running uv is not
   the required one; ruff and mypy are given git's list itself, and pytest walks `tests/` only
   once nothing it would read is ignored
6. `scripts/sync-standards.sh --check` — `agent-os/standards/base/`, the `base:` section of
   `agent-os/standards/index.yml` and the script itself are byte-identical to `patchbay-standards`
   at the commit in `agent-os/standards/base/.version`, read from the sibling checkout
   `../patchbay-standards`
7. **Docs** — the documentation the change touches reads true after it: `README.md`, `CLAUDE.md`,
   the header comments and pointers in the files changed, and every standard that names them.
   Record what was checked in `shape.md`.
8. **Version** — the change is recorded under `[Unreleased]` in `CHANGELOG.md`, and the version
   in `pyproject.toml` bumped when a release is cut. Record it in `shape.md`.
9. **Standards retrospective** — per `agent-os/standards/base/process/standards-retrospective.md`:
   check what this spec taught against the standards, add any pattern it invented,
   correct anything it proved stale, and keep `index.yml` in step — as an edit for a
   project standard, as a proposal under `### Standards retrospective (proposed, base)` for
   a base standard. List those edits separately from the feature's when reporting, so they
   can be committed apart from it. If the spec taught nothing, record
   `Standards retrospective: no changes` in `shape.md`. "No changes" is valid; silence is not.
   Always record `Proposals sent upstream:` in `shape.md`, `none` when the retrospective
   recorded no base proposal. When it records one, before the spec reports done (the standard's
   "Base proposals go to the owner, then upstream"): present every proposal to the owner with
   AskUserQuestion, multi-select, each in one or two sentences with the shipped file and test it
   is verified against, at most three to a question, each question ending with a "None of
   these" option, four questions to a call; file the approved ones as one issue with
   `gh issue create --repo fromtheoutfit/patchbay-standards`, no AI attribution, and write its
   number beside each; mark each declined one `declined by owner, <date>`. A proposal neither
   filed nor marked declined fails the gate.

`scripts/gate.sh` runs steps 1–6 as one command, exit 1 at the first failing step after a `FAIL`
line naming it, exit 2 on usage or when it cannot enter the repository root. Steps 7–9 are
judgment, in that order, recorded in `shape.md`; the retrospective is always last.

If any step fails, fix the underlying issue (do not bypass) and rerun before marking the
spec complete.

---

Does this plan structure look right? I'll fill in the implementation tasks next.
```

### Step 8: Complete the Plan

After Task 1 is confirmed, continue building out the remaining implementation tasks based on:
- The feature scope from Step 1
- Patterns from reference implementations (Step 3)
- Constraints from standards (Step 5)

Each task should be specific and actionable.

**Always include the final verification task** (`scripts/gate.sh` — `bash -n` over the shell
scripts git lists under `scripts/`, `uv sync --locked` then
`uv run --locked ruff format --check .`, `uv run --locked ruff check .`, `uv run --locked mypy`,
`uv run --locked pytest`, `scripts/sync-standards.sh --check` — then Docs, Version and the
standards retrospective) as the last task in every plan, regardless of feature size. Do not skip
this for "small" changes — a one-file fix is exactly the kind of spec that quietly invents a
pattern.

### Step 9: Ready for Execution

When the full plan is ready:

```
Plan complete. When you approve and execute:

1. Task 1 will save all spec documentation first
2. Then implementation tasks will proceed
3. The final task runs the verification gate: the six runnable steps, then Docs,
   Version and the standards retrospective. The spec is not complete until the gate is
   green, Docs and Version are recorded, AND the standards are either updated (or
   proposed, for base/, each proposal filed upstream or declined by the owner) or
   recorded as "no changes"

Ready to start? (approve / adjust)
```

## Output Structure

The spec folder will contain:

```
agent-os/specs/{YYYY-MM-DD-HHMM-feature-slug}/
├── plan.md           # The full plan
├── shape.md          # Shaping decisions and context
├── standards.md      # Which standards apply and key points
├── references.md     # Pointers to similar code
├── verification/     # gate-run.txt, and the negative-test transcripts when a gate file changed
└── visuals/          # Mockups, screenshots (if any)
```

## shape.md Content

The shape.md file should capture:

```markdown
# {Feature Name} — Shaping Notes

## Core Architecture (Non-Negotiable)

- `base/python/toolchain`, `base/python/layout`, `base/python/typing`, `base/python/models` and
  `base/python/errors` — included without asking (Step 5a); their full text in `standards.md`.

## Scope

[What we're building, from Step 1]

## Decisions

- [Key decisions made during shaping]
- [Constraints or requirements noted]

## Context

- **Visuals:** [List of visuals provided, or "None"]
- **References:** [Code references studied]
- **Product alignment:** [Notes from product context, or "N/A"]

## Standards Applied

**Core (always applied):**
- `base/python/toolchain`, `base/python/layout`, `base/python/typing`, `base/python/models`,
  `base/python/errors` — Step 5a

**Feature-specific:**
- {folder/standard} — [why it applies]

## Verification Gate

Spec is not complete until `scripts/gate.sh` passes — `bash -n` on every shell script
under `scripts/` as git lists them, with no tracked file a `.gitignore` ignores;
`uv sync --locked`, then
`uv run --locked ruff format --check .`, `uv run --locked ruff check .`, `uv run --locked mypy`
and `uv run --locked pytest` under `pyproject.toml`'s `[tool.*]` rule set and `uv.lock`'s pins;
and `scripts/sync-standards.sh --check` against `../patchbay-standards` at the commit in
`agent-os/standards/base/.version` — and the three judgment steps are recorded, in this order:
Docs, Version, then the standards retrospective below.

**Results ({date}):** [exit status, branch, `verification/gate-run.txt`; which negative
tests were rerun if a gate file changed]

**Docs (step 7):** [what documentation was checked and reads true]

**Version (step 8):** [the `[Unreleased]` entry in `CHANGELOG.md`; the version bump, if any]

## Standards Retrospective

Step 9, always last. Per `agent-os/standards/base/process/standards-retrospective.md`. Filled
in at the END of the spec, from the shipped diff — not at shaping time. "No changes" is valid;
silence is not.

Either:

`Standards retrospective: no changes.`

Or a list, each entry naming the standard, what the spec taught it, and the shipped file
that verifies it:

- `{project standard}` — [what changed, and the code that proves it]
- `agent-os/standards/index.yml` — [updated for the above, in this repository's own sections;
  the `base:` section is synced and never edited by hand]
- **Deviation, not a standard change:** [what we did differently and why it stays a one-off]

Either way, then the one line that says where the base proposals went, in one of four forms, a
declined proposal named by its file and a short name, never by its place in the list:

Proposals sent upstream: none
Proposals sent upstream: {fromtheoutfit/patchbay-standards#N}
Proposals sent upstream: {fromtheoutfit/patchbay-standards#N}; declined: {`base/…` (short name)}
Proposals sent upstream: declined: {`base/…` (short name)}, {…}

(`none` when no proposal was recorded; the issue alone when all were filed; the issue and the
declined ones when some were declined; the declined ones alone when every one was.)

### Standards retrospective (proposed, base)

Only when the spec taught a base standard something. Proposals, never local edits; each is
presented to the owner before the spec is done, the approved ones filed as one issue on
`patchbay-standards`, whose own spec lands them as a pull request, approved by a person.

- `base/{folder/standard}.md` — [the change, and the shipped file and test that prove it].
  Proposed, not applied; filed as {fromtheoutfit/patchbay-standards#N} | declined by owner,
  {date}.
```

## standards.md Content

Include the full content of each relevant standard:

```markdown
# Standards for {Feature Name}

The following standards apply to this work, as they read when the spec was shaped
(before the retrospective). If this spec changed or proposed a change to any of them,
`shape.md`'s Standards Retrospective says which and why — this file is the snapshot, not
the current text.

---

## {folder/standard}

[Full content of the standard file]
```

## references.md Content

```markdown
# References for {Feature Name}

## Similar Implementations

### {Reference 1 name}

- **Location:** `{path}`
- **Relevance:** [Why this is relevant]
- **Key patterns:** [What to borrow from this]

### {Reference 2 name}

...
```

## Tips

- **Keep shaping fast** — Don't over-document. Capture enough to start, refine as you build.
- **Visuals are optional** — Not every feature needs mockups.
- **Feature-specific standards inform the plan** — If the plan conflicts with one, revise the plan, or record in `shape.md` why the standard doesn't apply here. A standard that's simply wrong gets fixed in the retrospective, not worked around — and a base standard gets *proposed*, not edited.
- **Specs are discoverable** — Months later, someone can find this spec and understand what was built and why.
- **The gate is the definition of done** — A spec with a script that does not parse, a base standard or index entry that drifted from the pinned commit, a doc that reads false, a missing CHANGELOG entry, or an unwritten retrospective is unfinished work, however small the change.
- **Standards are a living record** — The retrospective in gate step 9 is how they grow. A spec that taught nothing says so in `shape.md`; a spec that taught something changes a project standard (or proposes a base change) in its own change set, verified against the shipped code rather than the plan.

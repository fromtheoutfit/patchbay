# Standards Retrospective

`base/` describes how the patchbay packages are built; a consuming project syncs it in as
`agent-os/standards/base/`, next to the project's own standards. That description is only as
accurate as the last spec that checked it, and **nothing fails when it drifts**. No test goes
red because a standard describes a pattern we stopped using two specs ago, or because a spec
invented a pattern that never got written down.

This is the step that closes that loop. It runs as **the last item of the verification gate**,
on every spec-sized change, whether or not `/agent-os:shape-spec` shaped it. **Record the
answer either way**: "no changes" is a valid outcome, silence is not, because nobody can tell it
apart from "never noticed."

## Why this exists

A pattern invented inside a spec and never written down is a pattern the next spec re-invents
differently. Three specs later there are three ways to do the same thing, all of them
defensible, none of them written anywhere, and the standards confidently describe a fourth.

The cost of asking at the end of a spec is a paragraph. The cost of not asking is the
`discover-standards` pass again.

## The ordering rule

**No pattern is invented that is not in the standards.** If a spec needs one that isn't there,
it is proposed, added, and only then used, in that order. Reaching the retrospective and
discovering a whole new pattern already shipped means the proposal step was skipped; add it now
(or propose it, if it belongs in `base/`), and note in `shape.md` that it landed late.

At shaping time this means: when the plan needs a pattern the standards don't cover, that is a
standards change to decide with the user, not an ad-hoc call to make inside the implementation.

## The questions

Check each against the spec's actual diff.

1. **Did this spec introduce a pattern no standard covers?** A new adapter shape, a new way of
   naming or validating a parameter, a new test seam, a new way two packages talk to each
   other. If it will be copied by the next person who does something similar, it belongs in a
   standard.
2. **Did a standard turn out to be wrong, or stale?** Correct it, citing the code that proves
   the correction. This includes standards you merely *read* during the spec and found didn't
   match reality; you don't have to have changed the code to have learned this.
3. **Did the spec deliberately deviate from a standard?** Either the standard grows the
   exception (with its condition), or the deviation is recorded in `shape.md` as a one-off with
   its reason. A deviation that is neither will read as a violation to the next reviewer.
4. **Did anything a standard points at move, get renamed, or get deleted?** File paths, module
   and class names, config keys, command and script names, and test-file references inside
   standards go stale silently. Fix the pointer.

## Verify against the code, not against the spec

**A standard rewritten during a retrospective is verified against the shipped code and tests,
never against the spec's own decisions or plan.** Read the artifact being described, not the
artifact that described it.

A sibling project has already paid for this lesson. A guard was meant to hold a list of third
parties equal to the list a published document named, and the list was transcribed by reading
that document. The document was missing one entry, so the guard was missing it too, and it
passed. A description copied from the thing it describes agrees with that thing by
construction, **including when the thing is wrong**. The same trap catches a standard rewritten
from the plan that shaped the code instead of from the code that shipped.

## Who owns which standard

Two kinds of standard sit side by side in a consuming project, and the retrospective treats
them differently:

- **Base standards** live under `base/` in `patchbay-standards` and are synced into a consuming
  project as `agent-os/standards/base/`, pinned to a commit. They are owned by
  `patchbay-standards`, and **a base standard is never edited in place during a spec**, not in
  a consuming project and not in `patchbay-standards` itself. The change the spec would make is
  written up in `shape.md` under `## Standards retrospective (proposed, base)`: the file, the
  change, and the shipped code that proves it. That proposal becomes a pull request to
  `patchbay-standards`; a consuming project picks it up on its next sync, and until then lives
  with the standard as it is. The proposal, not a local edit, is the record. (Inside
  `patchbay-standards`, changing a base standard is a spec's feature work on its own branch,
  never a side effect of some other spec's retrospective.)
- **Project standards**, everything under `agent-os/standards/` outside `base/`, belong to the
  project and are edited in the retrospective as the questions above direct.

**Every standards edit is approved by a person, always**: a base proposal as the pull request to
`patchbay-standards`, a project standard in the project's own review of the retrospective's
change set. An agent proposes; it does not land a standard on its own.

## Keep the index in step

A standard added, renamed or removed carries its index entry in the same change set: a project
standard in the project's own sections of `agent-os/standards/index.yml`, a base proposal in the
root `index.yml` of `patchbay-standards`, where `scripts/check-index.sh` holds the index to the
files under `base/` and the `gate` check is required on `main`, so a proposal without its entry
does not merge. The index's format, the description line and how a consuming project's index
relates to the root index are `base/process/standards-index.md`'s.

## Never edit this file from inside a retrospective

A gate that rewrites its own terms during the process it governs is precisely what this
prohibition exists for. Strengthening or relaxing the retrospective is a deliberate edit made in
its own spec, with the user, on its own branch, never inside the retrospective of some other spec.

The gate's own files are under the same rule. Which files those are, and that they change only in
a spec whose feature is the gate, are `base/process/verification-gate.md`'s.

## Recording the answer

`shape.md` gets a `## Standards Retrospective` heading. One of two shapes:

```markdown
## Standards Retrospective

Standards retrospective: no changes.
```

or

```markdown
## Standards Retrospective

- `agent-os/standards/testing/fixtures.md` — added the shared-fixture rule; this spec found
  that two adapters each built the same fake device. Verified against `tests/conftest.py` as
  shipped.
- `agent-os/standards/index.yml` — description updated for the above.
- **Deviation, not a standard change:** the dry-run flag skips the version check. One-off;
  nothing reads the version on that path.

### Standards retrospective (proposed, base)

- `base/process/standards-retrospective.md` — [the change, and the shipped code that proves
  it]. Proposed, not applied; becomes a pull request to `patchbay-standards`.
```

The `(proposed, base)` list appears only when the spec taught a base standard something; it
holds proposals and never a local edit.

## Git

The retrospective's edits are **their own change set**, separate from the feature's: a
standards change that arrives buried inside a feature diff is a standards change nobody
reviews.

Committing, pushing and staging follow the `## Git` rule in `CLAUDE.md`. "Own change set" means
the retrospective's files are listed explicitly and separately when the work is reported, so
they can be committed apart from the feature. Leaving them unlisted, mixed into a wall of
modified files, defeats the point.

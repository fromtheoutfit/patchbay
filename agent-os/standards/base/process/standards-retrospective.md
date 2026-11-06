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

**The same holds of a tool's documentation, and of a probe.** A rule that rests on how a tool
behaves is verified by running the tool at its pinned version, on a scratch copy, with the
transcript in the spec's `verification/`, and:

- **the probe's cases are chosen so they can tell the competing claims apart**, not only the
  case that confirms the expected one;
- **the probe's setup is shown to have done what it claims** before its result is read;
- **where a probe and the documentation disagree, the tool's source at the pinned version
  decides**.

A spec that changes such a rule reruns the probe.

`patchbay-standards` paid for all three in one spec. A probe of a build tool tried one version
range outside the running tool, saw the build succeed with a warning, and concluded that the range
did not matter, against the tool's documentation. The range held another version that the tool's
source, at the pinned version, lists as accepted. A range outside every accepted version, and an
exact pin of another version, cases the probe never ran, build with a package fetched from the
index and fail offline: the documentation was right. A second probe, meant to empty a linter's
ignore list, overrode the list in a configuration layer that does not reset the file's and showed
no finding for a rule the file ignores, the same reading a review finding rested on. The tool's
printed settings showed the setup had not done what it claimed; with the selection reset as well,
the rule reports on every file.

## Who owns which standard

Two kinds of standard sit side by side in a consuming project, and the retrospective treats
them differently:

- **Base standards** live under `base/` in `patchbay-standards` and are synced into a consuming
  project as `agent-os/standards/base/`, pinned to a commit. They are owned by
  `patchbay-standards`, and **a base standard is never edited in place during a spec**, not in
  a consuming project and not in `patchbay-standards` itself. The change the spec would make is
  written up in `shape.md` under `### Standards retrospective (proposed, base)`: the file, the
  change, and the shipped code that proves it. That proposal goes to the owner before the spec
  is done and, approved, to `patchbay-standards` as an issue (below), whose own spec lands it as
  a pull request; a consuming project picks it up on its next sync, and until then lives with
  the standard as it is. The proposal, not a local edit, is the record. (Inside
  `patchbay-standards`, changing a base standard is a spec's feature work on its own branch,
  never a side effect of some other spec's retrospective.)
- **Project standards**, everything under `agent-os/standards/` outside `base/`, belong to the
  project and are edited in the retrospective as the questions above direct.

**Every standards edit is approved by a person, always**: a base proposal when the owner sends it
upstream and again as the pull request to `patchbay-standards`, a project standard in the
project's own review of the retrospective's change set. An agent proposes; it does not land a
standard on its own.

## Base proposals go to the owner, then upstream

A retrospective that records one or more entries under
`### Standards retrospective (proposed, base)` is not complete until the owner has seen them. The
agent presents every proposal, each in one or two sentences with the shipped file and the test it
is verified against, and asks which to send upstream: AskUserQuestion, multi-select. A question
holds at most four options, so it carries at most three proposals and ends with a "None of these"
option. A call holds at most four questions, so twelve proposals; more take another call. Then,
before the spec reports done:

- **The approved proposals become one issue on `patchbay-standards`**, created with
  `gh issue create --repo fromtheoutfit/patchbay-standards` from the project's checkout, with no
  AI attribution (`base/process/ownership.md`). It has one section per proposal with its
  verification pointer, a "Depends on" line naming the repository and branch that hold the
  evidence, and it ends with the rules its spec is held to, as
  `fromtheoutfit/patchbay-standards#12` does. The issue's number is written in `shape.md` beside
  each proposal it carries.
- **Its title names it a gate spec when any proposal it carries needs a gate file changed**
  (`base/process/verification-gate.md`), and a standards spec otherwise. A gate spec's issue says
  which proposals touch gate files, and its standards proposals land with it in the same spec.
- **A declined proposal stays in `shape.md`**, marked `declined by owner, <date>`, so the record
  says it was seen.
- **A proposal neither filed nor marked declined is a gate failure for the spec.** The step is
  judgment, like the rest of the retrospective; no machine runs it.

The issue is filed while the evidence it cites is still uncommitted work on the branch, since an
agent never pushes (`base/process/ownership.md`); the owner's push puts it there. When the pull
request opens, whoever writes its body, the owner or an agent asked to, names the issue in the
body, adds the pull request to the issue's "Depends on" line, and checks that every path the issue
cites exists at the pull request's head.

Writing the issue is the agent's work; which proposals it carries is the owner's call. The rule
holds in `patchbay-standards` too: a proposal recorded here becomes an issue here, and the spec
that takes the issue lands it as a pull request.

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

Proposals sent upstream: none.
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

Proposals sent upstream: fromtheoutfit/patchbay-standards#<N>; declined:
`base/process/verification-gate.md` (<its short name>).

### Standards retrospective (proposed, base)

- `base/process/standards-retrospective.md` — [the change, and the shipped file and test that
  prove it]. Proposed, not applied; filed as fromtheoutfit/patchbay-standards#<N>.
- `base/process/verification-gate.md` — [the change, and the shipped file and test that prove
  it]. Proposed, not applied; declined by owner, <date>.
```

The `(proposed, base)` list appears only when the spec taught a base standard something; it
holds proposals and never a local edit. Each entry ends with the issue it was filed in or
`declined by owner, <date>`. The `Proposals sent upstream:` line is always there, in one of four
forms:

- `none`, when the retrospective recorded no proposal;
- the issue, when every proposal was filed in it;
- the issue, then `; declined:` and the declined ones, when some were declined;
- `declined:` and the declined ones, with no issue, when every one was declined.

A declined proposal is named by its file and a short name, never by its place in the list, which
a later edit can reorder.

## Git

The retrospective's edits are **their own change set**, separate from the feature's: a
standards change that arrives buried inside a feature diff is a standards change nobody
reviews.

Committing, pushing and staging follow the `## Git` rule in `CLAUDE.md`. "Own change set" means
the retrospective's files are listed explicitly and separately when the work is reported, so
they can be committed apart from the feature. Leaving them unlisted, mixed into a wall of
modified files, defeats the point.

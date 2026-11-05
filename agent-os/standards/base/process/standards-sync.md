# Standards Sync

`base/` is written here and read everywhere: a consuming project holds a copy of it as
`agent-os/standards/base/`, beside its own standards, and the `base:` section of its
`agent-os/standards/index.yml` is the root `index.yml` of this repository. This standard fixes how
that copy is made and kept: `scripts/sync-standards.sh`, run from the project's root, and the
invariant it holds.

## What the sync writes, and nothing else

`scripts/sync-standards.sh [--init] [<path-to-patchbay-standards> [<ref>]]`, run from the project's
root, writes four things at one commit of that checkout: the one `<ref>` resolves to, by default
the checkout's `origin/HEAD`, origin's default branch, so a bare sync pins a pushed, merged commit.
`<path>` defaults to `../patchbay-standards`, the sibling checkout, and a path inside a checkout
resolves to its top. The four:

- **`agent-os/standards/base/`**, replaced whole with `base/` as committed, so a file removed here
  is removed there.
- **`agent-os/standards/base/.version`**, the commit as forty hex digits and a newline: the one
  file under a project's `base/` that is not a standard.
- **The `base:` section of `agent-os/standards/index.yml`**, replaced with the `base:` section of
  the root `index.yml` at that commit, byte for byte. Every other line of the project's index is
  left as it was, in place and in order.
- **`scripts/sync-standards.sh`**, the project's copy, replaced with the script at that same commit
  as the last thing the sync writes, so the project carries the script at its pinned commit and
  the next sync runs it. The sync that delivers a change to the script is run by the copy before
  it: a fix to the sync applies from the next sync on.

It reads from the commit's tree, never the working tree: each file is read raw with `git cat-file`,
so an uncommitted edit in the checkout cannot be synced, neither a standard nor the script itself,
and neither can the checkout's line-ending settings or attributes. Every precondition is checked
first, and `base/`, `.version` and the new index are built in a temporary directory and swapped in
only then: a refusal leaves the project as it was. What it did is reported on stderr (each file
added, removed or changed, the old and new commit, what the index and the script did) and as one
JSON object on stdout after the last write, for a wrapper to read. Exit 0 is a sync whose result
it compared against the export and found equal; 1 is a result that did not match; 2 is usage or a
precondition, each named: a bad flag or two mode flags, a directory that is not the top of a git
work tree, `<path>` not a patchbay-standards checkout, no `origin/HEAD` to default the ref to,
`<ref>` not a commit, no parseable `base:` section in the project's index without `--init` or in
the commit's `index.yml`, a path under `base/` that is not a regular file or holds a control
character. An explicit `<ref>` whose commit is not on origin's default branch is synced with a
`WARN` line naming it: a commit not pushed or not merged can be rebased or abandoned, leaving the
pin at nothing.

## The invariant

**`agent-os/standards/base/`, less `.version`, and the `base:` section of the project's index are
byte-identical to `base/` and the root `index.yml` of `patchbay-standards` at the commit in
`.version`**, and the project's `scripts/sync-standards.sh` is the script at that commit.
`scripts/sync-standards.sh --check [<path>]` holds it: it exports the pinned commit from the
checkout and names every file missing, extra or changed, whether the `base:` section differs and
whether the script does, exit 1 on any of them, writing nothing. The project's files are the
tracked ones plus the untracked ones git does not ignore, as `scripts/check-index.sh` reads them,
so an ignored `.DS_Store` is never drift. A pinned commit the checkout does not have is a
precondition (exit 2), not drift: fetch it. The check is a step of the project's gate.

No entry in the `base:` section and no file under `base/` is edited by hand. A description the
project disagrees with, a rule it would change, a standard it lacks, is changed in
`patchbay-standards` by a pull request there and taken when the project moves its pin; the
proposal shape is `base/process/standards-retrospective.md`'s.

## Pinned, not tracking

A project pins one commit and stays on it until it decides otherwise. The default ref is origin's
default branch, so a bare sync moves to what is merged, never to whatever branch the checkout
happens to be on. Syncing forward is deliberate: read this repository's `CHANGELOG.md` from the
pinned commit to the target first, since the `base/` lines of each entry are what the sync will
bring in; run the sync; read what it reports; commit the result in its own change set, titled
`chore: sync base standards to <sha>`. That commit changes nothing but `agent-os/standards/base/`,
`.version`, the `base:` section and `scripts/sync-standards.sh`. Work the new standards ask of the
project's own files is its own spec, after.

## The index

The `base:` section is the line `base:` with nothing after the colon, and every line after it that
is indented, blank or a column-0 comment, up to the last indented line: a trailing blank or comment
line and the next column-0 key are the project's, and a trailing comment in the root `index.yml`
stays here. The sync replaces that span and nothing else, so the project's own sections, its
header comment, its blank lines and the comments it keeps beside its keys come through byte for
byte; test r in `scripts/gate-negative-tests.sh` holds that against an index built by hand, a
section on line 1 included.

- **`--index-only [<path>]`** regenerates the section alone, from the commit in `.version`, and
  touches no file under `base/` and not the script. It is the regeneration that is safe to run on
  a synced index: a hand-edited entry is drift to `--check` and is repaired by it (test s). The
  stock `/agent-os:index-standards` rewrites the whole file and is not run on a synced index, as
  `base/process/standards-index.md` says.
- **`--init`** creates the section for a project syncing for the first time, before the first
  column-0 key other than `root:` that sorts after `base` (above the column-0 comment lines
  directly over that key, which stay with it) or at the end, with one blank line on each side, and
  creates the file when there is none. That is the one place the sync normalizes: the blank lines
  directly above the insertion collapse to the one, and a missing final newline is added. Without
  `--init` a missing section is refused; a `base:` line that is not a parseable section (a second
  `base:` line, or content after the colon) is refused either way.

## In this repository

`scripts/sync-standards.sh` lives here and is run from a consuming project; here
`agent-os/standards/base` is a symlink and the script refuses to run (exit 2, test u). It is a
gate file in every project, so it changes only in its own spec here, carrying its negative tests:
o to v in `scripts/gate-negative-tests.sh`, each on a scratch checkout whose `HEAD` and
`origin/main` hold the working tree's files beside a scratch Agent OS project with its own index
sections and standards, the sync run from the project with the sibling checkout as the default
path and its `origin/main` as the default ref. Gate step 1 parses the script.

## In a consuming project

This standard is synced in as `agent-os/standards/base/process/standards-sync.md`. The project's
checkout of `patchbay-standards` sits beside it as `../patchbay-standards`. The first sync is run
from the checkout's copy, `../patchbay-standards/scripts/sync-standards.sh --init`, which installs
`scripts/sync-standards.sh`; every later sync and check runs the project's copy.
`scripts/sync-standards.sh --check` is a step of the project's `scripts/gate.sh`. The project's
gate workflow checks both repositories out under the workspace, since `actions/checkout` writes
nowhere else: the project into a subdirectory and `patchbay-standards` beside it, at the commit in
`agent-os/standards/base/.version` (a step reads the file and passes it as that checkout's `ref`,
or the checkout fetches the whole history), each action pinned as the gate standard directs, and
runs `scripts/gate.sh` with the project's directory as the working directory. The hosted run then
compares against the real thing at the pinned commit, and does not go red when `main` moves here.

# Standards Index

`agent-os/standards/index.yml` is what `/agent-os:shape-spec` Step 5 reads to decide which
standards a spec surfaces, and what `/agent-os:inject-standards` matches against. A standard that
is not indexed is invisible to every spec after the one that wrote it: the file exists and nobody
finds it. This standard fixes the index's format and how a consuming project's index relates to
the root index of `patchbay-standards`.

## Keys

- **The index has two levels, section then key**, as the stock Agent OS commands read it: a
  section is a folder directly under the standards root, and a key resolves to
  `agent-os/standards/<section>/<key>.md`. The one exception is the reserved section `root`,
  which the stock commands resolve to `agent-os/standards/<key>.md`: a standard directly under
  the standards root, in no folder.
- **A key is the standard's path relative to its section, without the `.md`.** In the `base:`
  section the key carries the whole path under `base/`: `base/process/ownership.md` is
  `process/ownership`, and resolves to `agent-os/standards/base/process/ownership.md` in a
  consuming project. The section is `base`; the slash inside the key is the folder under it.
- **Sections are alphabetical, and keys are alphabetical within their section**, as the stock
  `/agent-os:index-standards` command writes them.

## The description line

- **One line, saying what the standard decides**, not what area it belongs to. The description
  is what retrieval matches a spec's context against; "testing conventions" matches nothing,
  "every adapter builds its fake device from the shared fixture" matches the spec that needs it.
- **The value holds no colon followed by a space and no space followed by a hash.** The stock
  commands read the file as YAML, where the first nests the rest of the line as a mapping and the
  second starts a comment that silently cuts the description short. Say it another way.
- **The description is rewritten when the standard's rule changes**, in the same change set.

## Every standard and nothing else

- **Every file under the standards folder has an entry, and no entry lacks a file.** In
  `patchbay-standards`, `scripts/check-index.sh` holds `index.yml` to this at every gate run and
  names each miss: a tracked file under `base/` with no entry, an entry with no tracked file. The
  files are the tracked ones, from `git ls-files`, and the script refuses what sits beside them: a
  file under `base/` that is not tracked, so a standard never added to git is reported by name
  rather than passed over, and a tracked file missing from the disk, so a deletion not yet staged
  is reported rather than counted as present. An ignored stray such as `.DS_Store` is neither
  tracked nor reported. The script runs only in a git work tree, and says so otherwise.
- **Only standards live under `base/`**: every file there is a `.md` and is indexed. Notes, drafts
  and assets live elsewhere; `check-index.sh` refuses a tracked non-`.md` file under `base/` by
  name.
- **A base change that adds, renames or removes a file carries its index entry** in the same
  change; the `gate` check is required on `main`, so a change without it does not merge.

## Two indexes, one `base:` section

- **The root `index.yml` of `patchbay-standards` holds the `base:` section and nothing else.**
  It is the source of every base entry.
- **A consuming project's `agent-os/standards/index.yml` is the project's own sections plus a
  `base:` section identical to the root `base:` section at the commit the project pins.** No
  entry in that section is edited by hand: an entry it lacks, or a description it disagrees
  with, is changed in `patchbay-standards` and taken when the project moves its pin. The section
  is replaced whole by `scripts/sync-standards.sh`, at the commit it records in
  `agent-os/standards/base/.version`; how, and what else the sync writes, is
  `base/process/standards-sync.md`'s.
- **A project's own sections are edited by hand, in the same change set as its own standards**,
  as the retrospective standard directs. The stock `/agent-os:index-standards` command rewrites
  the whole file, the `base:` section included, and removes entries it finds no file for without
  asking, so it is not run on an index that carries a synced `base:` section. The regeneration
  that is safe to run is `scripts/sync-standards.sh --index-only`, which replaces the `base:`
  section alone and leaves every other line in place (`base/process/standards-sync.md`).

## In this repository

- **`agent-os/standards/index.yml` is a symlink to `../../index.yml`**, because this repository
  has no sections of its own and the root index is the whole of its index: one file to edit,
  nothing to keep equal. `check-index.sh` refuses anything else by what it found, a regular file
  even when its bytes match, a symlink to any other target, or nothing. The root file is edited;
  the link follows by construction.
- **`agent-os/standards/base` is a symlink to `../../base`**, so the stock commands resolve
  `agent-os/standards/base/<key>.md` here exactly as in a consuming project. The symlink is this
  repository's convenience and never ships to a project; a project holds a copy, pinned to a
  commit.

## In a consuming project

This standard is synced in as `agent-os/standards/base/process/standards-index.md`. The project's
`agent-os/standards/index.yml` carries the `base:` section as the sync wrote it and its own
sections beside it; its retrospective keeps its own sections in step, and proposes base entries to
`patchbay-standards`.

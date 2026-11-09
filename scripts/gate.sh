#!/usr/bin/env bash
# The runnable half of the verification gate: steps 1-6 of the gate every spec in this
# repository ends with (.claude/commands/agent-os/shape-spec.md, Task N). Steps 7-9 are
# judgment, recorded in the spec's shape.md: Docs (the documentation the change touches reads
# true), Version (the change under [Unreleased] in CHANGELOG.md) and the standards
# retrospective per agent-os/standards/base/process/standards-retrospective.md; nothing here can
# run them. The shape of the gate is agent-os/standards/base/process/verification-gate.md's.
# CI runs this same script and nothing else (.github/workflows/gate.yml).
#
# Usage: scripts/gate.sh        (no arguments; any argument is usage, exit 2)
#
# Exit status: 0 when every step passed; 1 at the first step that fails, after a line
# "FAIL  step N/M: <reason>" on stderr naming it, whatever status the tool returned, so a
# failing step 1 is reported before step 2 has a chance to pass; 2 on usage, or when the
# repository root cannot be entered, each said on stderr with no step run.
#
# A step that reads files from the tree reads the files git lists (the rule in
# agent-os/standards/base/process/verification-gate.md, "One script"): the tracked files plus the
# untracked ones git does not ignore, in one git ls-files -z call, each path once (a path in merge
# conflict is in the index once per stage), so an ignored stray such as .DS_Store is never seen
# and a file a spec adds before it is staged is. Each listing is written to a file in a temporary
# directory and git's own status checked, since neither a pipe nor a process substitution keeps
# it: a listing git could not make (a corrupt index) fails its step by name rather than reading as
# an empty one. Step 1 first refuses a tree whose work-tree top is not the repository root, a copy
# without .git inside another repository included, so no step lists files against an outer
# repository; it asks git whether this is inside a work tree (git rev-parse --is-inside-work-tree
# is true, which it is not in .git/ or a bare repository, where --show-cdup is empty too) and
# whether it is the top (--show-cdup is empty), and compares no paths, since a path typed in
# another case, or spelled C:/ rather than /c/, names the same directory. Step 1 then refuses every
# tracked file a committed .gitignore matches under the paths the gate's listings read (git
# ls-files --cached --ignored --exclude-per-directory=.gitignore -- ., step 2 listing the whole
# tree: a file force-added, or added before its pattern), naming each under one FAIL line: git
# lists such a file though the repository says it is ignored, and a tool that reads .gitignore
# itself skips it. Only committed .gitignore files count, so every clone of a commit gets the same
# answer; .git/info/exclude and the global excludes file are the machine's, and a file no step
# reads never fails the gate. A listed path missing from the disk, or a symlink to nothing, fails
# its step by name. Step 1 parses a file ending in .sh or starting with a bash shebang; any other
# file fails the step by name, since only shell scripts live under scripts/. Steps 2-4 give ruff
# and mypy git's list itself: the .py and .pyi files it lists (for mypy, those under src/ and
# tests/), as explicit paths, so git alone decides what .gitignore, .git/info/exclude and the
# global excludes file hide. pytest has no form that reads a list without also loading the
# conftest.py of each directory it collects from, so step 5 lets it walk tests/ (testpaths) and
# first refuses, by name, any .py file git ignores there, an ignored test*.txt there, which its
# doctest plugin collects, an ignored conftest.py at the root, which pytest loads too, and an
# ignored pytest.toml, .pytest.toml, pytest.ini or .pytest.ini at the root, each read in place of
# pyproject.toml (the spec of issue #12, verification/probes.txt): with nothing ignored for pytest
# to read, its walk reads only what git lists. Step 5's listing keeps --exclude-standard: it
# guards what pytest reads on this machine, which those files are.
#
# Steps 2-5 run the Python toolchain: ruff format --check, ruff check, mypy and pytest, each as
# `uv run --locked <tool>` from the repository root. Pins: the tools are pinned exactly in the
# [dependency-groups] dev section of pyproject.toml, each with the date it was published, and
# resolved in uv.lock; uv itself is pinned by [tool.uv] required-version there. Step 2 opens with
# `uv sync --locked`, which installs exactly what uv.lock names into .venv (a package the lock does
# not name is removed, as in CI) and fails the step as the sync, before any tool runs, when the
# lockfile no longer matches pyproject.toml (it is never rewritten), when uv cannot read either file
# or build the package from them (a license-files entry with no file, say), or when the running uv
# is not the required version; so a pin edited without re-locking is a failure by name and the gate
# writes nothing but the ignored .venv and caches. The tools then run under --locked, a check the
# sync has already passed. The rule set each step reads is the [tool.*] sections of pyproject.toml,
# named in that file's header; a value ruff or pytest cannot parse fails its step. A pin or a rule
# is changed deliberately, in the gate's own spec
# (agent-os/standards/base/process/verification-gate.md), and the gate rerun.
#
# Step 1 needs bash, git and mktemp. Steps 2-5 need git, which lists their files, uv on PATH at the
# version [tool.uv] required-version pins (the one runtime this repository assumes;
# agent-os/standards/base/process/ownership.md) and, the first time, network access to fetch the
# locked packages and the interpreter .python-version names into uv's cache. Step 6 needs git,
# cmp, comm, awk and sed, and the sibling checkout of patchbay-standards at ../patchbay-standards
# holding the commit pinned in agent-os/standards/base/.version
# (agent-os/standards/base/process/standards-sync.md). Nothing else is installed to run the gate.
set -euo pipefail
cd "$(dirname "$0")/.." || { echo "gate: cannot enter the repository root, $(dirname "$0")/..; not run as the gate" >&2; exit 2; }

if [ $# -ne 0 ]; then
  echo "usage: scripts/gate.sh   (no arguments; exits 1 at the first failing step, 2 on usage)" >&2
  exit 2
fi

step() { printf '\n== %s\n' "$1"; }
fail() { printf 'FAIL  step %s: %s\n' "$1" "$2" >&2; exit 1; }   # fail <step> <reason>
git_list() { local out=$1; shift; git ls-files -z "$@" > "$out.raw" && LC_ALL=C sort -zu "$out.raw" > "$out"; }   # git_list <file> <ls-files args...>: git's list into <file>, NUL-separated, sorted, each path once; fails when git cannot list
listed() { local out=$1; shift; git_list "$out" --cached --others --exclude-standard -- "$@"; }   # listed <file> <path...>: what git lists under the paths, tracked or untracked not ignored
fail_list() {  # fail_list <step> <reason> <file>: fail the step naming every path in the NUL-separated file, each indented eight spaces
  local f
  printf 'FAIL  step %s: %s:\n' "$1" "$2" >&2
  while IFS= read -r -d '' f; do printf '        %s\n' "$f" >&2; done < "$3"
  exit 1
}
present() {  # present <step> <path>: fail the step unless the listed path is on the disk
  if [ -L "$2" ] && [ ! -e "$2" ]; then fail "$1" "$2 is a symlink to nothing"; fi
  [ -e "$2" ] || fail "$1" "$2 is tracked but missing from the disk"
}

step "1/6  bash -n on every shell script under scripts/ (tracked or untracked, not ignored), in a tree with no tracked file a .gitignore ignores"
root=$(pwd -P)
inside=$(git rev-parse --is-inside-work-tree 2>/dev/null) && [ "$inside" = true ] &&
  cdup=$(git rev-parse --show-cdup 2>/dev/null) && [ -z "$cdup" ] ||
  fail 1/6 "not a git work tree rooted at $root; the gate lists files with git ls-files"
tmp=$(mktemp -d) && [ -n "$tmp" ] && [ -d "$tmp" ] ||
  fail 1/6 "mktemp -d made no temporary directory for git's listings (see above)"
trap 'rm -rf "$tmp"' EXIT
git_list "$tmp/ignored" --cached --ignored --exclude-per-directory=.gitignore -- . ||
  fail 1/6 "git could not list the tracked files a .gitignore ignores (see above)"
if [ -s "$tmp/ignored" ]; then
  fail_list 1/6 "tracked, but a .gitignore ignores them; stop ignoring each (a ! pattern, and for a file under an ignored directory, ignore dir/* rather than dir/ first) or stop tracking it (git rm --cached)" "$tmp/ignored"
fi
listed "$tmp/scripts" scripts || fail 1/6 "git could not list the files under scripts/ (see above)"
n=0
while IFS= read -r -d '' f; do
  present 1/6 "$f"
  case "$f" in
    *.sh) ;;
    *) head -n 1 "$f" | grep -Eq '^#!.*bash' || fail 1/6 "$f is not a shell script; only shell scripts live under scripts/" ;;
  esac
  bash -n "$f" || fail 1/6 "$f does not parse"
  echo "ok   $f"; n=$((n + 1))
done < "$tmp/scripts"
[ "$n" -gt 0 ] || fail 1/6 "git lists no file under scripts/"

step "2/6  uv sync --locked, then uv run --locked ruff format --check over the .py and .pyi files git lists (the locked toolchain; the formatter)"
listed "$tmp/tree" . || fail 2/6 "git could not list the files of the tree (see above)"
py=()
while IFS= read -r -d '' f; do
  case "$f" in *.py|*.pyi) present 2/6 "$f"; py+=("$f") ;; esac
done < "$tmp/tree"
[ "${#py[@]}" -gt 0 ] || fail 2/6 "git lists no .py or .pyi file"
command -v uv >/dev/null 2>&1 || fail 2/6 "uv is not on PATH; steps 2-5 run the pinned tools through uv run --locked"
uv sync --locked ||
  fail 2/6 "uv could not sync the locked toolchain: uv.lock does not match pyproject.toml, uv could not read them or build the package, or this uv is not the version [tool.uv] requires (see above)"
echo "ok   the locked toolchain synced"
uv run --locked ruff format --check -- "${py[@]}" ||
  fail 2/6 "a file is not formatted as ruff format would write it, or ruff could not read its settings (see above)"
echo "ok   ${#py[@]} file(s) formatted"

step "3/6  uv run --locked ruff check over the same files (the linter: [tool.ruff.lint] of pyproject.toml)"
uv run --locked ruff check -- "${py[@]}" || fail 3/6 "ruff check found a violation, or could not read its rule set (see above)"
echo "ok   no violation"

step "4/6  uv run --locked mypy over the .py and .pyi files git lists under src/ and tests/ ([tool.mypy] of pyproject.toml: strict)"
listed "$tmp/src" src tests || fail 4/6 "git could not list the files under src/ and tests/ (see above)"
src=()
while IFS= read -r -d '' f; do
  case "$f" in *.py|*.pyi) present 4/6 "$f"; src+=("$f") ;; esac
done < "$tmp/src"
[ "${#src[@]}" -gt 0 ] || fail 4/6 "git lists no .py or .pyi file under src/ or tests/"
uv run --locked mypy -- "${src[@]}" || fail 4/6 "mypy found a type error (see above)"
echo "ok   no type error"

step "5/6  uv run --locked pytest ([tool.pytest.ini_options] of pyproject.toml, over tests/, once nothing pytest would read is one git ignores)"
git_list "$tmp/pytest" --others --ignored --exclude-standard -- tests conftest.py pytest.toml .pytest.toml pytest.ini .pytest.ini ||
  fail 5/6 "git could not list what it ignores under tests/ (see above)"
while IFS= read -r -d '' f; do
  case "$f" in
    */__pycache__/*) ;;
    *.py) fail 5/6 "$f is a .py file git ignores, which pytest would read; remove it, or stop ignoring it" ;;
    pytest.toml|.pytest.toml|pytest.ini|.pytest.ini) fail 5/6 "$f is a pytest configuration file git ignores, which pytest would read in place of pyproject.toml; remove it, or stop ignoring it" ;;
    *) case "${f##*/}" in test*.txt) fail 5/6 "$f is a doctest file git ignores, which pytest would read; remove it, or stop ignoring it" ;; esac ;;
  esac
done < "$tmp/pytest"
uv run --locked pytest || fail 5/6 "a test failed, or pytest could not read its configuration (see above)"
echo "ok   every test passed"

step "6/6  scripts/sync-standards.sh --check: agent-os/standards/base/, the base: section and the script match patchbay-standards at the commit in .version (../patchbay-standards)"
scripts/sync-standards.sh --check ||
  fail 6/6 "drift from patchbay-standards at the pinned commit, or the sibling checkout ../patchbay-standards unusable (see above)"

printf '\nGate steps 1-6 passed. Steps 7-9 are judgment, recorded in shape.md: Docs, Version, the standards retrospective.\n'

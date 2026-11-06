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
# failing step 1 is reported before step 2 has a chance to pass; 2 on usage.
#
# Step 1 parses every shell script under scripts/ as git lists them: the tracked files plus the
# untracked ones git does not ignore (the rule scripts/sync-standards.sh applies to base/), so an
# ignored stray such as .DS_Store is never seen and a script a spec adds before it is staged is. A
# file ending in .sh or starting with a bash shebang is parsed; any other file fails the step by
# name, since only shell scripts live under scripts/; a tracked file missing from the disk, and a
# tree that is not a git work tree, each fail by name.
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
# Step 1 needs bash and git. Steps 2-5 need uv on PATH at the version [tool.uv] required-version
# pins (the one runtime this repository assumes; agent-os/standards/base/process/ownership.md)
# and, the first time, network access to fetch the locked packages and the interpreter
# .python-version names into uv's cache. Step 6 needs git, cmp, comm, awk and sed, and the sibling
# checkout of patchbay-standards at ../patchbay-standards holding the commit pinned in
# agent-os/standards/base/.version (agent-os/standards/base/process/standards-sync.md). Nothing
# else is installed to run the gate.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ $# -ne 0 ]; then
  echo "usage: scripts/gate.sh   (no arguments; exits 1 at the first failing step, 2 on usage)" >&2
  exit 2
fi

step() { printf '\n== %s\n' "$1"; }
fail() { printf 'FAIL  step %s: %s\n' "$1" "$2" >&2; exit 1; }   # fail <step> <reason>

step "1/6  bash -n on every shell script under scripts/ (tracked or untracked, not ignored)"
git rev-parse --show-toplevel >/dev/null 2>&1 || fail 1/6 "not a git work tree; step 1 lists files with git ls-files"
n=0
while IFS= read -r -d '' f; do
  [ -e "$f" ] || fail 1/6 "$f is tracked but missing from the disk"
  case "$f" in
    *.sh) ;;
    *) head -n 1 "$f" | grep -Eq '^#!.*bash' || fail 1/6 "$f is not a shell script; only shell scripts live under scripts/" ;;
  esac
  bash -n "$f" || fail 1/6 "$f does not parse"
  echo "ok   $f"; n=$((n + 1))
done < <({ git -c core.quotePath=false ls-files -z -- scripts
           git -c core.quotePath=false ls-files -z --others --exclude-standard -- scripts; } | LC_ALL=C sort -zu)
[ "$n" -gt 0 ] || fail 1/6 "git lists no file under scripts/"

step "2/6  uv sync --locked, then uv run --locked ruff format --check . (the locked toolchain; the formatter)"
command -v uv >/dev/null 2>&1 || fail 2/6 "uv is not on PATH; steps 2-5 run the pinned tools through uv run --locked"
uv sync --locked ||
  fail 2/6 "uv could not sync the locked toolchain: uv.lock does not match pyproject.toml, uv could not read them or build the package, or this uv is not the version [tool.uv] requires (see above)"
echo "ok   the locked toolchain synced"
uv run --locked ruff format --check . ||
  fail 2/6 "a file is not formatted as ruff format would write it, or ruff could not read its settings (see above)"
echo "ok   every file formatted"

step "3/6  uv run --locked ruff check . (the linter: [tool.ruff.lint] of pyproject.toml)"
uv run --locked ruff check . || fail 3/6 "ruff check found a violation, or could not read its rule set (see above)"
echo "ok   no violation"

step "4/6  uv run --locked mypy ([tool.mypy] of pyproject.toml: strict, over src/ and tests/)"
uv run --locked mypy || fail 4/6 "mypy found a type error (see above)"
echo "ok   no type error"

step "5/6  uv run --locked pytest ([tool.pytest.ini_options] of pyproject.toml, over tests/)"
uv run --locked pytest || fail 5/6 "a test failed, or pytest could not read its configuration (see above)"
echo "ok   every test passed"

step "6/6  scripts/sync-standards.sh --check: agent-os/standards/base/, the base: section and the script match patchbay-standards at the commit in .version (../patchbay-standards)"
scripts/sync-standards.sh --check ||
  fail 6/6 "drift from patchbay-standards at the pinned commit, or the sibling checkout ../patchbay-standards unusable (see above)"

printf '\nGate steps 1-6 passed. Steps 7-9 are judgment, recorded in shape.md: Docs, Version, the standards retrospective.\n'

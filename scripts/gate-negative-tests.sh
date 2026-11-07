#!/usr/bin/env bash
# Negative tests of the verification gate (agent-os/standards/base/process/verification-gate.md,
# "Every step that can fail is proven to fail"). Not run by scripts/gate.sh; gate step 1 parses this
# file. Each test lays a scratch copy of the gate's inputs out as <case>/patchbay in a fresh
# temporary directory (scripts/, the standards, pyproject.toml, uv.lock, .python-version, README.md
# and LICENSE, which the package build reads, src/ and tests/), git-inits and git-adds the copy (the
# gate and the sync script list files with git and run only at the top of a work tree), puts a
# patchbay-standards checkout beside it as <case>/patchbay-standards, breaks the copy in one way,
# and must fail with the named reason and exit status, the steps after it never reached; the
# positive cases beside them must pass. The checkout is a symlink to one git clone of
# ../patchbay-standards made per run: a local clone, which shares the sibling's objects and so holds
# the pinned commit whichever of the sibling's refs reaches it; the drift check reads the pin from
# agent-os/standards/base/.version, not from any branch (agent-os/standards/base/process/
# standards-sync.md, "In a consuming project"). A copy that reaches step 2 syncs its own .venv from
# uv's cache in step 2's `uv sync --locked`, a second or two per case, and that is the only install
# a case makes.
#
# Every run names the status it expects, and a run that expects a failure also names the lines its
# output must hold, in order, each a fixed string found within a line: the tool's own line naming
# the file where one is printed, then the gate's "FAIL  step N/M: <reason>" line last. gate.sh gives
# exit 1 for every step's failure and sync-standards.sh exit 2 for every precondition, so a status
# alone cannot tell a guard from its absence. A text naming gate.sh's FAIL  step N/M line also holds
# the run to no step banner past step N, and one that is gate.sh's usage or cd line to none at all,
# so the steps after a failure are checked as never reached, not assumed. run takes text only for
# a run expected to fail; a passing run names the lines its output must hold with holds after it
# (or through check, as j's replay does), and times holds one whole line to an exact count. The
# text says nothing of what else was printed, so a case that says step 6 names one drift alone
# follows its run with only, which holds the lines of step 6's drift report to exactly those it
# names. A mismatch of any of these is marked UNEXPECTED and the
# harness exits 1 at the end naming the count, so the transcript's last line says whether every
# case behaved. Every setup step (a command that builds a case's state) stops the harness by name
# when it fails (exit 2) rather than letting a case fail for the wrong reason. Nothing in the tree
# and nothing in ../patchbay-standards is written: the scratch directory is refused unless mktemp
# made it, outside this repository, and only then is the trap that removes it set. The transcript
# of one run is kept in the spec's verification/ folder as gate-negative-tests.txt (every test but
# j) and ci-negative-test.txt (j, the CI replay), each holding that one run and ending on its count;
# an earlier run kept as evidence, a failing one before a fix, goes in a file of its own.
#
# Usage: scripts/gate-negative-tests.sh [test ...]   (default: every test but j; "all" adds j)
#   tests: a b c d e f g h i k l m n o p q r u j
#   a  an unparsable script under scripts/: gate.sh stops at step 1, exit 1, step 2 never reached
#   b  one byte appended to a file under agent-os/standards/base/: step 6 names it changed alone
#   c  a hand-edited entry in the base: section of the index: step 6 reports the section alone
#   d  the sibling checkout missing: step 6 names ../patchbay-standards, exit 1 (the sync's own: 2)
#   e  the copy's scripts/sync-standards.sh edited: step 6 reports the script alone
#   f  an untracked .md under agent-os/standards/base/: step 6 names it extra alone
#   g  step 1's file list: an ignored scripts/.DS_Store passes; the copy entered through its path in
#      upper case passes step 1 (case-insensitive file systems only); a script in a three-way
#      merge conflict is listed once; a tracked non-shell file, a tracked script missing from the
#      disk, a tracked symlink to nothing, a corrupt index, a copy that is not a git work tree and
#      the same copy inside another repository's work tree each fail by name; the gate at 92cd215
#      or 6adf50e is shown where it had the bug, as it was
#   h  a misformatted module under src/patchbay/: step 2 names it, exit 1, step 3 never reached
#   i  a formatted module with an unused import: step 2 passes, step 3 reports F401, exit 1
#   k  a function returning Any where it promises int: steps 2-3 pass, step 4 reports it under
#      strict (no-any-return is a strict check), exit 1
#   l  a test asserting the wrong version: steps 2-4 pass, step 5 reports the failure, exit 1
#   m  the rule set is read from pyproject.toml: line-length lowered to 40 makes the clean tree
#      fail step 2 (a changed value applied); line-length = "wide" is refused by ruff at step 2;
#      a stray "[" is refused by step 2's uv sync, each by name
#   n  a dev pin edited in pyproject.toml without re-locking: step 2's uv sync --locked fails, uv
#      naming the stale lockfile, with the sync's reason; ruff never runs, exit 1
#   o  [tool.uv] required-version set to a uv that is not running: step 2's uv sync fails, uv
#      naming the required and the running version, with the sync's reason, exit 1
#   p  steps 2-4 read git's list: an ignored src/patchbay/local_settings.py with format, lint and
#      type faults passes the gate; force-added while .gitignore still matches it, git lists it and
#      step 2 names it; clean but for a type error, step 4 names it, where mypy walking under
#      exclude_gitignore (the first spec's step 4) passes; in a linked worktree, a module hidden
#      only by .git/info/exclude passes the gate, where that walk names it
#   q  step 5 refuses what pytest would read that git ignores: an ignored failing test, an ignored
#      tests/unit/conftest.py that deselects a tracked failing test (pytest given --ignore for it,
#      the first spec's step 5, passes), and an ignored conftest.py at the root, each by name
#   r  a listing git cannot make fails its step by name: a git that refuses the listing call of
#      step 2, of step 4, and of step 5 in turn, each step after it never reached
#   u  not run as the gate: --help and a stray argument exit 2 with the usage line, a script that
#      cannot enter the repository root exits 2 saying so, no step run; the clean copy exits 0
#   j  the CI replay: the run steps of .github/workflows/gate.yml on a clean copy and a broken one
# Needs git and uv (steps 2-5 of the gate run through it; j reads the workflow with pyyaml,
# through uv run --with, installing nothing). Needs ../patchbay-standards beside this repository,
# as the gate does. g runs the gate from history (git show <sha>:scripts/gate.sh, at 92cd215 or
# 6adf50e) to show the bugs it guards against as they were; that part is skipped where the commit
# is absent, and g's upper-case run on a case-sensitive file system. r puts a git that refuses one
# call on PATH, in the scratch directory.
set -uo pipefail
die() { echo "harness: $1" >&2; exit 2; }   # die <reason>: a setup failure, not a test result
cd "$(dirname "$0")/.." || die "cannot enter the repository root"
REPO=$(pwd -P)
SIBLING=$(cd "$REPO/../patchbay-standards" 2>/dev/null && pwd -P) ||
  die "../patchbay-standards is missing; the gate and these tests need it beside this repository"
NEG=$(mktemp -d) || die "mktemp -d failed"
[ -n "$NEG" ] && [ -d "$NEG" ] || die "mktemp -d gave no directory"
NEG=$(cd "$NEG" && pwd -P) || die "the scratch directory cannot be entered"   # physical, as the scripts print it
case "$NEG" in
  "$REPO"|"$REPO"/*) die "the scratch directory $NEG is inside this repository; refusing to use it" ;;
esac
trap 'rm -rf "${NEG:?}"' EXIT
NEGUP=$(printf '%s' "$NEG" | tr '[:lower:]' '[:upper:]')   # the scratch path typed in upper case (g)
git clone -q "$SIBLING" "$NEG/patchbay-standards" || die "could not clone $SIBLING into the scratch directory"

# The gate's own failure lines, named by the cases that end on them.
F2SYNC="FAIL  step 2/6: uv could not sync the locked toolchain: uv.lock does not match pyproject.toml, uv could not read them or build the package, or this uv is not the version [tool.uv] requires (see above)"
F2FMT="FAIL  step 2/6: a file is not formatted as ruff format would write it, or ruff could not read its settings (see above)"
F6="FAIL  step 6/6: drift from patchbay-standards at the pinned commit, or the sibling checkout ../patchbay-standards unusable (see above)"
USAGE="usage: scripts/gate.sh   (no arguments; exits 1 at the first failing step, 2 on usage)"

runs=0; unexpected=0
says() {  # says <text> <file>: each line of the text is found in the file, in order, as a fixed string within a line
  WANT=$1 awk 'BEGIN { n = split(ENVIRON["WANT"], w, "\n"); k = 1 }
    k <= n && index($0, w[k]) { k++ }
    END { exit (k <= n) }' "$2"
}
later() {  # later <n> <file>: the file holds a gate.sh step banner (== K/M) past step <n>
  awk -v n="$1" '/^== [0-9]+\// && substr($0, 4) + 0 > n { f = 1 } END { exit !f }' "$2"
}
check() {  # check <expected status> <status> [<expected text> <printed output>]: print the status; assert it, the text (required for a failure), and no gate.sh step past the one the text fails at
  local n=
  runs=$((runs + 1))
  case ${3:-} in
    *'FAIL  step '[0-9]*) n=${3##*FAIL  step }; n=${n%%/*} ;;   # the last FAIL  step N/M line the text names
    'usage: scripts/gate.sh'*|'gate: cannot enter'*) n=0 ;;      # not run as the gate: no step at all
  esac
  if [ "$2" -ne "$1" ]; then
    echo "exit=$2  UNEXPECTED (expected $1)"; unexpected=$((unexpected + 1))
  elif { [ "$1" -ne 0 ] || [ -n "${3:-}" ]; } && ! { [ -n "${3:-}" ] && says "$3" "$4"; }; then
    echo "exit=$2  UNEXPECTED (the output does not say: ${3:-<no reason named>})"; unexpected=$((unexpected + 1))
  elif [ -n "$n" ] && later "$n" "$4"; then
    echo "exit=$2  UNEXPECTED (a step after step $n was reached)"; unexpected=$((unexpected + 1))
  else
    echo "exit=$2"
  fi
}
shown() {  # shown <raw output>: print it with the scratch paths shortened to <copy name> (<COPY NAME> when typed in upper case), into $NEG/run.out too
  sed -e "s#$NEG/\([a-z0-9-]*\)#<copy \1>#g" -e "s#$NEGUP/\([A-Z0-9-]*\)#<COPY \1>#g" "$1" > "$NEG/run.out" || die "sed on $1"
  cat "$NEG/run.out"
}
run() {  # run <case> <expected status> [<expected text, when the status is not 0>] <cmd...>: run in <case>/patchbay, print its output and status, assert both
  local c=$1 want=$2 text= got; shift 2
  if [ "$want" -ne 0 ]; then text=$1; shift; fi
  ( cd "$NEG/$c/patchbay" && "$@" ) > "$NEG/run.raw" 2>&1; got=$?
  shown "$NEG/run.raw"
  check "$want" "$got" "$text" "$NEG/run.out"
}
only() {  # only <line>...: after run, the lines step 6's drift check printed under "check base standards against" (each indented two spaces: the missing, extra and changed entries, then the index and script lines) are exactly these, in order; a mismatch is UNEXPECTED, an assertion on that run, not another run
  local want got
  want=$(printf '  %s\n' "$@")
  got=$(awk '/^check base standards against / { f = 1; next } f && /^  [^ ]/' "$NEG/run.out")
  if [ "$got" = "$want" ]; then
    echo "only=$(printf '%s; ' "$@")"
  else
    echo "only=$(printf '%s; ' "$@") UNEXPECTED (listed: $(printf '%s\n' "$got" | sed 's/^ *//' | paste -sd ';' -))"; unexpected=$((unexpected + 1))
  fi
}
holds() {  # holds <text>: after run, its output holds each line of the text, in order (a passing run's named lines); a mismatch is UNEXPECTED, an assertion on that run
  if says "$1" "$NEG/run.out"; then echo "holds=$(printf '%s' "$1" | paste -sd ';' -)"
  else echo "holds=$(printf '%s' "$1" | paste -sd ';' -)  UNEXPECTED (not in the output, in order)"; unexpected=$((unexpected + 1)); fi
}
times() {  # times <n> <line>: after run, its output holds exactly this whole line exactly n times; a mismatch is UNEXPECTED, an assertion on that run
  local got
  got=$(grep -cxF -- "$2" "$NEG/run.out")
  if [ "$got" -eq "$1" ]; then echo "times=$1 x $2"
  else echo "times=$1 x $2  UNEXPECTED (found $got)"; unexpected=$((unexpected + 1)); fi
}
hdr() { printf '\n### %s\n' "$1"; }
note() { printf -- '-- %s\n' "$1"; }
mk() {  # mk <case>: <case>/patchbay, a copy of the gate's inputs, git-added, with the sibling symlinked beside it
  d="$NEG/$1"; rm -rf "$d" || die "mk $1: rm"; mkdir -p "$d/patchbay/agent-os" || die "mk $1: mkdir"
  cp -R scripts src tests "$d/patchbay/" || die "mk $1: cp scripts src tests"
  cp -R agent-os/standards "$d/patchbay/agent-os/" || die "mk $1: cp standards"
  cp .gitignore .python-version pyproject.toml uv.lock README.md LICENSE "$d/patchbay/" || die "mk $1: cp the package files"
  git -c init.defaultBranch=main -C "$d/patchbay" init -q || die "mk $1: git init"
  git -C "$d/patchbay" add -A || die "mk $1: git add"
  ln -s ../patchbay-standards "$d/patchbay-standards" || die "mk $1: ln"
}
old_file() {  # old_file <case> <sha> <path>: <path> as of <sha>, in <case>/patchbay as <stem>-<sha>.sh, or return 1
  if git cat-file -e "$2:$3" 2>/dev/null; then
    git show "$2:$3" > "$NEG/$1/patchbay/${3%.sh}-$2.sh" || die "old_file $1 $2 $3"
    chmod +x "$NEG/$1/patchbay/${3%.sh}-$2.sh" || die "old_file $1 $2 $3: chmod"
  else
    note "commit $2 is not in this repository; its $3 is not shown"; return 1
  fi
}
broken() { printf '#!/usr/bin/env bash\nif true; then\n' > "$NEG/$1/patchbay/scripts/broken.sh" || die "broken $1"; }   # broken <case>: an unparsable script in the copy

tests=("$@")
[ "${#tests[@]}" -eq 0 ] && tests=(a b c d e f g h i k l m n o p q r u)
[ "${tests[*]}" = all ] && tests=(a b c d e f g h i k l m n o p q r u j)

for t in "${tests[@]}"; do case "$t" in
a) hdr "a (unparsable script scripts/broken.sh: gate.sh must fail at step 1 naming it, exit 1, and never print 2/6)"
   mk a; broken a
   run a 1 $'scripts/broken.sh: line 3: syntax error: unexpected end of file\nFAIL  step 1/6: scripts/broken.sh does not parse' scripts/gate.sh ;;
b) hdr "b (one byte appended to agent-os/standards/base/process/ownership.md: steps 1-5 pass, step 6 must name it changed and nothing else, exit 1)"
   mk b; printf 'x' >> "$NEG/b/patchbay/agent-os/standards/base/process/ownership.md" || die "b: append"
   run b 0 git status --short
   run b 1 $'ok   every test passed\n  changed  process/ownership.md\nFAIL  drift from patchbay-standards at\n'"$F6" scripts/gate.sh
   only 'changed  process/ownership.md' 'index    base: section identical' 'script   scripts/sync-standards.sh matches' ;;
c) hdr "c (a description in the base: section of agent-os/standards/index.yml hand-edited: step 6 must report the section differs and nothing else, exit 1)"
   mk c
   sed -i.bak 's/^    description: A person owns every commit/    description: Hand-edited here/' "$NEG/c/patchbay/agent-os/standards/index.yml" || die "c: sed"
   rm "$NEG/c/patchbay/agent-os/standards/index.yml.bak" || die "c: rm .bak"
   run c 0 git diff --stat
   run c 1 $'  index    base: section differs\nFAIL  drift from patchbay-standards at\n'"$F6" scripts/gate.sh
   only 'index    base: section differs' 'script   scripts/sync-standards.sh matches' ;;
d) hdr "d (no checkout at ../patchbay-standards: step 6 must fail naming it, exit 1; the sync script's own status is 2, the gate's is 1)"
   mk d; rm "$NEG/d/patchbay-standards" || die "d: rm symlink"
   note "the sync script alone, for its status:"
   run d 2 "FAIL  ../patchbay-standards is not a git checkout; pass the path to a patchbay-standards checkout" scripts/sync-standards.sh --check
   note "the gate:"
   run d 1 $'FAIL  ../patchbay-standards is not a git checkout; pass the path to a patchbay-standards checkout\n'"$F6" scripts/gate.sh ;;
e) hdr "e (a comment appended to the copy's scripts/sync-standards.sh: steps 1-5 pass, step 6 must report the script differs and nothing else, exit 1)"
   mk e; printf '\n# a hand edit to the synced script\n' >> "$NEG/e/patchbay/scripts/sync-standards.sh" || die "e: append"
   run e 0 git status --short
   run e 1 $'  script   scripts/sync-standards.sh differs\nFAIL  drift from patchbay-standards at\n'"$F6" scripts/gate.sh
   only 'index    base: section identical' 'script   scripts/sync-standards.sh differs' ;;
f) hdr "f (an untracked agent-os/standards/base/process/extra.md: step 6 must name it extra and nothing else, exit 1)"
   mk f; printf '# Extra\n\nNot a synced standard.\n' > "$NEG/f/patchbay/agent-os/standards/base/process/extra.md" || die "f: write"
   run f 0 git status --short
   run f 1 $'  extra    process/extra.md\nFAIL  drift from patchbay-standards at\n'"$F6" scripts/gate.sh
   only 'extra    process/extra.md' 'index    base: section identical' 'script   scripts/sync-standards.sh matches' ;;
g) hdr "g (step 1 lists files with git: an ignored scripts/.DS_Store passes; the copy entered through its path in upper case passes step 1; a script in a three-way merge conflict is listed once; a corrupt index is refused by name; a tracked scripts/notes.txt is refused by name; a tracked script deleted from the disk, and a tracked symlink to nothing, are each refused by name; a copy that is not a git work tree, and the same copy inside another repository's work tree, are each refused by name)"
   mk g; touch "$NEG/g/patchbay/scripts/.DS_Store" || die "g: touch"
   note "untracked, ignored scripts/.DS_Store present (must pass, exit 0; the gate never lists it):"
   run g 0 git status --short --ignored scripts
   run g 0 scripts/gate.sh
   UPC=$(printf '%s' "$NEG/g/patchbay" | tr '[:lower:]' '[:upper:]')
   if [ -d "$UPC" ]; then
     note "the copy entered through its path in upper case (this file system is case-insensitive): step 1 asks git whether this is the top, compares no paths, and must pass, as steps 2-5 do; step 6 must then fail in the synced sync-standards.sh, whose own root check still compares the two paths as strings (proposed upstream), exit 1:"
     run g 1 $'ok   scripts/sync-standards.sh\nok   every test passed\nFAIL  run from the consuming project\'s root, the top of its git work tree\n'"$F6" bash -c 'cd "$1" && scripts/gate.sh' _ "$UPC"
     if old_file g 6adf50e scripts/gate.sh; then
       note "the gate at 6adf50e on the same: step 1 compares pwd -P with git's top as strings and refuses the repository's own root (the bug):"
       run g 1 "FAIL  step 1/6: not a git work tree rooted at <COPY G>/PATCHBAY; the gate lists files with git ls-files" bash -c 'cd "$1" && scripts/gate-6adf50e.sh' _ "$UPC"
       rm "$NEG/g/patchbay/scripts/gate-6adf50e.sh" || die "g: rm old gate"
     fi
   else
     note "this file system is case-sensitive: the copy's path in upper case is no directory, so the upper-case run is skipped"
   fi
   printf '#!/usr/bin/env bash\necho conflict\n' > "$NEG/g/patchbay/scripts/conflict.sh" || die "g: conflict.sh"
   ch=$(git -C "$NEG/g/patchbay" hash-object -w scripts/conflict.sh) || die "g: hash-object"
   printf '100755 %s 1\tscripts/conflict.sh\n100755 %s 2\tscripts/conflict.sh\n100755 %s 3\tscripts/conflict.sh\n' "$ch" "$ch" "$ch" |
     git -C "$NEG/g/patchbay" update-index --index-info || die "g: index-info"
   note "scripts/conflict.sh in a three-way merge conflict, its index entry at stages 1, 2 and 3 (step 1 must list it once, and the gate pass, exit 0):"
   run g 0 git ls-files -s scripts/conflict.sh
   run g 0 scripts/gate.sh
   times 1 'ok   scripts/conflict.sh'
   if old_file g 6adf50e scripts/gate.sh; then
     note "the gate at 6adf50e on the same: listed without -u, the path is parsed, printed and counted three times (the bug):"
     run g 0 scripts/gate-6adf50e.sh
     times 3 'ok   scripts/conflict.sh'
     rm "$NEG/g/patchbay/scripts/gate-6adf50e.sh" || die "g: rm old gate"
   fi
   git -C "$NEG/g/patchbay" rm -q --cached scripts/conflict.sh || die "g: rm conflict"; rm "$NEG/g/patchbay/scripts/conflict.sh" || die "g: rm conflict file"
   cp "$NEG/g/patchbay/.git/index" "$NEG/g-index" || die "g: save index"
   printf 'garbage' > "$NEG/g/patchbay/.git/index" || die "g: corrupt index"
   note "the copy's index overwritten with garbage, so git cannot list (must fail at step 1 naming the listing, exit 1, 2/6 never printed):"
   run g 1 $'index file smaller than expected\nFAIL  step 1/6: git could not list the files under scripts/ (see above)' scripts/gate.sh
   if old_file g 6adf50e scripts/gate.sh; then
     note "the gate at 6adf50e on the same: the listing's failure is swallowed in the process substitution, and step 1 says git lists no file (the bug):"
     run g 1 "FAIL  step 1/6: git lists no file under scripts/" scripts/gate-6adf50e.sh
     rm "$NEG/g/patchbay/scripts/gate-6adf50e.sh" || die "g: rm old gate"
   fi
   cp "$NEG/g-index" "$NEG/g/patchbay/.git/index" || die "g: restore index"
   run g 0 git status --short scripts
   printf 'a note\n' > "$NEG/g/patchbay/scripts/notes.txt" || die "g: notes"; git -C "$NEG/g/patchbay" add scripts/notes.txt || die "g: add notes"
   note "scripts/notes.txt tracked, neither .sh nor a bash shebang (must fail at step 1 naming it, exit 1, 2/6 never printed):"
   run g 1 "FAIL  step 1/6: scripts/notes.txt is not a shell script; only shell scripts live under scripts/" scripts/gate.sh
   git -C "$NEG/g/patchbay" rm -q --cached scripts/notes.txt || die "g: rm notes"; rm "$NEG/g/patchbay/scripts/notes.txt" || die "g: rm notes file"
   rm "$NEG/g/patchbay/scripts/gate-negative-tests.sh" || die "g: rm harness copy"
   note "scripts/gate-negative-tests.sh tracked but deleted from the disk, deletion not staged (must fail at step 1 naming it, exit 1):"
   run g 0 git status --short scripts
   run g 1 "FAIL  step 1/6: scripts/gate-negative-tests.sh is tracked but missing from the disk" scripts/gate.sh
   git -C "$NEG/g/patchbay" checkout -q -- scripts/gate-negative-tests.sh || die "g: restore"
   ln -s nowhere.sh "$NEG/g/patchbay/scripts/dangling.sh" || die "g: ln dangling"; git -C "$NEG/g/patchbay" add scripts/dangling.sh || die "g: add dangling"
   note "scripts/dangling.sh tracked, a symlink to nothing (must fail at step 1 naming it as one, not as missing from the disk, exit 1):"
   run g 1 "FAIL  step 1/6: scripts/dangling.sh is a symlink to nothing" scripts/gate.sh
   if old_file g 92cd215 scripts/gate.sh; then
     note "the gate at 92cd215 (main before this spec) on the same: the symlink named missing from the disk (the bug):"
     run g 1 "FAIL  step 1/6: scripts/dangling.sh is tracked but missing from the disk" scripts/gate-92cd215.sh
     rm "$NEG/g/patchbay/scripts/gate-92cd215.sh" || die "g: rm old gate"
   fi
   git -C "$NEG/g/patchbay" rm -q --cached scripts/dangling.sh || die "g: rm dangling"; rm "$NEG/g/patchbay/scripts/dangling.sh" || die "g: rm dangling link"
   rm -rf "$NEG/g/patchbay/.git" || die "g: rm .git"
   note "the copy's .git removed (must fail at step 1 by name, exit 1):"
   run g 1 "FAIL  step 1/6: not a git work tree rooted at <copy g>/patchbay; the gate lists files with git ls-files" scripts/gate.sh
   mkdir "$NEG/go" || die "g: mkdir go"; git -c init.defaultBranch=main -C "$NEG/go" init -q || die "g: git init go"
   cp -R "$NEG/g" "$NEG/go/copy" || die "g: cp into go"
   rm -rf "$NEG/go/copy/patchbay/.venv" || die "g: rm the copied .venv"
   rm "$NEG/go/copy/patchbay-standards" || die "g: rm copied symlink"; ln -s ../../patchbay-standards "$NEG/go/copy/patchbay-standards" || die "g: ln go"
   note "the same copy, still without .git, inside another repository's work tree (<copy go>, nothing tracked there): git's work-tree top is the outer repository, not the copy:"
   run go/copy 0 git rev-parse --show-toplevel
   note "the shipped gate on it (must fail at step 1 by name, exit 1, no file listed against the outer repository):"
   run go/copy 1 "FAIL  step 1/6: not a git work tree rooted at <copy go>/copy/patchbay; the gate lists files with git ls-files" scripts/gate.sh
   if old_file go/copy 92cd215 scripts/gate.sh; then
     note "the gate at 92cd215 on the same: step 1 lists the copy's files as the outer repository's untracked ones and passes, steps 2-5 run, and only the sync script's own guard, at step 6, stops it, for another reason (the bug):"
     run go/copy 1 $'ok   scripts/sync-standards.sh\nok   every test passed\nFAIL  run from the consuming project\'s root, the top of its git work tree\nFAIL  step 6/6' scripts/gate-92cd215.sh
   fi ;;
h) hdr "h (src/patchbay/_broken.py misformatted: step 1 passes, step 2 must name the file, exit 1, and never print 3/6)"
   mk h; printf '"""A module the formatter would rewrite."""\n\nx  =  1\n' > "$NEG/h/patchbay/src/patchbay/_broken.py" || die "h: write"
   run h 1 $'--> src/patchbay/_broken.py\n'"$F2FMT" scripts/gate.sh ;;
i) hdr "i (src/patchbay/_unused.py formatted but importing os unused: step 2 passes, step 3 must report F401 naming the file, exit 1, and never print 4/6)"
   mk i; printf '"""A module with an import nothing uses."""\n\nimport os\n' > "$NEG/i/patchbay/src/patchbay/_unused.py" || die "i: write"
   run i 1 $'file(s) formatted\nF401 [*] `os` imported but unused\n--> src/patchbay/_unused.py\nFAIL  step 3/6: ruff check found a violation, or could not read its rule set (see above)' scripts/gate.sh ;;
k) hdr "k (tests/unit/test_broken_types.py returns Any from a function typed -> int: steps 2-3 pass, step 4 must report no-any-return, a check strict turns on, exit 1, and never print 5/6)"
   mk k
   cat > "$NEG/k/patchbay/tests/unit/test_broken_types.py" <<'SRC' || die "k: write"
"""A function that returns Any where it promises int; mypy --strict refuses it, ruff does not."""

import json


def parsed() -> int:
    """Return whatever json gives, typed as int."""
    return json.loads("1")
SRC
   run k 1 $'ok   no violation\ntests/unit/test_broken_types.py:8: error: Returning Any from function declared to return "int"  [no-any-return]\nFAIL  step 4/6: mypy found a type error (see above)' scripts/gate.sh ;;
l) hdr "l (tests/unit/test_broken_assertion.py asserts the version is 9.9.9: steps 2-4 pass, step 5 must report the failure, exit 1, and never print 6/6)"
   mk l
   cat > "$NEG/l/patchbay/tests/unit/test_broken_assertion.py" <<'SRC' || die "l: write"
"""A test that states the wrong version."""

import patchbay


def test_version_is_something_else() -> None:
    """Fails: the version is not 9.9.9."""
    assert patchbay.__version__ == "9.9.9"
SRC
   run l 1 $'ok   no type error\nFAILED tests/unit/test_broken_assertion.py::test_version_is_something_else\nFAIL  step 5/6: a test failed, or pytest could not read its configuration (see above)' scripts/gate.sh ;;
m) hdr "m (the rule set is pyproject.toml's: a changed line-length is applied and fails the clean tree at step 2; a value ruff cannot parse fails step 2 by name, and a file uv cannot parse fails step 2's sync by name)"
   mk m
   note "line-length = 100 changed to 40 in the copy's pyproject.toml (the clean tree must now fail step 2, exit 1):"
   sed -i.bak 's/^line-length = 100$/line-length = 40/' "$NEG/m/patchbay/pyproject.toml" || die "m: sed line-length"
   grep -qx 'line-length = 40' "$NEG/m/patchbay/pyproject.toml" || die "m: line-length not set to 40"
   run m 0 grep -n '^line-length' pyproject.toml
   run m 1 $'ok   the locked toolchain synced\n--> src/patchbay/__init__.py\nfiles would be reformatted\n'"$F2FMT" scripts/gate.sh
   note 'line-length = "wide" (valid TOML, a value ruff refuses; step 2 must fail after the sync passed, exit 1):'
   sed -i.bak 's/^line-length = 40$/line-length = "wide"/' "$NEG/m/patchbay/pyproject.toml" || die "m: sed wide"
   grep -qx 'line-length = "wide"' "$NEG/m/patchbay/pyproject.toml" || die "m: line-length not set to wide"
   run m 0 grep -n '^line-length' pyproject.toml
   run m 1 $'ok   the locked toolchain synced\nFailed to parse <copy m>/patchbay/pyproject.toml\ninvalid type: string "wide", expected i64\n'"$F2FMT" scripts/gate.sh
   note "the line restored to 100 and a stray [ appended (TOML uv cannot parse; step 2's sync must fail, exit 1):"
   sed -i.bak 's/^line-length = "wide"$/line-length = 100/' "$NEG/m/patchbay/pyproject.toml" || die "m: sed restore"
   rm "$NEG/m/patchbay/pyproject.toml.bak" || die "m: rm .bak"
   grep -qx 'line-length = 100' "$NEG/m/patchbay/pyproject.toml" || die "m: line-length not restored"
   printf '[\n' >> "$NEG/m/patchbay/pyproject.toml" || die "m: append"
   run m 1 $'error: Failed to parse: pyproject.toml\nunquoted keys cannot be empty\n'"$F2SYNC" scripts/gate.sh ;;
n) hdr "n (ruff==0.17.4 changed to ruff==0.17.3 in the copy's pyproject.toml, uv.lock untouched: step 2's uv sync --locked must fail with uv naming the stale lockfile and the sync's reason, ruff never run, exit 1)"
   mk n
   sed -i.bak 's/^    "ruff==0.17.4",/    "ruff==0.17.3",/' "$NEG/n/patchbay/pyproject.toml" || die "n: sed pin"
   rm "$NEG/n/patchbay/pyproject.toml.bak" || die "n: rm .bak"
   grep -q '^    "ruff==0.17.3",' "$NEG/n/patchbay/pyproject.toml" || die "n: pin not rewritten"
   run n 0 grep -n '"ruff==' pyproject.toml
   run n 1 $'error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.\n'"$F2SYNC" scripts/gate.sh ;;
o) hdr "o ([tool.uv] required-version changed to ==0.13.6 in the copy's pyproject.toml, a uv that is not the one running: step 2's uv sync must fail with uv naming both versions and the sync's reason, ruff never run, exit 1, and never print 3/6)"
   mk o
   sed -i.bak 's/^required-version = "==0.13.7"$/required-version = "==0.13.6"/' "$NEG/o/patchbay/pyproject.toml" || die "o: sed required-version"
   rm "$NEG/o/patchbay/pyproject.toml.bak" || die "o: rm .bak"
   grep -qx 'required-version = "==0.13.6"' "$NEG/o/patchbay/pyproject.toml" || die "o: required-version not rewritten"
   run o 0 grep -n '^required-version' pyproject.toml
   note "the uv running here:"
   run o 0 uv --version
   run o 1 $'error: Required uv version `==0.13.6` does not match the running version `0.13.7`\n'"$F2SYNC" scripts/gate.sh ;;
p) hdr "p (steps 2-4 read git's list: an ignored src/patchbay/local_settings.py, unformatted, with an unused import and an untyped argument, passes the gate; force-added while .gitignore still matches it, git lists it and step 2 must name it, 3/6 never printed; clean but for a type error, step 4 must name it, where mypy walking under exclude_gitignore, the first spec's step 4, passes; in a linked worktree, a module hidden only by .git/info/exclude passes the gate, where that walk names it)"
   mk p; printf 'import os\ndef f(x)->int:\n  return x\n' > "$NEG/p/patchbay/src/patchbay/local_settings.py" || die "p: write"
   run p 0 git check-ignore -v src/patchbay/local_settings.py
   note "the gate (must pass, exit 0: git's list does not hold the file, so neither ruff nor mypy is given it):"
   run p 0 scripts/gate.sh
   git -C "$NEG/p/patchbay" add -f src/patchbay/local_settings.py || die "p: add -f"
   note "force-added: git lists it as tracked, though .gitignore still matches it, and step 2 must name it, exit 1, 3/6 never printed:"
   run p 0 git ls-files src/patchbay/local_settings.py
   run p 1 $'--> src/patchbay/local_settings.py\n'"$F2FMT" scripts/gate.sh
   cat > "$NEG/p/patchbay/src/patchbay/local_settings.py" <<'SRC' || die "p: rewrite"
"""A function that returns Any where it promises int; mypy --strict refuses it, ruff does not."""

import json


def parsed() -> int:
    """Return whatever json gives, typed as int."""
    return json.loads("1")
SRC
   note "the same file, still force-added, formatted and lint-clean but returning Any where it promises int: steps 2-3 pass, step 4 must name it, exit 1, 5/6 never printed:"
   run p 1 $'ok   no violation\nsrc/patchbay/local_settings.py:8: error: Returning Any from function declared to return "int"  [no-any-return]\nFAIL  step 4/6: mypy found a type error (see above)' scripts/gate.sh
   note "mypy walking files = [src, tests] under exclude_gitignore, the first spec's step 4, on the same: it skips the tracked file .gitignore matches and passes (finding 3, the bug as it was):"
   run p 0 uv run --locked mypy --exclude-gitignore
   holds 'Success: no issues found in 3 source files'
   mk pw
   git -c user.name=test -c user.email=test@example.invalid -c commit.gpgsign=false -C "$NEG/pw/patchbay" commit -qm "the copy" || die "p: commit pw"
   mkdir "$NEG/pwt" || die "p: mkdir pwt"
   git -C "$NEG/pw/patchbay" worktree add -q --detach "$NEG/pwt/patchbay" || die "p: worktree add"
   ln -s ../patchbay-standards "$NEG/pwt/patchbay-standards" || die "p: ln pwt"
   printf 'src/patchbay/_excluded.py\n' >> "$NEG/pw/patchbay/.git/info/exclude" || die "p: info/exclude"
   cp "$NEG/p/patchbay/src/patchbay/local_settings.py" "$NEG/pwt/patchbay/src/patchbay/_excluded.py" || die "p: write _excluded"
   note "a linked worktree of a committed copy, its .git a file naming the main repository's, and src/patchbay/_excluded.py, typed wrong as above, hidden only by the main repository's .git/info/exclude:"
   run pwt 0 cat .git
   run pwt 0 git status --short --ignored src
   note "mypy walking under exclude_gitignore, the first spec's step 4: it reads <dir>/.git/info/exclude, which a worktree does not have, and names the file git hides (finding 4, the bug as it was):"
   run pwt 1 'src/patchbay/_excluded.py:8: error: Returning Any from function declared to return "int"  [no-any-return]' uv run --locked mypy --exclude-gitignore
   note "the gate in the worktree (must pass, exit 0: git's list does not hold the file):"
   run pwt 0 scripts/gate.sh ;;
q) hdr "q (step 5 refuses what pytest would read that git ignores: an ignored failing tests/unit/test_local.py; an ignored tests/unit/conftest.py that deselects a tracked failing test, which pytest given --ignore for it, the first spec's step 5, passes; an ignored conftest.py at the root; each must fail step 5 by name before pytest runs, exit 1, 6/6 never printed)"
   mk q; printf 'tests/unit/test_local.py\n' >> "$NEG/q/patchbay/.gitignore" || die "q: ignore test_local"
   cat > "$NEG/q/patchbay/tests/unit/test_local.py" <<'SRC' || die "q: write test_local"
"""A local test that states the wrong version."""

import patchbay


def test_local() -> None:
    """Fails: the version is not 9.9.9."""
    assert patchbay.__version__ == "9.9.9"
SRC
   run q 0 git status --short --ignored tests
   note "an ignored failing test (must fail at step 5 naming it, exit 1):"
   run q 1 $'ok   no type error\nFAIL  step 5/6: tests/unit/test_local.py is a .py file git ignores, which pytest would read; remove it, or stop ignoring it' scripts/gate.sh
   rm "$NEG/q/patchbay/tests/unit/test_local.py" || die "q: rm test_local"
   cat > "$NEG/q/patchbay/tests/unit/test_broken_assertion.py" <<'SRC' || die "q: write broken"
"""A test that states the wrong version."""

import patchbay


def test_version_is_something_else() -> None:
    """Fails: the version is not 9.9.9."""
    assert patchbay.__version__ == "9.9.9"
SRC
   git -C "$NEG/q/patchbay" add tests/unit/test_broken_assertion.py || die "q: add broken"
   printf 'tests/unit/conftest.py\n' >> "$NEG/q/patchbay/.gitignore" || die "q: ignore conftest"
   cat > "$NEG/q/patchbay/tests/unit/conftest.py" <<'SRC' || die "q: write conftest"
"""A local conftest git ignores, which deselects the failing test."""


def pytest_collection_modifyitems(config, items):
    keep = [i for i in items if "broken" not in i.nodeid]
    config.hook.pytest_deselected(items=[i for i in items if i not in keep])
    items[:] = keep
SRC
   note "a tracked failing test, and an ignored tests/unit/conftest.py that deselects it:"
   run q 0 git status --short --ignored tests
   note "pytest given --ignore for the conftest, the first spec's step 5: it loads the conftest anyway, the failing test is deselected, and the run passes (finding 1, the bug as it was):"
   run q 0 uv run --locked pytest --ignore=tests/unit/conftest.py
   holds '1 deselected'
   note "the gate (must fail at step 5 naming the conftest before pytest runs, exit 1):"
   run q 1 $'ok   no type error\nFAIL  step 5/6: tests/unit/conftest.py is a .py file git ignores, which pytest would read; remove it, or stop ignoring it' scripts/gate.sh
   rm "$NEG/q/patchbay/tests/unit/conftest.py" || die "q: rm conftest"
   git -C "$NEG/q/patchbay" rm -q --cached tests/unit/test_broken_assertion.py || die "q: rm --cached broken"
   rm "$NEG/q/patchbay/tests/unit/test_broken_assertion.py" || die "q: rm broken"
   printf '/conftest.py\n' >> "$NEG/q/patchbay/.gitignore" || die "q: ignore root conftest"
   printf 'raise RuntimeError("an ignored root conftest was imported")\n' > "$NEG/q/patchbay/conftest.py" || die "q: write root conftest"
   note "an ignored conftest.py at the root, which pytest loads though nothing under tests/ is ignored (must fail at step 5 naming it, exit 1):"
   run q 0 git status --short --ignored conftest.py
   run q 1 $'ok   no type error\nFAIL  step 5/6: conftest.py is a .py file git ignores, which pytest would read; remove it, or stop ignoring it' scripts/gate.sh ;;
r) hdr "r (a listing git cannot make fails its step by name: a git on PATH that refuses only the listing call of step 2, then of step 4, then of step 5, each step failing by name, exit 1, the step after it never reached)"
   mk r
   mkdir "$NEG/shim" || die "r: mkdir shim"
   cat > "$NEG/shim/git" <<SH || die "r: write shim"
#!/usr/bin/env bash
# git, refusing a call whose arguments hold \$GATE_TEST_REFUSE; every other call is the real git
case " \$* " in *"\$GATE_TEST_REFUSE"*) echo "git (test shim): refusing: \$*" >&2; exit 128 ;; esac
exec "$(command -v git)" "\$@"
SH
   chmod +x "$NEG/shim/git" || die "r: chmod shim"
   note "the listing of step 2 (git ls-files ... -- .) refused:"
   run r 1 $'git (test shim): refusing\nFAIL  step 2/6: git could not list the files of the tree (see above)' env PATH="$NEG/shim:$PATH" GATE_TEST_REFUSE=' -- . ' scripts/gate.sh
   note "the listing of step 4 (git ls-files ... -- src tests) refused:"
   run r 1 $'ok   no violation\ngit (test shim): refusing\nFAIL  step 4/6: git could not list the files under src/ and tests/ (see above)' env PATH="$NEG/shim:$PATH" GATE_TEST_REFUSE=' -- src tests ' scripts/gate.sh
   note "the listing of step 5 (git ls-files --others --ignored ...) refused:"
   run r 1 $'ok   no type error\ngit (test shim): refusing\nFAIL  step 5/6: git could not list what it ignores under tests/ (see above)' env PATH="$NEG/shim:$PATH" GATE_TEST_REFUSE=' --ignored ' scripts/gate.sh ;;
u) hdr "u (not run as the gate: --help and a stray argument each exit 2 with the usage line and run no step; a script that cannot enter the repository root exits 2 saying so; the clean copy exits 0)"
   mk u
   note "clean copy (must pass, exit 0):"
   run u 0 scripts/gate.sh
   note "--help (exit 2, no step banner):"
   run u 2 "$USAGE" scripts/gate.sh --help
   note "a stray argument (exit 2):"
   run u 2 "$USAGE" scripts/gate.sh x
   note "the copy's gate.sh run as bash -c with \$0 under a directory that does not exist, so its cd to the repository root fails (exit 2 saying so, no step banner):"
   run u 2 "gate: cannot enter the repository root, <copy u>/patchbay/nowhere/scripts/..; not run as the gate" bash -c "$(cat "$NEG/u/patchbay/scripts/gate.sh")" "$NEG/u/patchbay/nowhere/scripts/gate.sh" ;;
j) hdr "j (CI replay: the run steps of .github/workflows/gate.yml, in order, on a clean copy and on a copy with a broken script)"
   cat <<'TXT'
The workflow is not run on a hosting service here. The job's steps are read from the workflow file
and the run steps executed in order under the scratch directory laid out as the workspace (patchbay/
and patchbay-standards/ side by side, as the two checkout steps leave it), each from the step's
working-directory under the shell GitHub gives a run step on ubuntu (bash --noprofile --norc -eo
pipefail), with GITHUB_OUTPUT pointed at a scratch file whose content is printed after a step that
has an id. GitHub's rule: a step that exits non-zero fails the job unless continue-on-error is set,
and this job sets nothing. This replays the job's control flow on this machine's toolchain; it is
not the ubuntu run. The hosted run on the pull request is the proof of the workflow itself,
recorded by run id and conclusion in the spec's verification/ once it exists. The uses steps are
the two checkouts, which the scratch layout stands in for (the second takes the pin step's output
as its ref, and the replay shows the sha the step wrote beside the one in .version), and setup-uv,
which the uv already on this machine's PATH stands in for.
TXT
   echo "uv on PATH: $(uv --version)"
   mk j1; mk j2; broken j2
   replay() {  # replay <case> <expected status> [<expected text>]: the workflow's steps against $NEG/<case> as the workspace
     local c=$1 want=$2 text=${3:-} got
     : > "$NEG/$c/github-output" || die "replay $c: github-output"
     GITHUB_OUTPUT="$NEG/$c/github-output" uv run --quiet --no-project --with pyyaml python -u - "$NEG/$c" .github/workflows/gate.yml > "$NEG/run.raw" 2>&1 <<'PY'
import os, subprocess, sys, yaml
ws, wf = sys.argv[1], sys.argv[2]
w = yaml.safe_load(open(wf)); on = w[True] if True in w else w["on"]; job = w["jobs"]["gate"]
print(f"job: gate  runs-on: {job['runs-on']}  timeout-minutes: {job.get('timeout-minutes')}  on: {on}")
for i, s in enumerate(job["steps"], 1):
    if "uses" in s:
        print(f"step {i}: uses {s['uses']}  with {s.get('with', {})}  (not run here)"); continue
    cwd = os.path.join(ws, s.get("working-directory", "."))
    print(f"step {i}: run {s['run']}  (working-directory: {s.get('working-directory', '.')})")
    r = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", s["run"]], cwd=cwd)
    print(f"step {i} exit={r.returncode}")
    if "id" in s:
        print(f"step {i} (id {s['id']}) wrote to GITHUB_OUTPUT: {open(os.environ['GITHUB_OUTPUT']).read().strip()}")
    if r.returncode:
        print(f"job: FAILED at step {i} (a run step that exits non-zero fails the job)"); sys.exit(r.returncode)
print("job: passed")
PY
     got=$?
     shown "$NEG/run.raw"
     check "$want" "$got" "$text" "$NEG/run.out"
   }
   note "the commit pinned in the copy's .version:"
   run j1 0 cat agent-os/standards/base/.version
   note "j1, clean copy (the job must pass):"
   replay j1 0 $'Gate steps 1-6 passed.\njob: passed'
   note "j2, scripts/broken.sh added as in test a (gate.sh fails at step 1, exit 1, so the job must fail at the gate's step):"
   replay j2 1 $'FAIL  step 1/6: scripts/broken.sh does not parse\njob: FAILED at step 6' ;;
*) die "unknown test: $t" ;;
esac; done

printf '\n%d runs, %d unexpected\n' "$runs" "$unexpected"
[ "$unexpected" -eq 0 ]

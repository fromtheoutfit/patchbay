#!/usr/bin/env bash
# Negative tests of the verification gate (agent-os/standards/base/process/verification-gate.md,
# "Every step that can fail is proven to fail"). Not run by scripts/gate.sh; gate step 1 parses
# this file. Each test lays a scratch copy of the gate's inputs out as <case>/patchbay in a fresh
# temporary directory, git-inits and git-adds the copy (the gate and the sync script list files
# with git and run only at the top of a work tree), puts a patchbay-standards checkout beside it as
# <case>/patchbay-standards (a symlink to one git clone of ../patchbay-standards made per run,
# which carries every branch and so the pinned commit), breaks the copy in one way, and must fail
# with the named reason and exit status, the steps after it never reached; the positive cases
# beside them must pass. Every run names the status it expects: a mismatch is marked UNEXPECTED
# and the harness exits 1 at the end naming the count, so the transcript's last line says whether
# every case behaved. A setup step that fails stops the harness (exit 2) rather than letting a
# case fail for the wrong reason. Nothing in the tree and nothing in ../patchbay-standards is
# written: the scratch directory is refused unless mktemp made it, outside this repository. The
# transcript of a run is kept in the spec's verification/ folder as gate-negative-tests.txt (every
# test but j) and ci-negative-test.txt (j, the CI replay).
#
# Usage: scripts/gate-negative-tests.sh [test ...]   (default: every test but j; "all" adds j)
#   tests: a b c d e f g u j
#   a  an unparsable script under scripts/: gate.sh stops at step 1, exit 1, step 2 never reached
#   b  one byte appended to a file under agent-os/standards/base/: step 2 names it changed, exit 1
#   c  a hand-edited entry in the base: section of the index: step 2 reports the section, exit 1
#   d  the sibling checkout missing: step 2 names ../patchbay-standards, exit 1
#   e  the copy's scripts/sync-standards.sh edited: step 2 reports the script differs, exit 1
#   f  an untracked .md under agent-os/standards/base/: step 2 names it extra, exit 1
#   g  step 1's file list: an ignored scripts/.DS_Store passes; a tracked non-shell file, a tracked
#      script missing from the disk, and a copy that is not a git work tree each fail by name
#   u  usage: any argument exits 2 with the usage line; the clean copy exits 0
#   j  the CI replay: the run steps of .github/workflows/gate.yml on a clean copy and a broken one
# Needs git, and uv for j (it reads the workflow with pyyaml, through uv run --with, installing
# nothing). Needs ../patchbay-standards beside this repository, as the gate does.
set -uo pipefail
cd "$(dirname "$0")/.."
REPO=$(pwd -P)
die() { echo "harness: $1" >&2; exit 2; }   # die <reason>: a setup failure, not a test result
SIBLING=$(cd "$REPO/../patchbay-standards" 2>/dev/null && pwd -P) ||
  die "../patchbay-standards is missing; the gate and these tests need it beside this repository"
NEG=$(mktemp -d) || die "mktemp -d failed"
[ -n "$NEG" ] && [ -d "$NEG" ] || die "mktemp -d gave no directory"
NEG=$(cd "$NEG" && pwd -P) || die "the scratch directory cannot be entered"
case "$NEG" in
  "$REPO"|"$REPO"/*) die "the scratch directory $NEG is inside this repository; refusing to use it" ;;
esac
trap 'rm -rf "${NEG:?}"' EXIT
git clone -q "$SIBLING" "$NEG/patchbay-standards" || die "could not clone $SIBLING into the scratch directory"

runs=0; unexpected=0
mk() {  # mk <case>: <case>/patchbay, a copy of the gate's inputs, git-added, with the sibling symlinked beside it
  d="$NEG/$1"; rm -rf "$d"; mkdir -p "$d/patchbay/agent-os" || die "mk $1: mkdir"
  cp -R scripts "$d/patchbay/" || die "mk $1: cp scripts"
  cp -R agent-os/standards "$d/patchbay/agent-os/" || die "mk $1: cp standards"
  cp .gitignore "$d/patchbay/" || die "mk $1: cp .gitignore"
  git -c init.defaultBranch=main -C "$d/patchbay" init -q || die "mk $1: git init"
  git -C "$d/patchbay" add -A || die "mk $1: git add"
  ln -s ../patchbay-standards "$d/patchbay-standards" || die "mk $1: ln"
}
run() {  # run <case> <expected status> <cmd...>: run in <case>/patchbay, print its output and status, assert the status
  local c=$1 want=$2 got; shift 2
  ( cd "$NEG/$c/patchbay" && "$@" ) 2>&1 | sed "s#$NEG/\([a-z0-9-]*\)#<copy \1>#g"
  got=${PIPESTATUS[0]}; runs=$((runs + 1))
  if [ "$got" -eq "$want" ]; then echo "exit=$got"
  else echo "exit=$got  UNEXPECTED (expected $want)"; unexpected=$((unexpected + 1)); fi
}
hdr() { printf '\n### %s\n' "$1"; }
note() { printf -- '-- %s\n' "$1"; }
broken() { printf '#!/usr/bin/env bash\nif true; then\n' > "$NEG/$1/patchbay/scripts/broken.sh" || die "broken $1"; }   # broken <case>: an unparsable script in the copy

tests=("$@")
[ "${#tests[@]}" -eq 0 ] && tests=(a b c d e f g u)
[ "${tests[*]}" = all ] && tests=(a b c d e f g u j)

for t in "${tests[@]}"; do case "$t" in
a) hdr "a (unparsable script scripts/broken.sh: gate.sh must fail at step 1 naming it, exit 1, and never print 2/2)"
   mk a; broken a
   run a 1 scripts/gate.sh ;;
b) hdr "b (one byte appended to agent-os/standards/base/process/ownership.md: step 1 passes, step 2 must name it changed, exit 1)"
   mk b; printf 'x' >> "$NEG/b/patchbay/agent-os/standards/base/process/ownership.md" || die "b: append"
   run b 0 git status --short
   run b 1 scripts/gate.sh ;;
c) hdr "c (a description in the base: section of agent-os/standards/index.yml hand-edited: step 2 must report the section differs, exit 1)"
   mk c
   sed -i.bak 's/^    description: A person owns every commit/    description: Hand-edited here/' "$NEG/c/patchbay/agent-os/standards/index.yml" || die "c: sed"
   rm "$NEG/c/patchbay/agent-os/standards/index.yml.bak"
   run c 0 git diff --stat
   run c 1 scripts/gate.sh ;;
d) hdr "d (no checkout at ../patchbay-standards: step 2 must fail naming it, exit 1; the sync script's own status is 2, the gate's is 1)"
   mk d; rm "$NEG/d/patchbay-standards" || die "d: rm symlink"
   note "the sync script alone, for its status:"
   run d 2 scripts/sync-standards.sh --check
   note "the gate:"
   run d 1 scripts/gate.sh ;;
e) hdr "e (a comment appended to the copy's scripts/sync-standards.sh: step 1 passes, step 2 must report the script differs, exit 1)"
   mk e; printf '\n# a hand edit to the synced script\n' >> "$NEG/e/patchbay/scripts/sync-standards.sh" || die "e: append"
   run e 0 git status --short
   run e 1 scripts/gate.sh ;;
f) hdr "f (an untracked agent-os/standards/base/process/extra.md: step 2 must name it extra, exit 1)"
   mk f; printf '# Extra\n\nNot a synced standard.\n' > "$NEG/f/patchbay/agent-os/standards/base/process/extra.md" || die "f: write"
   run f 0 git status --short
   run f 1 scripts/gate.sh ;;
g) hdr "g (step 1 lists files with git: an ignored scripts/.DS_Store passes; a tracked scripts/notes.txt is refused by name; a tracked script deleted from the disk is refused; a copy that is not a git work tree is refused by name)"
   mk g; touch "$NEG/g/patchbay/scripts/.DS_Store" || die "g: touch"
   note "untracked, ignored scripts/.DS_Store present (must pass, exit 0):"
   run g 0 git status --short --ignored scripts
   run g 0 scripts/gate.sh
   printf 'a note\n' > "$NEG/g/patchbay/scripts/notes.txt" || die "g: notes"; git -C "$NEG/g/patchbay" add scripts/notes.txt || die "g: add notes"
   note "scripts/notes.txt tracked, neither .sh nor a bash shebang (must fail at step 1 naming it, exit 1):"
   run g 1 scripts/gate.sh
   git -C "$NEG/g/patchbay" rm -q --cached scripts/notes.txt || die "g: rm notes"; rm "$NEG/g/patchbay/scripts/notes.txt"
   rm "$NEG/g/patchbay/scripts/gate-negative-tests.sh" || die "g: rm harness copy"
   note "scripts/gate-negative-tests.sh tracked but deleted from the disk, deletion not staged (must fail at step 1 naming it, exit 1):"
   run g 0 git status --short scripts
   run g 1 scripts/gate.sh
   git -C "$NEG/g/patchbay" checkout -q -- scripts/gate-negative-tests.sh || die "g: restore"
   rm -rf "$NEG/g/patchbay/.git"
   note "the copy's .git removed (must fail at step 1 by name, exit 1):"
   run g 1 scripts/gate.sh ;;
u) hdr "u (usage: --help and a stray argument each exit 2 with the usage line and run no step; the clean copy exits 0)"
   mk u
   note "clean copy (must pass, exit 0):"
   run u 0 scripts/gate.sh
   note "--help (exit 2):"
   run u 2 scripts/gate.sh --help
   note "a stray argument (exit 2):"
   run u 2 scripts/gate.sh x ;;
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
recorded by run id and conclusion in the spec's verification/ once it exists. The two uses steps
are the checkouts, which the scratch layout stands in for; the second takes the pin step's output
as its ref, and the replay shows the sha the step wrote beside the one in .version.
TXT
   mk j1; mk j2; broken j2
   replay() {  # replay <case> <expected status>: the workflow's steps against $NEG/<case> as the workspace
     local c=$1 want=$2 got
     : > "$NEG/$c/github-output"
     GITHUB_OUTPUT="$NEG/$c/github-output" uv run --quiet --no-project --with pyyaml python -u - "$NEG/$c" .github/workflows/gate.yml <<'PY' 2>&1 | sed "s#$NEG/\([a-z0-9-]*\)#<copy \1>#g"
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
     got=${PIPESTATUS[0]}; runs=$((runs + 1))
     if [ "$got" -eq "$want" ]; then echo "exit=$got"
     else echo "exit=$got  UNEXPECTED (expected $want)"; unexpected=$((unexpected + 1)); fi
   }
   note "the commit pinned in the copy's .version:"
   run j1 0 cat agent-os/standards/base/.version
   note "j1, clean copy (the job must pass):"; replay j1 0
   note "j2, scripts/broken.sh added as in test a (gate.sh fails at step 1, so the job must fail):"; replay j2 1 ;;
*) die "unknown test: $t" ;;
esac; done

printf '\n%d runs, %d unexpected\n' "$runs" "$unexpected"
[ "$unexpected" -eq 0 ]

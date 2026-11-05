#!/usr/bin/env bash
# Negative tests of the verification gate (agent-os/standards/base/process/verification-gate.md,
# "Every step that can fail is proven to fail"). Not run by scripts/gate.sh; gate step 1 parses
# this file. Each test lays a scratch copy of the gate's inputs out as <case>/patchbay in a fresh
# temporary directory, git-inits and git-adds the copy (the sync script runs only at the top of a
# work tree and reads git ls-files), puts a patchbay-standards checkout beside it as
# <case>/patchbay-standards (a symlink to one git clone of ../patchbay-standards made per run,
# which carries every branch and so the pinned commit), breaks the copy in one way, and must fail
# with the named reason and exit status, the steps after it never reached; the positive cases
# beside them must pass. Nothing in the tree and nothing in ../patchbay-standards is written. The
# transcript of a run is kept in the spec's verification/ folder as gate-negative-tests.txt (every
# test but j) and ci-negative-test.txt (j, the CI replay).
#
# Usage: scripts/gate-negative-tests.sh [test ...]   (default: every test but j; "all" adds j)
#   tests: a b c d u j
#   a  an unparsable script under scripts/: gate.sh stops at step 1, exit 1, step 2 never reached
#   b  one byte appended to a file under agent-os/standards/base/: step 2 names it changed, exit 1
#   c  a hand-edited entry in the base: section of the index: step 2 reports the section, exit 1
#   d  the sibling checkout missing: step 2 names ../patchbay-standards, exit 1
#   u  usage: any argument exits 2 with the usage line; the clean copy exits 0
#   j  the CI replay: the run steps of .github/workflows/gate.yml on a clean copy and a broken one
# Needs git, and uv for j (it reads the workflow with pyyaml, through uv run --with, installing
# nothing). Needs ../patchbay-standards beside this repository, as the gate does.
set -uo pipefail
cd "$(dirname "$0")/.."
REPO=$(pwd -P)
SIBLING=$(cd "$REPO/../patchbay-standards" 2>/dev/null && pwd -P) ||
  { echo "../patchbay-standards is missing; the gate and these tests need it beside this repository" >&2; exit 2; }
NEG=$(cd "$(mktemp -d)" && pwd -P)   # physical, as the scripts print it
trap 'rm -rf "$NEG"' EXIT
git clone -q "$SIBLING" "$NEG/patchbay-standards" ||
  { echo "could not clone $SIBLING into the scratch directory" >&2; exit 2; }

mk() {  # mk <case>: <case>/patchbay, a copy of the gate's inputs, git-added, with the sibling symlinked beside it
  d="$NEG/$1"; rm -rf "$d"; mkdir -p "$d/patchbay/agent-os"
  cp -R scripts "$d/patchbay/"
  cp -R agent-os/standards "$d/patchbay/agent-os/"
  cp .gitignore "$d/patchbay/"
  git -c init.defaultBranch=main -C "$d/patchbay" init -q && git -C "$d/patchbay" add -A
  ln -s ../patchbay-standards "$d/patchbay-standards"
}
run() {  # run <case> <cmd...>: run in <case>/patchbay, print its output and exit status, the scratch path masked
  ( cd "$NEG/$1/patchbay" && shift && "$@" ) 2>&1 | sed "s#$NEG/\([a-z0-9-]*\)#<copy \1>#g"
  echo "exit=${PIPESTATUS[0]}"
}
hdr() { printf '\n### %s\n' "$1"; }
note() { printf -- '-- %s\n' "$1"; }
broken() { printf '#!/usr/bin/env bash\nif true; then\n' > "$NEG/$1/patchbay/scripts/broken.sh"; }   # broken <case>: an unparsable script in the copy

tests=("$@")
[ "${#tests[@]}" -eq 0 ] && tests=(a b c d u)
[ "${tests[*]}" = all ] && tests=(a b c d u j)

for t in "${tests[@]}"; do case "$t" in
a) hdr "a (unparsable script scripts/broken.sh: gate.sh must fail at step 1 naming it, exit 1, and never print 2/2)"
   mk a; broken a
   run a scripts/gate.sh ;;
b) hdr "b (one byte appended to agent-os/standards/base/process/ownership.md: step 1 passes, step 2 must name it changed, exit 1)"
   mk b; printf 'x' >> "$NEG/b/patchbay/agent-os/standards/base/process/ownership.md"
   run b git status --short
   run b scripts/gate.sh ;;
c) hdr "c (a description in the base: section of agent-os/standards/index.yml hand-edited: step 2 must report the section differs, exit 1)"
   mk c
   sed -i.bak 's/^    description: A person owns every commit/    description: Hand-edited here/' "$NEG/c/patchbay/agent-os/standards/index.yml"
   rm "$NEG/c/patchbay/agent-os/standards/index.yml.bak"
   run c git diff --stat
   run c scripts/gate.sh ;;
d) hdr "d (no checkout at ../patchbay-standards: step 2 must fail naming it, exit 1; the sync script's own status is 2, the gate's is 1)"
   mk d; rm "$NEG/d/patchbay-standards"
   note "the sync script alone, for its status:"
   run d scripts/sync-standards.sh --check
   note "the gate:"
   run d scripts/gate.sh ;;
u) hdr "u (usage: --help and a stray argument each exit 2 with the usage line and run no step; the clean copy exits 0)"
   mk u
   note "clean copy (must pass, exit 0):"
   run u scripts/gate.sh
   note "--help (exit 2):"
   run u scripts/gate.sh --help
   note "a stray argument (exit 2):"
   run u scripts/gate.sh x ;;
j) hdr "j (CI replay: the run steps of .github/workflows/gate.yml, in order, on a clean copy and on a copy with a broken script)"
   cat <<'TXT'
The workflow is not run on a hosting service here. The job's steps are read from the workflow file
and the run steps executed in order under the scratch directory laid out as the workspace (patchbay/
and patchbay-standards/ side by side, as the two checkout steps leave it), each from the step's
working-directory under the shell GitHub gives a run step on ubuntu (bash --noprofile --norc -eo
pipefail). GitHub's rule: a step that exits non-zero fails the job unless continue-on-error is set,
and this job sets nothing. This replays the job's control flow on this machine's toolchain; it is
not the ubuntu run. The hosted run on the pull request is the proof of the workflow itself,
recorded by run id and conclusion in the spec's verification/ once it exists. The three uses steps
are the two checkouts, which the scratch layout stands in for, and setup-uv pinned to a version;
the uv on PATH here is shown.
TXT
   echo "uv on PATH: $(uv --version)"
   mk j1; mk j2; broken j2
   replay() {  # replay <case>: the workflow's steps against $NEG/<case> as the workspace
     uv run --quiet --no-project --with pyyaml python -u - "$NEG/$1" .github/workflows/gate.yml <<'PY' 2>&1 | sed "s#$NEG/\([a-z0-9-]*\)#<copy \1>#g"
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
    if r.returncode:
        print(f"job: FAILED at step {i} (a run step that exits non-zero fails the job)"); sys.exit(r.returncode)
print("job: passed")
PY
     echo "exit=${PIPESTATUS[0]}"
   }
   note "j1, clean copy (the job must pass):"; replay j1
   note "j2, scripts/broken.sh added as in test a (gate.sh fails at step 1, so the job must fail):"; replay j2 ;;
*) echo "unknown test: $t" >&2; exit 2 ;;
esac; done

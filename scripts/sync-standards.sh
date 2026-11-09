#!/usr/bin/env bash
# Sync the base standards of patchbay-standards into a consuming project, check the project's copy
# for drift, or regenerate the base: section of the project's index alone. The rule is
# base/process/standards-sync.md; this file lives in patchbay-standards and is copied into each
# project as scripts/sync-standards.sh by the sync itself, from the project's pinned commit.
#
# Usage, from the consuming project's root (the top of its git work tree):
#   scripts/sync-standards.sh [--init] [<path-to-patchbay-standards> [<ref>]]   sync
#   scripts/sync-standards.sh --index-only [<path-to-patchbay-standards>]       the base: section alone
#   scripts/sync-standards.sh --check [<path-to-patchbay-standards>]            drift check, writes nothing
# <path> defaults to ../patchbay-standards, the sibling checkout; a path inside a checkout resolves
# to its top. <ref> defaults to the checkout's origin/HEAD, origin's default branch (origin/main),
# so a bare sync pins a pushed, merged commit; a checkout with no origin/HEAD is told to pass a ref,
# and a ref whose commit is not on that branch is synced with a warning naming it. --index-only and
# --check take no ref: they read the commit pinned in agent-os/standards/base/.version. The first
# sync of a project is run from the checkout's copy:
#   ../patchbay-standards/scripts/sync-standards.sh --init
#
# A sync, at the commit <ref> resolves to:
#   - reads base/, index.yml and scripts/sync-standards.sh out of that commit's tree with git
#     ls-tree and git cat-file, raw bytes and never the working tree, so an uncommitted edit, the
#     checkout's line-ending settings and its attributes cannot reach the project
#   - checks every precondition, then builds the new base/ (with .version, the commit as forty hex
#     digits and a newline, the one file under base/ that is not a standard) and the new index in
#     a temporary directory, and only then swaps them in: a refusal (exit 2) leaves the project as
#     it was
#   - replaces agent-os/standards/base/ whole, so a file removed upstream is removed here
#   - replaces the base: section of agent-os/standards/index.yml with the base: section of the
#     commit's index.yml, byte for byte, leaving every other line of the project's index as it
#     was, in place and in order; the file is written beside itself and moved into place. --init
#     creates the section (and the file) for a project syncing for the first time; without --init
#     a missing section is refused
#   - verifies the result against the export (a mismatch exits 1)
#   - copies scripts/sync-standards.sh from the same commit over the project's copy, the last thing
#     it writes, so the project carries the script at its pinned commit and the next sync runs it;
#     the sync that delivers a change to the script is run by the copy before it
#   - then reports what changed on stderr (added, removed, changed files; old and new commit; what
#     the index and the script did) and prints one JSON object on stdout
# --check exports the pinned commit and compares: every file under agent-os/standards/base/ except
# .version, the base: section, and the script. Any difference is drift (exit 1), each named.
# --index-only regenerates the base: section from the pinned commit and touches nothing else.
#
# The base: section of an index is the line `base:` with nothing after the colon, plus every line
# after it that is indented, blank or a column-0 comment, ending at the last indented line: a
# trailing blank or comment line and the next column-0 key belong to the project. A second `base:`
# line, or one with content after the colon, is not a parseable section. --init inserts the section
# before the first column-0 key other than `root:` that sorts after `base` (above the column-0
# comment lines directly over that key, which stay with it), or at the end, with one blank line on
# each side: the blank lines directly above the insertion collapse to that one, and a missing
# final newline is added. The project's files are the tracked ones plus the untracked ones git
# does not ignore, as scripts/check-index.sh reads them, so an ignored stray is never drift. A
# path holding a control character, here or in the commit, is refused, so every list below and
# the JSON hold by construction.
#
# The work-tree root is asked of git: --is-inside-work-tree is true there (it is false in .git/ and
# in a bare repository, where --show-cdup is empty too) and --show-cdup is empty. No paths are
# compared, so a project's root typed in another case, or spelled C:/ rather than /c/, is its root.
#
# Exit status: 0 success; 1 a failed check (drift, or a sync whose result does not match the
# export); 2 usage or a precondition (a bad flag or two mode flags, not at a work-tree root, run
# inside patchbay-standards itself, <path> not a patchbay-standards checkout, no origin/HEAD to
# default to, <ref> not a commit, the pinned commit absent, no parseable base: section here
# without --init or in the commit, a path that is not a regular file or holds a control
# character, a listing of the project's files git could not make). Needs git, cmp, comm, awk, sed.
set -euo pipefail
export LC_ALL=C   # one collation for every sort, comm and awk comparison below

usage() {
  cat <<'TXT'
usage: scripts/sync-standards.sh [--init] [<path-to-patchbay-standards> [<ref>]]
       scripts/sync-standards.sh --index-only [<path-to-patchbay-standards>]
       scripts/sync-standards.sh --check [<path-to-patchbay-standards>]
Run from the consuming project's root. <path> defaults to ../patchbay-standards; <ref> to its origin/HEAD.
TXT
}
die() { echo "FAIL  $2" >&2; exit "$1"; }   # die <status> <reason>
has_control() {  # has_control <string>: 0 when it holds a control character (newline and tab included)
  [ "$(printf '%s' "$1" | tr -d '[:cntrl:]' | wc -c | tr -d ' ')" -ne "$(printf '%s' "$1" | wc -c | tr -d ' ')" ]
}

mode=sync; init=0; path=; ref=
set_mode() { [ "$mode" = sync ] || { usage >&2; die 2 "one mode per run: --$mode and $1 both given"; }; mode=${1#--}; }
while [ $# -gt 0 ]; do
  case "$1" in
    --init) init=1 ;;
    --index-only|--check) set_mode "$1" ;;
    -h|--help) usage; exit 0 ;;
    --*) usage >&2; die 2 "unknown flag $1" ;;
    *) if [ -z "$path" ]; then path=$1
       elif [ -z "$ref" ]; then ref=$1
       else usage >&2; die 2 "too many arguments"; fi ;;
  esac
  shift
done
[ "$mode" = sync ] || [ -z "$ref" ] || { usage >&2; die 2 "--$mode takes no ref; it reads the commit in agent-os/standards/base/.version"; }
[ "$mode" = sync ] || [ "$init" -eq 0 ] || { usage >&2; die 2 "--init is a sync flag"; }
: "${path:=../patchbay-standards}"

# Preconditions, the cheap ones first; nothing is read from the commit until they all hold.
root=$(pwd -P)
if ! inside=$(git rev-parse --is-inside-work-tree 2>/dev/null) || [ "$inside" != true ] ||
   ! cdup=$(git rev-parse --show-cdup 2>/dev/null) || [ -n "$cdup" ]; then   # git says: a work tree, and its top
  die 2 "run from the consuming project's root, the top of its git work tree (here: $root)"
fi
base=agent-os/standards/base
idx=agent-os/standards/index.yml
script=scripts/sync-standards.sh
if [ -L "$base" ]; then
  die 2 "$base is a symlink: this is patchbay-standards itself, not a consuming project"
fi
if ! [ -d "$path" ] || ! up=$(git -C "$path" rev-parse --show-toplevel 2>/dev/null); then
  die 2 "$path is not a git checkout; pass the path to a patchbay-standards checkout"
fi
up=$(cd "$up" && pwd -P)
has_control "$up" && die 2 "the checkout's path holds a control character and is refused"
has_control "$ref" && die 2 "the ref holds a control character and is refused"

# section_bounds <file>: "<first line> <last line>" of the base: section per the rule in the header, or nothing.
# The one walk of the section; extraction and replacement work on the line range it prints.
section_bounds() {
  awk '
    !inbase && /^base:[[:space:]]*$/ { inbase = 1; start = NR; end = NR; next }
    inbase && /^[^[:space:]#]/       { exit }
    inbase && /^[[:space:]]*$/       { next }
    inbase && /^#/                   { next }
    inbase                           { end = NR }
    END                              { if (start) print start, end }
  ' "$1"
}
base_section() {  # base_section <file>: the section's lines, or nothing
  local b
  [ -f "$1" ] || return 0
  b=$(section_bounds "$1"); [ -n "$b" ] || return 0
  awk -v s="${b% *}" -v e="${b#* }" 'NR >= s && NR <= e' "$1"
}
section_state() {  # section_state <file>: "none", "ok" or "unparseable" (a second base: line, or content after the colon)
  local n
  [ -f "$1" ] || { echo none; return; }
  n=$(grep -c '^base:' "$1" || true)
  case "$n" in
    0) echo none ;;
    1) if [ -n "$(section_bounds "$1")" ]; then echo ok; else echo unparseable; fi ;;
    *) echo unparseable ;;
  esac
}
refuse_section() {  # refuse_section <state>: exit 2 naming why the project's index cannot be used
  case "$1" in
    none) die 2 "$idx has no base: section; a first sync passes --init to create it" ;;
    *) die 2 "$idx has a base: line that is not a parseable section (a second base: line, or content after the colon)" ;;
  esac
}
state=$(section_state "$idx")
case "$state" in
  ok) ;;
  none) [ "$mode" = sync ] && [ "$init" -eq 1 ] || refuse_section none ;;
  *) refuse_section "$state" ;;
esac

# The commit: <ref> for a sync, the pinned one otherwise.
if [ "$mode" = sync ]; then
  if [ -z "$ref" ]; then
    ref=$(git -C "$up" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null) ||
      die 2 "no default ref: $up has no origin/HEAD (pass a ref, or set it: git -C $path remote set-head origin --auto)"
  fi
  sha=$(git -C "$up" rev-parse --verify --quiet "$ref^{commit}") || die 2 "$ref is not a commit in $up"
else
  [ -f "$base/.version" ] || die 2 "$base/.version is missing; nothing is pinned (run a sync first)"
  sha=$(tr -d '[:space:]' < "$base/.version")
  printf '%s' "$sha" | grep -Eq '^[0-9a-f]{40}$' || die 2 "$base/.version does not hold a commit: $sha"
  git -C "$up" cat-file -e "$sha^{commit}" 2>/dev/null || die 2 "pinned commit $sha is not in $up (fetch it)"
fi
for p in base index.yml scripts/sync-standards.sh; do
  git -C "$up" cat-file -e "$sha:$p" 2>/dev/null ||
    die 2 "$up is not a patchbay-standards checkout at $sha: $p is missing from that commit"
done
if [ "$mode" = sync ] && default=$(git -C "$up" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null) &&
   ! git -C "$up" merge-base --is-ancestor "$sha" "$default" 2>/dev/null; then
  echo "WARN  $sha is not on $default: a commit not pushed or not merged can be rebased or abandoned, leaving the pin at nothing" >&2
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tab=$(printf '\t')

# The committed base/, index.yml and script under $tmp/export, each blob written raw by git cat-file.
export_commit() {
  local entry meta fmode p
  mkdir -p "$tmp/export/base"
  git -C "$up" ls-tree -r -z "$sha" -- base index.yml scripts/sync-standards.sh > "$tmp/tree"
  while IFS= read -r -d '' entry; do
    meta=${entry%%"$tab"*}; p=${entry#*"$tab"}; fmode=${meta%% *}
    has_control "$p" && die 2 "a path at $sha holds a control character and is refused: $(printf '%q' "$p")"
    case "$fmode" in
      100644|100755) ;;
      *) die 2 "$p at $sha is not a regular file (mode $fmode); base/ holds standards and nothing else" ;;
    esac
    mkdir -p "$tmp/export/$(dirname "$p")"
    git -C "$up" cat-file blob "$sha:$p" > "$tmp/export/$p"
  done < "$tmp/tree"
}
export_commit
state=$(section_state "$tmp/export/index.yml")
[ "$state" = ok ] || die 2 "index.yml at $sha has no parseable base: section (state: $state); nothing written"
base_section "$tmp/export/index.yml" > "$tmp/section.new"

# splice_section <file> <start> <end>: the file with lines start..end replaced by the exported section, on stdout
splice_section() {
  awk -v s="$2" -v e="$3" -v f="$tmp/section.new" '
    NR == s { while ((getline l < f) > 0) print l }
    NR < s || NR > e
  ' "$1"
}
# insertion_point <file>: the line of the first column-0 key other than root: that sorts after base, or of the
# column-0 comment run directly above it; 0 when there is none (the section goes at the end)
insertion_point() {
  awk '
    /^#/            { if (!run) run = NR; next }
    /^[^[:space:]]/ { key = $0; sub(/:.*$/, "", key)
                      if (key != "root" && key > "base") { print (run ? run : NR); found = 1; exit }
                      run = 0; next }
                    { run = 0 }
    END             { if (!found) print 0 }
  ' "$1"
}
# insert_section <file> <at>: the file with the exported section inserted before line <at> (0: at the end), one
# blank line on each side, the blank lines directly above collapsed to that one; on stdout
insert_section() {
  awk -v at="$2" -v f="$tmp/section.new" '
    function flush(  i, l) {
      while (n > 0 && buf[n] ~ /^[[:space:]]*$/) n--
      for (i = 1; i <= n; i++) print buf[i]
      if (n > 0) print ""
      while ((getline l < f) > 0) print l
      done = 1
    }
    !done && (at == 0 || NR < at) { buf[++n] = $0; next }
    !done                         { flush(); print "" }
    { print }
    END { if (!done) flush() }
  ' "$1"
}
# build_index: the project's index with its base: section replaced (or, with --init, created) from the export,
# as $tmp/index.new when it changes; sets index_status to created, replaced or unchanged. Writes nothing.
build_index() {
  local b at
  case "$(section_state "$idx")" in
    ok)
      base_section "$idx" > "$tmp/section.old"
      if cmp -s "$tmp/section.old" "$tmp/section.new"; then index_status=unchanged; return; fi
      b=$(section_bounds "$idx")
      splice_section "$idx" "${b% *}" "${b#* }" > "$tmp/index.new"
      index_status=replaced ;;
    none)
      [ "$init" -eq 1 ] || refuse_section none
      if [ -f "$idx" ]; then at=$(insertion_point "$idx"); insert_section "$idx" "$at" > "$tmp/index.new"
      else insert_section /dev/null 0 > "$tmp/index.new"; fi
      index_status=created ;;
    *) refuse_section unparseable ;;
  esac
}
write_index() {  # $tmp/index.new into place, written beside the index and moved over it
  [ "$index_status" != unchanged ] || return 0
  mkdir -p "$(dirname "$idx")"
  cp "$tmp/index.new" "$idx.new" && mv "$idx.new" "$idx"
}

# project_files: paths under $base relative to it, tracked or untracked-not-ignored, on disk, minus .version; sorted
project_files() {
  local f
  : > "$tmp/have.raw"
  [ -d "$base" ] || return 0
  if ! git -c core.quotePath=false ls-files -z -- "$base" > "$tmp/ls" ||
     ! git -c core.quotePath=false ls-files -z --others --exclude-standard -- "$base" >> "$tmp/ls"; then
    die 2 "git could not list the files under $base (see above)"   # before any write: nothing between this and the verification listing writes .git/index
  fi
  while IFS= read -r -d '' f; do
    [ -f "$f" ] || continue
    has_control "$f" && die 2 "a path under $base holds a control character and is refused: $(printf '%q' "$f")"
    f=${f#"$base"/}; [ "$f" = .version ] && continue
    printf '%s\n' "$f"
  done < "$tmp/ls" > "$tmp/have.raw"
  sort -u "$tmp/have.raw"
}
# compare: the project's base/ against the export; writes $tmp/{added,removed,changed}
# (added = in the export, not the project; removed = in the project, not the export)
compare() {
  local f l
  project_files > "$tmp/have"
  (cd "$tmp/export/base" && find . -type f | sed 's#^\./##') | sort > "$tmp/want"
  for l in have want; do sort -c "$tmp/$l" 2>/dev/null || die 1 "internal: the $l list is not sorted"; done
  comm -13 "$tmp/have" "$tmp/want" > "$tmp/added" || die 1 "internal: comm could not compare the lists"
  comm -23 "$tmp/have" "$tmp/want" > "$tmp/removed" || die 1 "internal: comm could not compare the lists"
  comm -12 "$tmp/have" "$tmp/want" > "$tmp/common" || die 1 "internal: comm could not compare the lists"
  while IFS= read -r f; do cmp -s "$base/$f" "$tmp/export/base/$f" || printf '%s\n' "$f"; done < "$tmp/common" > "$tmp/changed"
}
section_differs() {  # 0 when the project's base: section differs from the export's
  base_section "$idx" > "$tmp/section.have"
  ! cmp -s "$tmp/section.have" "$tmp/section.new"
}

json_str() { printf '"%s"' "$(printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g')"; }   # control-free by the checks above
json_list() {  # json_list <file>: one JSON array of its lines
  local first=1 out="[" f
  while IFS= read -r f; do
    [ "$first" -eq 1 ] || out="$out,"; first=0; out="$out$(json_str "$f")"
  done < "$1"
  printf '%s]' "$out"
}
report_files() {  # report_files <label> <file>: one stderr line per path
  local f
  while IFS= read -r f; do printf '  %-8s %s\n' "$1" "$f" >&2; done < "$2"
}
entries() { grep -c '^  [^[:space:]#]' "$1" || true; }

case "$mode" in
check)
  compare
  if section_differs; then index_status=differs; else index_status=identical; fi
  if ! [ -f "$script" ]; then script_status=missing
  elif cmp -s "$script" "$tmp/export/scripts/sync-standards.sh"; then script_status=matches
  else script_status=differs; fi
  ok=true
  { [ -s "$tmp/added" ] || [ -s "$tmp/removed" ] || [ -s "$tmp/changed" ]; } && ok=false
  [ "$index_status" = identical ] || ok=false
  [ "$script_status" = matches ] || ok=false
  echo "check base standards against $sha  ($up)" >&2
  report_files missing "$tmp/added"
  report_files extra "$tmp/removed"
  report_files changed "$tmp/changed"
  echo "  index    base: section $index_status" >&2
  echo "  script   $script $script_status" >&2
  printf '{"mode":"check","upstream":%s,"commit":"%s","missing":%s,"extra":%s,"changed":%s,"index":"%s","script":"%s","ok":%s}\n' \
    "$(json_str "$up")" "$sha" "$(json_list "$tmp/added")" "$(json_list "$tmp/removed")" "$(json_list "$tmp/changed")" \
    "$index_status" "$script_status" "$ok"
  if [ "$ok" = true ]; then
    echo "ok   $base and the base: section of $idx match patchbay-standards at $sha" >&2; exit 0
  fi
  echo "FAIL  drift from patchbay-standards at $sha (see above)" >&2; exit 1 ;;
index-only)
  build_index
  write_index
  echo "regenerate the base: section of $idx from $sha  ($up)" >&2
  echo "  index    base: section $index_status ($(entries "$tmp/section.new") entries)" >&2
  printf '{"mode":"index-only","upstream":%s,"commit":"%s","index":"%s"}\n' "$(json_str "$up")" "$sha" "$index_status"
  exit 0 ;;
esac

# sync: everything built and checked under $tmp, then swapped in.
old=none; [ -f "$base/.version" ] && old=$(tr -d '[:space:]' < "$base/.version")
compare
for l in added removed changed; do mv "$tmp/$l" "$tmp/$l.pre"; done   # what this sync changes
build_index
mkdir -p "$tmp/new"; cp -R "$tmp/export/base" "$tmp/new/base"   # the export itself stays pristine for the verification
printf '%s\n' "$sha" > "$tmp/new/base/.version"
mkdir -p "$(dirname "$base")"
rm -rf "$base"
mv "$tmp/new/base" "$base"
write_index
compare
if [ -s "$tmp/added" ] || [ -s "$tmp/removed" ] || [ -s "$tmp/changed" ] || section_differs; then
  die 1 "the synced $base or the base: section of $idx does not match the export at $sha"
fi
if ! [ -f "$script" ]; then script_status=installed
elif cmp -s "$script" "$tmp/export/scripts/sync-standards.sh"; then script_status=unchanged
else script_status=updated; fi
if [ "$script_status" != unchanged ]; then
  mkdir -p scripts
  cp "$tmp/export/scripts/sync-standards.sh" "$script.new"; chmod +x "$script.new"
  mv "$script.new" "$script"   # the last write: the running bash keeps its own inode open
fi
echo "sync base standards: $old -> $sha  ($up, ref $ref)" >&2
report_files added "$tmp/added.pre"
report_files removed "$tmp/removed.pre"
report_files changed "$tmp/changed.pre"
echo "  index    base: section $index_status ($(entries "$tmp/section.new") entries)" >&2
echo "  script   $script $script_status" >&2
printf '{"mode":"sync","upstream":%s,"ref":%s,"old":%s,"new":"%s","added":%s,"removed":%s,"changed":%s,"index":"%s","script":"%s"}\n' \
  "$(json_str "$up")" "$(json_str "$ref")" "$([ "$old" = none ] && echo null || json_str "$old")" "$sha" \
  "$(json_list "$tmp/added.pre")" "$(json_list "$tmp/removed.pre")" "$(json_list "$tmp/changed.pre")" "$index_status" "$script_status"
echo "ok   synced to $sha" >&2

# Gate revision after the review of PR 15 — Shaping Notes

Shaped 2026-11-09 in plan mode with this repository's customized `/agent-os:shape-spec`. The owner
answered the Step 1–5 questions and four design questions.

## Core Architecture (Non-Negotiable)

- `base/python/toolchain`, `base/python/layout`, `base/python/typing`, `base/python/models` and
  `base/python/errors` — included without asking (Step 5a); their full text in `standards.md`.

## Scope

The owner's review of PR 15 at `912987a` (the gate spec of issues #12 and #13,
`agent-os/specs/2026-11-09-0802-gate-after-sync-and-event-utc-offset/`): 13 findings, each answered
in `plan.md`'s dispositions table. A gate spec: `scripts/gate.sh`, the harness and
`[tool.pytest.ini_options]` change, each changed step with its negative test and each new guard with
its mutation. On the same branch, so PR 15 carries it. CHANGELOG entry, gate green,
`verification/gate-run.txt`. No stage, commit or push by an agent.

## Shaping answers

- **Step 1, scope:** all 13, in a new spec folder on the same branch, as after the reviews of PRs 3,
  4, 9 and 11; the reviewed spec's folder stays its record.
- **Step 2, visuals:** none.
- **Step 3, references:** `references.md`.
- **Step 4, product context:** no change.
- **Step 5, standards:** the core five, and `process/verification-gate`, `process/standards-sync`,
  `process/standards-retrospective`, `process/ownership`, `python/events`, `testing/tests`. Snapshot
  at `e31f7db` in `standards.md`.

## Decisions

1. **All 13, each reproduced or probed before it is fixed** (`verification/probes.txt`).
2. **Findings 1, 2 and 4: the tools are told which config to read.** `ruff --config pyproject.toml`,
   `mypy --config-file pyproject.toml`, `pytest -c pyproject.toml`. Probed against every config file
   each tool discovers, a nested `ruff.toml` included. Step 5's list of four names goes, so a pin bump
   that adds a name opens nothing.
3. **`-p no:doctest` joins `addopts`.** pytest then reads no `.txt`, and step 5's `test*.txt` arm
   goes. The plan said a later `--doctest-glob` fails loudly; the probe shows otherwise. From
   `addopts` the plugin is unregistered after its options are added, so the option is accepted and
   inert. That still closes finding 4's hazard, since no glob reopens the hole.
4. **A root `uv.toml` is refused by name, tracked or not.** uv has no equivalent flag:
   `--config-file` takes only a `uv.toml`, and `--no-config` would drop `[tool.uv] required-version`.
5. **Finding 3: the claim is corrected, not the code.** The refusal reads the work tree's `.gitignore`
   files, and CI's clean checkout is the one that counts; a local run with an uncommitted edit can
   disagree. The header's sentence changes, ahead of the sibling, named as the one deviation in
   `verification/gate-sh-diff.txt`, and a base proposal corrects the standard's.
6. **Finding 6: the claims soften.** Both answers zero, at the time given. A zone whose offset moves
   answers `None` and is refused every season; a `tzinfo` claiming zero for no instant is taken at
   its word only for the time given.
7. **Finding 7: the refusal reads what the steps read.** Step 2 lists `'*.py' '*.pyi'`, and the
   refusal's pathspec is `scripts '*.py' '*.pyi'`, the union of the gate's listings.
8. **patchbay-standards#27 is revised in place** after the owner approves the proposals, with a
   "Revised" paragraph, its numbers kept, no attribution.
9. **Out of scope:** environment variables (`PYTEST_ADDOPTS`, `UV_*`), and
   `.pre-commit-config.yaml`'s hooks, which are a convenience and not the gate.

## Context

- **Visuals:** None.
- **References:** `references.md`.
- **Product alignment:** N/A.

## Standards Applied

**Core (always applied):**
- `base/python/toolchain`, `base/python/layout`, `base/python/typing`, `base/python/models`,
  `base/python/errors` — Step 5a

**Feature-specific:**
- `process/verification-gate` — the shape of the gate and the negative-test rules
- `process/standards-sync` — the harness's fixture and the sync check it holds
- `process/standards-retrospective` — gate step 9, the probe rule and the route of a base proposal
- `process/ownership` — no stage, commit or push by an agent
- `python/events` — findings 5, 6 and 8
- `testing/tests` — their tests

## Verification Gate

Spec is not complete until `scripts/gate.sh` passes — `bash -n` on every shell script under
`scripts/` as git lists them, with no tracked file a `.gitignore` ignores; `uv sync --locked`, then
`uv run --locked ruff format --check .`, `uv run --locked ruff check .`, `uv run --locked mypy` and
`uv run --locked pytest` under `pyproject.toml`'s `[tool.*]` rule set and `uv.lock`'s pins; and
`scripts/sync-standards.sh --check` against `../patchbay-standards` at the commit in
`agent-os/standards/base/.version` — and the three judgment steps are recorded, in this order: Docs,
Version, then the standards retrospective below.

**Results (2026-11-09):** exit 0 on branch
`task/12-gate-spec-3-take-patchbay-standards-17-19-20-and-21-after-the-sync-that-brings-them-in`,
`verification/gate-run.txt`, the last thing done before hand-over. The gate was green after each of
Tasks 3, 4, 5, 6 and 9, after Tasks 7 and 8 together, and after the comment rewrap. The whole harness
was rerun after the last edit `mk` copies, one run per transcript:
`verification/gate-negative-tests.txt`, 124 runs, 0 unexpected; `verification/ci-negative-test.txt`
(j), 3 runs, 0 unexpected. `verification/guard-mutations.txt`: 12 mutations, each as required, and
each caught for its own reason. `verification/gate-sh-diff.txt`: step lists, pins, paths, the
refusal's pathspec and the one named deviation. `verification/probes.txt`: findings 1, 2, 3 in both
directions, 5 and 7 reproduced at `912987a`, and each flag shown holding where the same file changes
the rules without it.

**Docs (step 7):** checked and reads true after the change:
- `README.md` (the step list's 1 and 5, the paragraph on what the steps read);
- `CLAUDE.md` (the gate sentence, finding 9 among it);
- `.claude/commands/agent-os/shape-spec.md` (the gate task's steps 1 and 5, the steps 2–5 sentence,
  the template paragraph);
- `pyproject.toml` (the header naming `uv.toml`, the `addopts` comment);
- the headers of `scripts/gate.sh` and `scripts/gate-negative-tests.sh`, and the docstring and comment
  of `src/patchbay/events.py`;
- `CHANGELOG.md`: one `### Changed` (finding 10), and the ninth spec's entry where this revision
  superseded it.

The reviewed spec's folder stays as it was recorded, so its `shape.md` describes the gate at
`912987a`.

**Version (step 8):** the tenth spec's entry under `### Changed` in `[Unreleased]`, `CHANGELOG.md`.
The version stays 0.0.1.

## Standards Retrospective

Step 9, always last. Answered from the shipped diff; there are no project standards in this
repository, so every change is a base proposal.

1. **A pattern no standard covers:** two. A tool that discovers its own config is told which file to
   read, and a validator that calls a caller's code asks it inside a `try`. Both below.
2. **A standard wrong or stale:** `verification-gate.md`'s "committed" sentence, and what this
   revision changes in `toolchain.md` and `events.md`. Below.
3. **A deliberate deviation:** one, below.
4. **A pointer moved:** none. Every test and file the standards name is still there.

- **Deviation, not a standard change:** `scripts/gate.sh`'s header says the work tree's `.gitignore`
  files are read, ahead of the sibling's sentence, and `verification/gate-sh-diff.txt` names it. It
  is a comment, and ends when the sync brings the standard's correction.

Proposals sent upstream: fromtheoutfit/patchbay-standards#27, revised in place.

### Standards retrospective (proposed, base)

- `base/process/verification-gate.md`, "The first step makes the forms agree" — "Only committed
  `.gitignore` files count, so every clone of a commit gets the same answer" is false of
  `git ls-files --exclude-per-directory`, which reads the work tree's: the sentence says so, that a
  clean checkout answers from its commit's own, and that an uncommitted edit can make a local run
  disagree with CI. The sibling's `scripts/gate.sh` header and its test y's note follow. Verified
  against `scripts/gate.sh` step 1, test p's two directions and `verification/probes.txt`, finding 3.
  Proposed, not applied; filed as
  fromtheoutfit/patchbay-standards#27.
- `base/process/verification-gate.md`, "Pinned" — a tool that discovers its own config is told which
  file to read, by flag, so a config file beside the manifest or below it, tracked or not, cannot
  replace the rule set, and a refusal by name is not a list to keep in step with a pin; a runner with
  no such flag has its config file refused at the root by name. Verified against `scripts/gate.sh`
  steps 2 to 5, test s and q, and `verification/probes.txt`. Proposed, not applied; filed as
  fromtheoutfit/patchbay-standards#27.
- `base/python/toolchain.md`, "The gate's tool steps", "pyproject.toml is the only config file" and
  "pytest and hypothesis" — the command lines carry the flags; the pytest step's refusal stays `.py`
  files under `tests/` and a root `conftest.py`; "so a tracked file `.gitignore` matches is read"
  goes; `uv.toml` joins the files that do not exist; `addopts` gains `-p no:doctest`. Verified against
  `scripts/gate.sh`, `pyproject.toml` and tests p, q and s. Proposed, not applied; filed as
  fromtheoutfit/patchbay-standards#27.
- `base/python/events.md`, "An event is stamped with the UTC time it was built", and its description
  in the root `index.yml` — both answers zero at the time given; a zone whose offset moves answers
  `None` and is refused every season, and a `tzinfo` claiming zero for no instant is taken at its word
  for that time alone, the sentence that says it is accepted corrected; a zone that cannot say is
  refused. Verified against `src/patchbay/events.py` (`_in_utc`) and `tests/unit/test_events.py`
  (`test_an_event_s_time_is_refused_unless_utc`,
  `test_a_zone_claiming_zero_is_taken_at_its_word_for_the_time_given`). Proposed, not applied; filed as
  fromtheoutfit/patchbay-standards#27.
- `base/python/models.md`, "A validator raises `ValueError`" — a validator that calls a caller's code,
  such as a `tzinfo`, asks it inside a `try` that catches `Exception` and raises `ValueError` from it,
  since pydantic lets any other exception through unwrapped. Verified against
  `src/patchbay/events.py` (`_in_utc`), the same test's "a bare tzinfo", "a zone raising at this
  instant" and "a zone answering an int", and `verification/probes.txt`, finding 5. Proposed, not applied; filed as
  fromtheoutfit/patchbay-standards#27.

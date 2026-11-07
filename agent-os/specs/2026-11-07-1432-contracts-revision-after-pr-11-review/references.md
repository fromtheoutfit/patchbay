# References for the contracts revision after the review of PR 11

The owner named four references at Step 3. No visuals.

## Similar Implementations

### The review itself

- **Location:** fromtheoutfit/patchbay#11, the owner's comment "Review of 6f4e7a8"
  (2026-11-07T19:12:33Z).
- **Relevance:** the scope. It gives 17 findings in three tiers, each with a file and line at
  `6f4e7a8`, and says which ones the reviewer reproduced (1, 2, 3, 5, 6 and 7).
- **Key patterns:** each finding is answered in the dispositions table of `plan.md`. A finding's
  own suggestion is taken where it fits the design. Where it does not, the reason is recorded
  (finding 3).

### The PR 9 revision

- **Location:** `agent-os/specs/2026-11-07-0711-gate-revision-after-pr-9-review/`
- **Relevance:** the precedent for a review answered on the same branch. That spec shaped a new
  folder, probed the design before any edit, and revised the open upstream issue in place
  (patchbay-standards#20) with a "Revised" paragraph.
- **Key patterns:**
  - the dispositions table (# / finding / disposition);
  - probes before edits, with each setup shown before its result;
  - one pointer line added to the spec it revises;
  - the PR body rewritten to the shipped tree.

### The contracts spec's shaping notes

- **Location:** `agent-os/specs/2026-11-07-0806-contracts-models-events-errors-fake/shape.md`
- **Relevance:** every Decision this revision keeps, refines or reverses: strict mode, frozen
  insides, the validation boundary, the UTC stamp, no unsubscribe, and the coded suppressions.
  It also holds the eight base proposals filed as patchbay-standards#21, which the retrospective
  revises.
- **Key patterns:** a departure from an earlier Decision is recorded as a new Decision with the
  owner's answer. The earlier text is never rewritten; it gets one pointer line.

### The contracts spec's probes

- **Location:** `verification/probes.txt` of
  `agent-os/specs/2026-11-07-0806-contracts-models-events-errors-fake/`
- **Relevance:** what pydantic 2.14.3, numpy 2.5.4 and mypy 2.4.1 do where the design rests on
  them. This revision's probes take the same form and pins.
- **Key patterns:** each probe is a scratch script outside the repository, run through the locked
  environment, with its source shown before its output. The cases are chosen to tell the
  competing claims apart, so the refusal sits beside the acceptance.

## The code the revision changes

- `src/patchbay/errors.py`, `models.py`, `events.py`, `contracts.py`, `__init__.py`
- `src/patchbay/testing/fake.py` and `contract_tests.py`
- `tests/unit/`, one test module per source module, and the broken fakes of
  `tests/unit/testing/test_contract_tests.py`, one for each contract test

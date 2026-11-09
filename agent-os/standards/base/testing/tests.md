# Tests

How a test in a patchbay package is written and where it lives, and how the contract suite, the
tests every implementation of a package's protocol runs, is written and proven. Every rule names the
file of a consuming project it is verified against, the test that holds it and the probe a rule
about a tool's behaviour rests on. Written from fromtheoutfit/patchbay at `7471387`, the merge of
its PR 11, whose contracts spec and that spec's revision record each choice as a Decision; the
evidence is in the `verification/` of the spec of issue #21 in `patchbay-standards` and of its
revision after the review of PR 25, patchbay's own probes cited by name and the ones those specs
added by letter. The toolchain spec of issue #4 deferred its test-file rules here.

pytest's and hypothesis's configuration, the `"tests/**"` per-file ignores and mypy's `files` are
`base/python/toolchain.md`'s. Where the `testing` subpackage lives is `base/python/layout.md`'s.

## Test files

- **The tests mirror the source, one test module per module**: `src/<package>/<module>.py` is
  tested by `tests/unit/test_<module>.py`, and `src/<package>/testing/<module>.py` by
  `tests/unit/testing/test_<module>.py`. Two named exceptions: the root `__init__.py` is tested by
  `test_package.py`, its surface and its distribution's metadata, and `test_version.py`, its
  version; `testing/__init__.py`, which holds re-exports alone, has no test module. No two modules
  of the package share a basename (`base/python/layout.md`), so the mirror never gives two test
  modules one name. Verified against `src/patchbay/` and `tests/unit/`.
- **Every module under `tests/` has a basename no other module there has, `conftest.py` included,
  and `tests/` has no `__init__.py`**: `tests/` is a tree pytest collects from `testpaths`, not a
  package, and mypy, given `src` and `tests`, refuses two modules of one name as a duplicate, two
  test files or two `conftest.py` alike, though pytest loads both of the latter. Verified against
  `tests/unit/`, the comment on INP001 in `pyproject.toml`'s per-file ignores, and the gate's mypy
  step; probes n and q.
- **`tests/` holds one `conftest.py` at most, in the directory that holds every test taking its
  fixtures**, the fixtures function-scoped so every test starts fresh: a second is a duplicate
  module to mypy (above). patchbay's is `tests/unit/testing/conftest.py`, whose `bus` and
  `instrument` the contract tests and the fake's tests both take, and there is no other. Verified
  against `tests/unit/testing/conftest.py`, `tests/unit/testing/test_contract_tests.py` and
  `tests/unit/testing/test_fake.py`; probe q.

## Inside a test

- **A test reads the repository's files from pytest's root**, `pytestconfig.rootpath`, the
  directory pytest took its own configuration from, never a path counted up from the test file.
  Verified against `tests/unit/test_version.py` (`test_version_matches_pyproject`).
- **A property test's strategy generates only inputs the property holds of, and a known
  counterexample is pinned with `@example`**, so it is tried on every run, not only when the search
  finds it. Verified against `tests/unit/test_version.py`
  (`test_release_pattern_rejects_a_non_numeric_segment`, its strategy filtered and its `@example`
  the Arabic-Indic ten) and `tests/unit/test_models.py` (`_FINITE`).
- **A pattern a value is held to spells its digits `[0-9]`, never `\d`**, which matches any Unicode
  decimal digit, ARABIC-INDIC DIGIT ONE among them; and a character ruff finds confusable is
  written as its escape, as RUF001 (in a string) and RUF003 (in a comment) ask, the rules kept:
  each reports the character itself and neither its escape. Verified against
  `tests/unit/test_version.py` (`_RELEASE` and its comment); probes f (o1), o (the character) and
  p (its escape).
- **A test that holds a refusal mypy must keep making carries a coded `# type: ignore[<code>]` on
  the refused line**, and strict's `warn_unused_ignores` fails the gate the day mypy stops refusing
  and the ignore suppresses nothing (`base/python/toolchain.md`, "mypy"). patchbay's tests hold six:
  a `PresetKey` where a `ParameterId` is expected (`arg-type`); `issubclass` of `Instrument`
  (`misc`); an assignment to a frozen model (`misc`); an assignment to a frozen event (`misc`); an
  item assigned into a `Patch`'s mapping (`index`); and a subscription of types mypy refuses
  (`call-overload`). Verified
  against `tests/unit/test_models.py` (`test_a_preset_key_is_not_a_parameter_id`,
  `test_a_frozen_model_is_unchanged_by_a_refused_assignment`, `test_a_patch_s_mappings_are_read_only`),
  `tests/unit/test_contracts.py` (`test_issubclass_is_refused_for_a_protocol_with_a_data_member`)
  and `tests/unit/test_events.py` (`test_an_event_is_frozen`, `_subscribe_unchecked`); probe c.

## The contract suite

- **The contract tests ship in the package that defines the protocol, in its `testing`
  subpackage, as plain functions `<property>(instrument, bus) -> None`**, taking an instrument that
  publishes on `bus`, both fresh for the test, and listed once in one tuple a consumer
  parametrizes over: patchbay's `CONTRACT_TESTS`, typed `tuple[ContractTest, ...]`, run as
  `@pytest.mark.parametrize("contract_test", CONTRACT_TESTS, ids=lambda test: test.__name__)`.
  Verified against `src/patchbay/testing/contract_tests.py` and
  `tests/unit/testing/test_contract_tests.py` (`test_contract`).
- **No contract test's name starts with `test_`**, so pytest never collects one a consumer imports
  by name: it runs from the tuple, once. Each docstring is imperative, "Check that ...", as ruff's
  D401 asks once the prefix that waived it is gone. Verified against
  `src/patchbay/testing/contract_tests.py` and `tests/unit/testing/test_contract_tests.py`
  (`test_the_contract_tests_are_never_collected_by_pytest`); probes e and b.
- **A contract test fails with an `AssertionError` subclass carrying fields**, patchbay's
  `ContractViolationError(test, expected, actual)`, its message built from them
  (`base/python/errors.md`): a failed assertion to pytest. It never uses `assert`, which
  `python -O` strips, and never imports pytest, a development dependency an installed package
  cannot count on. An exception the test does not expect propagates as itself. Verified against
  `src/patchbay/testing/contract_tests.py`, `src/patchbay/testing/__init__.py` and
  `tests/unit/testing/test_contract_tests.py`
  (`test_a_contract_violation_is_an_assertion_error_with_fields`); probe d.
- **Each contract test works out what it expects from the instrument's parameters and the contract
  alone**, never from an implementation's code. Values are set at a parameter's bounds, so an
  instrument that stores what it is given gets back exactly that; a value past a bound is the next
  float beyond it, `math.nextafter`, since at 2**53 and at the largest float `bound + 1.0` is the
  bound itself, and a bound with no finite float beyond it gets no candidate there. A ratio's
  candidates stay in `[0, 1]`, and a choice or a boolean adds `minimum + 0.5`. Verified against
  `src/patchbay/testing/contract_tests.py` (`_other_value`, `_out_of_range`) and
  `tests/unit/testing/test_contract_tests.py`
  (`test_a_correct_instrument_with_the_widest_bounds_passes`); probes f (f1) and `mutations.py`.
- **Each contract test is proven by the reference implementation broken its way**, and the proof
  asserts the reason the test gives, not only that it fails: the violation names the test, and its
  `expected` starts with the reason. A test holds the table of broken implementations to the
  suite, each contract test once and nothing else. Verified against
  `tests/unit/testing/test_contract_tests.py` (`test_every_contract_test_has_a_broken_fake`,
  `test_each_contract_test_catches_its_broken_fake`).
- **A correct implementation at the edges passes every contract test**: patchbay's reference fake,
  widened through its `parameters()` with one parameter up to 2**53 and one over every finite
  float. Put back to the arithmetic it replaced, `bound + 1.0`, two contract tests fail it with "no
  exception". Verified against `tests/unit/testing/test_contract_tests.py` (`_WideRange`,
  `test_a_correct_instrument_with_the_widest_bounds_passes`); probe `mutations.py`.
- **The suite holds the protocol's promises, a refusal's among them**: a call the instrument
  refuses changes nothing and publishes nothing; a call it carries out publishes its event once; a
  patch bad only at its last entry in key order is refused whole, changing and publishing nothing,
  which catches an implementation that loads one value at a time; and a render no implementation
  could produce raises the package's render error, never a built-in exception or exhausted
  memory. Verified against `src/patchbay/testing/contract_tests.py`
  (`a_patch_refused_part_way_changes_nothing`, `an_impossible_render_raises_render_failed`, and
  the eleven beside them) and `tests/unit/testing/test_contract_tests.py` (`_LoadsUntilARefusal`,
  `_RendersAnyLength`).
- **The suite runs with function-scoped `bus` and `instrument` fixtures in the `conftest.py` beside
  the tests that run it**, the instrument built on the bus, and runs unchanged against whatever
  instrument the fixture returns. Verified against `tests/unit/testing/conftest.py` and
  `tests/unit/testing/test_contract_tests.py` (`test_contract`).

## In this repository

This repository has no package, so this standard does not apply here; Step 5b of its `shape-spec.md`
leaves it out.

## In a consuming project

Synced in as `agent-os/standards/base/testing/tests.md`, its rules the project's, verified against
the project's own files; Step 5b surfaces it from the index for a spec that writes or changes a
test.

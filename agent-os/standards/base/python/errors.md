# Errors

A patchbay package reports every failure as an exception of its own, carrying the fields that say
what failed. This standard says how the package's exceptions are arranged, what each carries and
what may leave a public method. Every rule names the file of a consuming project it is verified
against, the test that holds it and the probe a rule about a tool's behaviour rests on. Written from
fromtheoutfit/patchbay at `7471387`, the merge of its PR 11, whose contracts spec and that spec's
revision record each choice as a Decision; the evidence is in the `verification/` of the spec of
issue #21 in `patchbay-standards` and of its revision after the review of PR 25, patchbay's own
probes cited by name and the ones those specs added by letter.

Where a model's refusal comes from is `base/python/models.md`'s, and what the event bus raises and
lets through is `base/python/events.md`'s; this standard names both and restates neither.

## One root

- **A package's exceptions have one root, and every exception the package raises derives from
  it**: patchbay's `PatchbayError`, so a caller catches every failure the package reports with one
  `except`. The root derives from `Exception`, and no exception's MRO holds a built-in narrower
  than `Exception`, so a caller's `except ValueError` or `except KeyError` never catches the
  package's error by accident: `PatchbayValidationError` is not a `ValueError`, though the pydantic
  error it stands in for is. The one exception is the contract suite's violation,
  `ContractViolationError`, an `AssertionError`: it is a failed assertion to pytest, raised by a
  test and never by the package's API (`base/testing/tests.md`). Verified against
  `src/patchbay/errors.py`, `src/patchbay/testing/contract_tests.py` and
  `tests/unit/test_errors.py` (`test_error_is_a_patchbay_error_and_no_builtin_subtype`).
- **Every exception's name ends in `Error`**, the root's included, as ruff's N818 asks under
  `select = ["ALL"]`. Verified against `src/patchbay/errors.py`,
  `src/patchbay/testing/contract_tests.py` and `pyproject.toml` (`[tool.ruff.lint]`, whose ignore
  list does not hold N818); probe j.

## Fields and messages

- **An error takes its fields as constructor arguments, keeps each as an attribute of the same
  name, and passes them to `Exception.__init__` in the same order**, so `args` holds them, and
  `copy` and pickling, which rebuild an exception by calling its class with its `args`, rebuild it.
  An error that passed a message instead cannot be copied or unpickled. Its message is `__str__`,
  built from the fields. The root takes no fields. Verified against `src/patchbay/errors.py` and
  `tests/unit/test_errors.py` (`test_fields_are_attributes`, `test_error_is_rebuilt_from_its_args`,
  `test_message_is_built_from_the_fields`); probe f (f3).
- **A field is typed as the plain value it is**: an id or a unit as `str`, a bound or a value as
  `float`. The errors module then imports nothing from its own package, and every other module can
  import it: it is the leaf the package's modules are built up from (`base/python/layout.md`). A
  third party's type a field carries is imported from the package that defines it, which the
  manifest declares: `PatchbayValidationError.details` holds pydantic-core's `ErrorDetails`, which
  pydantic does not re-export (`base/python/toolchain.md`, "Dependencies"). Verified against
  `src/patchbay/errors.py`, whose one import is `pydantic_core`, and `pyproject.toml`
  (`[project] dependencies`); probe f (f2).
- **No field takes the name of a third party's method on the error it stands in for.** A
  validation error's refusals are `.details`: pydantic's `ValidationError.errors` is a method, and
  a tuple of that name fails code ported from it with "'tuple' object is not callable", where a
  missing attribute fails it by name. A failure that carries exceptions holds them as
  `.exceptions`, the name `ExceptionGroup` gives them. Verified against `src/patchbay/errors.py`
  and `tests/unit/test_errors.py` (`test_no_field_is_named_like_pydantic_s_errors_method`); probe
  f (f2).

## What escapes

- **No built-in exception leaves a public method.** A lookup that fails is the package's not-found
  error, `ParameterNotFoundError(parameter_id, instrument)`, never `KeyError`; a value a parameter
  does not take is `ValueOutOfRangeError` or `UnitMismatchError`, never `ValueError`; a refused
  model input is the package's validation error (`base/python/models.md`). Two named exceptions,
  each passing an exception the package did not raise: validation pydantic runs on behalf of
  something else raises pydantic's error (`base/python/models.md`), and a `BaseException` that is
  not an `Exception` passes through the bus where a subscriber raised it
  (`base/python/events.md`). Verified against `src/patchbay/errors.py`,
  `src/patchbay/testing/fake.py` (`_parameter`), `src/patchbay/testing/contract_tests.py`
  (`an_unknown_id_raises_parameter_not_found`, `a_value_out_of_range_raises_value_out_of_range`)
  and `tests/unit/testing/test_fake.py`
  (`test_get_of_an_unknown_id_names_the_id_and_the_instrument`).
- **An error raised in place of another is chained from it**, `raise ... from error`, so the cause
  stays on `__cause__`: the validation error from pydantic's, the JSON-data refusal from `json`'s,
  the bus's failure from the first subscriber's exception, a refused patch from the check that
  refused it. The one exception is `from None` where the replaced error is the lookup's own
  `KeyError`, which says nothing the not-found error does not. An error with no cause, a patch for
  another instrument, is raised plainly. Verified against `src/patchbay/models.py`,
  `src/patchbay/events.py`, `src/patchbay/testing/fake.py` (`_parameter`, `_check_whole`),
  `tests/unit/test_models.py` (`test_every_entry_point_refuses_with_patchbay_validation_error`,
  `test_from_json_data_refuses_data_json_cannot_hold`) and `tests/unit/test_events.py`
  (`test_a_failing_subscriber_hides_the_event_from_no_other`).

## In this repository

This repository has no package, so this standard does not apply here; its `shape-spec.md` lists it
in Step 5a for consuming projects.

## In a consuming project

Synced in as `agent-os/standards/base/python/errors.md`, its rules the project's, verified against
the project's own files; Step 5a includes it in every spec, with its full content in that spec's
`standards.md`.

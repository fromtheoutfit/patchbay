# Models

Every value that crosses a patchbay package's boundary is a pydantic model on one base. This
standard says what that base guarantees and how each guarantee is kept: frozen, closed, finite and
strict, refusing as the package, read-only inside, and computing alike. Every rule names the file of
a consuming project it is verified against, the test that holds it and the probe a rule about a
tool's behaviour rests on. Written from fromtheoutfit/patchbay at `7471387`, the merge of its PR 11,
whose contracts spec and that spec's revision record each choice as a Decision; the evidence is in
the `verification/` of the spec of issue #21 in `patchbay-standards` and of its revision after the
review of PR 25, patchbay's own probes cited by name and the ones those specs added by letter.

How mypy reads a model's frozenness is here; the type system's other rules, the future import a
model's module never carries among them, are `base/python/typing.md`'s. What the package's errors
are, and what escapes them, is `base/python/errors.md`'s; an event is a model with rules of its own
in `base/python/events.md`.

## One base

- **Every model derives from one public base, the package's own**: patchbay's `PatchbayModel`, in
  `models.py` and in the root's `__all__`, from which every model and every event derives. A model
  that derives from it has every guarantee below, whichever module defines it. Verified against
  `src/patchbay/models.py`, `src/patchbay/events.py`, `src/patchbay/__init__.py` and
  `tests/unit/test_models.py` (`test_a_model_on_patchbay_model_refuses_as_patchbay_at_any_depth`).
- **The base is frozen by the class keyword `frozen=True`, and every subclass writes the keyword
  again on its class line.** mypy, with no pydantic plugin loaded (`[tool.mypy]` names none), reads
  frozen from the keyword and not from `model_config`: given the keyword it refuses an assignment
  to a field and a subclass that leaves the keyword out ("Non-frozen dataclass cannot inherit from
  a frozen dataclass"); given `model_config` alone it accepts an assignment pydantic refuses at
  runtime. The class keyword and `model_config` merge at runtime. There is no exception: every
  event's class line carries it too. Verified against `src/patchbay/models.py` and
  `src/patchbay/events.py` (every class line), `pyproject.toml` (`[tool.mypy]`),
  `tests/unit/test_models.py` (`test_a_frozen_model_is_unchanged_by_a_refused_assignment`) and
  `tests/unit/test_events.py` (`test_an_event_is_frozen`), each holding mypy's refusal with a coded
  ignore; probes `typing_probe.py` C and D, `frozen_kw.py`, `frozen_kw2.py` and `config_form.py`.
- **The base's `model_config` is closed, finite and strict**: `extra="forbid"`,
  `allow_inf_nan=False` and `strict=True`. A field the model does not declare, NaN and an infinity
  are refused, and no value is converted from another type: `"0.5"` is not 0.5, `1` is not `True`,
  a list is not a tuple and a `str` is not an enum. Strict admits three things, by pydantic's
  design: an int for a float; a dict for a nested model, every field inside it validated by the
  nested model's own config, so as strictly where the nested model is on the base too, and laxly
  where it is not, strict outside or not; and `model_validate_strings`, whose purpose is parsing
  strings. Every model a model holds is on the base, so strict holds at every depth. A model's own
  `model_config` adds to the base's and relaxes none of it: patchbay's `Patch` adds base64 for
  bytes, `RenderResult` arbitrary types for its array. Verified against `src/patchbay/models.py`
  and `tests/unit/test_models.py` (`test_every_entry_point_refuses_with_patchbay_validation_error`,
  `test_strict_refuses_a_conversion`, `test_strict_admits_an_int_for_a_float_and_json_forms`);
  probes `runtime.py` 5, `strict_nested.py` (1, strict inside; 2, a lax model inside a strict one
  admitting `'0.5'`) and `config_form.py`.

## Refusing as the package

- **A model's own entry points refuse with the package's validation error, chained from
  pydantic's.** The constructor, `model_validate`, `model_validate_json` (bad JSON included),
  `model_validate_strings`, the JSON-data entry point below, assignment and deletion each raise
  `PatchbayValidationError` from pydantic's `ValidationError`, which is a `ValueError` and so never
  escapes as one (`base/python/errors.md`). Verified against `src/patchbay/models.py`
  (`_refusals`) and `tests/unit/test_models.py`
  (`test_every_entry_point_refuses_with_patchbay_validation_error`); probe `runtime.py` 6.
- **Validation pydantic runs on behalf of something else is that thing's, and raises pydantic's
  error**: a `TypeAdapter` over a model, or a plain `BaseModel` that holds one as a field. A model
  that derives from the base is not something else: it refuses as the package at any depth.
  `model_copy(update=...)` validates nothing and is not a way in. No hook covers every path:
  pydantic-core collects a `ValueError` raised inside a validator, with its path, beside the outer
  model's own refusals, and lets any other exception through unwrapped, which ends the outer
  validation at the first nested refusal and loses the outer path and the outer refusals. So the
  package's error is raised around the entry points, never from inside a validator. Verified
  against `src/patchbay/models.py` (its docstring) and `tests/unit/test_models.py`
  (`test_validation_run_for_something_else_raises_pydantic_s_error`,
  `test_a_model_on_patchbay_model_refuses_as_patchbay_at_any_depth`); probe a (a1, a2, a5).
- **A validator raises `ValueError`**, which pydantic collects with the field's path; a validator
  that calls code raising the package's error catches it and raises `ValueError` from it
  (patchbay's `Parameter._default_is_a_value`). Verified against `src/patchbay/models.py`,
  `src/patchbay/events.py` and `tests/unit/test_models.py`
  (`test_a_parameter_that_does_not_hold_together_is_refused`); probe a (a1).
- **pydantic's validating classmethods are wrapped, never restated.** In the base, under
  `if not TYPE_CHECKING:`, each of `model_validate`, `model_validate_json` and
  `model_validate_strings` is `classmethod(_refusing(BaseModel.<name>.__func__))`, where
  `_refusing[**P, R]` is a `functools.wraps` decorator that raises a refusal as the package's
  error. mypy, which skips the block, checks every call against pydantic's own `Self`-typed
  signatures, so a misspelled keyword is a type error; at runtime the wrapper forwards whatever it
  is given, so a keyword a later pydantic adds reaches pydantic, and `inspect.signature` of each
  equals pydantic's. Nothing is copied, so ruff's PLR0913 has no case (`base/python/toolchain.md`,
  "ruff"). Verified against `src/patchbay/models.py` and `tests/unit/test_models.py`
  (`test_the_validating_classmethods_keep_pydantic_s_signatures`,
  `test_a_keyword_reaches_pydantic_through_the_wrapper`); probes `footing.py` A and
  `footing_typing.py`.
- **The base's own `__init__` carries pydantic's base-init marker**,
  `__pydantic_base_init__ = True`, with its coded `# type: ignore[attr-defined]` and the reason in
  the comment above it. The override validates exactly what `BaseModel.__init__` does. Without the
  marker, pydantic builds a nested model by calling that `__init__` with the parsed input in Python
  mode: strict then refuses a valid JSON enum string one level down, and a nested refusal escapes
  the outer validation without the outer path or the outer refusals. Verified against
  `src/patchbay/models.py` and `tests/unit/test_models.py`
  (`test_a_patch_round_trips_through_json_byte_for_byte`); probes `models_init.py` and a (a3, a4).

## Python input and JSON data

- **Python input is Python's types, strictly; data in JSON's form goes through one entry point on
  the base**, patchbay's `from_json_data(data)`, for what `json.loads`, a YAML or a TOML parser
  gives. It validates `json.dumps(data)` with `model_validate_json`, so the data meets pydantic's
  JSON rules exactly: an enum by its value, bytes as base64 where the model reads them so, a time
  as an ISO string, an array for a tuple. Strict still refuses `"0.5"` for a float, `1` for `True`
  and NaN. A value JSON cannot hold, a set, a `datetime` or a circular reference, is refused as the
  package's error with one detail at the root, chained from `json`'s `TypeError` or `ValueError`.
  The name keeps out of pydantic's `model_` namespace, where a later pydantic method could land.
  Verified against `src/patchbay/models.py`, `tests/unit/test_models.py`
  (`test_from_json_data_takes_json_s_own_forms`, `test_from_json_data_is_still_strict`,
  `test_from_json_data_refuses_data_json_cannot_hold`, `test_a_patch_comes_back_from_its_json_data`)
  and `tests/unit/test_events.py` (`test_an_event_comes_back_from_its_json_data`); probe
  `footing.py` E.

## Frozen inside

- **A mapping field is sorted by key and held as a `MappingProxyType`**, by an after-validator,
  with a wrap serializer that hands pydantic a plain dict: pydantic validates a `Mapping` to a
  `dict` that a frozen model still lets anyone change, and cannot serialize a proxy without the
  serializer. The same model then writes the same JSON whatever order it was built in. Verified
  against `src/patchbay/models.py` (`Patch`) and `tests/unit/test_models.py`
  (`test_a_patch_s_mappings_are_read_only`, `test_a_patch_has_one_json_whatever_order_it_was_built_in`);
  probe `runtime.py` 1 and 2.
- **An array field is copied, marked unwriteable, and checked for its dtype, its shape and finite
  values**, an arbitrary-type field being only an `isinstance` check; and the model defines `__eq__`
  with `np.array_equal`, since `==` on two arrays has no truth value. Verified against
  `src/patchbay/models.py` (`RenderResult`) and `tests/unit/test_models.py`
  (`test_a_render_result_holds_a_read_only_copy`, `test_a_render_result_refuses_audio_of_another_shape`,
  `test_a_render_result_refuses_audio_that_is_not_finite`, `test_render_results_compare_by_their_arrays`);
  probe `runtime.py` 4.
- **A model that cannot be hashed says so the way Python does**, `__hash__: ClassVar[None] = None`,
  with its coded `# type: ignore[assignment]` and the reason in the comment above it: pydantic's
  frozen hash would raise on a mapping or an array from inside. Verified against
  `src/patchbay/models.py` (`Patch`, `RenderResult`) and `tests/unit/test_models.py`
  (`test_a_patch_is_not_hashable`, `test_a_render_result_is_not_hashable`); probe `runtime.py` 1
  and 4.
- **Bytes go into JSON as base64** (`ser_json_bytes` and `val_json_bytes`), since pydantic's default,
  UTF-8, fails on bytes that are not text. Verified against `src/patchbay/models.py` (`Patch`) and
  `tests/unit/test_models.py` (`test_a_patch_round_trips_through_json_byte_for_byte`); probe
  `runtime.py` 3.
- **An id is non-empty wherever it appears**, a mapping's key included, written
  `Annotated[ParameterId, Field(min_length=1)]` where a field's `Field` cannot reach it. Verified
  against `src/patchbay/models.py`, `src/patchbay/events.py`, `tests/unit/test_models.py`
  (`test_a_patch_s_parameter_ids_are_not_empty`) and `tests/unit/test_events.py`
  (`test_a_changed_parameter_is_named`); probe `footing.py` D.

## Computing alike

- **A quantity every implementation must compute alike is one method on the model, in exact
  arithmetic**, so it is an int for every valid input, never an overflow or an infinity: patchbay's
  `RenderRequest.samples(pattern)`, the length of every render, and `sample_at(pattern, beat)`,
  where a note falls, each in `fractions.Fraction` and rounded half to even. An implementation
  calls the method and never restates the formula. A float derived from one divides an int by an
  int (`RenderResult.audio_seconds`), which Python rounds correctly and which overflows only where
  the quotient passes the largest float, as an array's length over a positive rate never does.
  Verified against
  `src/patchbay/models.py`, `src/patchbay/testing/fake.py` and
  `src/patchbay/testing/contract_tests.py`, which call them, and `tests/unit/test_models.py`
  (`test_samples_is_an_int_however_long_the_render`, `test_samples_rounds_half_to_even`,
  `test_sample_at_places_a_beat_by_the_rule_that_fixes_the_length`,
  `test_sample_at_is_an_int_at_any_tempo`, `test_audio_seconds_holds_at_any_rate`); probes
  `footing.py` B and s.

## In this repository

This repository has no package, so this standard does not apply here; its `shape-spec.md` lists it
in Step 5a for consuming projects.

## In a consuming project

Synced in as `agent-os/standards/base/python/models.md`, its rules the project's, verified against
the project's own files; Step 5a includes it in every spec, with its full content in that spec's
`standards.md`.

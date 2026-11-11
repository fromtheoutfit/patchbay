# References for issue #18: Instrument.get returns the value the parameter holds nearest the one given

## Similar Implementations

### The contract tests that set and read values

- **Location:** `src/patchbay/testing/contract_tests.py`: `_other_value` (lines 100-103),
  `get_after_set_returns_what_was_set` (145-153), `set_emits_parameter_changed_once` (295-310),
  `patch_round_trips_through_load_patch` (211-226), `_out_of_range` (106-122)
- **Relevance:** what the wording is verified against. `_other_value` returns a bound, always
  (`parameter.maximum if current.value != parameter.maximum else parameter.minimum`), and the two
  tests that read a value back after a set require it exactly: `got == value`, and the event's
  `new` equal to the bound given. Every other value the suite gives is refused.
- **Key patterns:** the suite holds only what every instrument holds exactly; `_out_of_range`
  adds `minimum + 0.5` for a choice or a boolean alone, so no continuous parameter is given a
  value between its bounds.

### What a parameter takes

- **Location:** `src/patchbay/models.py`, `Parameter` and `Parameter.check` (lines 181-207)
- **Relevance:** a continuous parameter takes any value in `[minimum, maximum]`
  (`whole = self.kind == "continuous" or value.value.is_integer()`); "takes" is what `set`
  refuses or not, "holds" what `get` returns.

### The event a set publishes

- **Location:** `src/patchbay/events.py`, `ParameterChanged` (line 93: "the value it had and the
  value it has now")
- **Relevance:** `new` is the value held after the set, which `set`'s docstring now says.

### The reference implementation

- **Location:** `src/patchbay/testing/fake.py`, `FakeInstrument.get`, `.set` and the module
  docstring
- **Relevance:** the exact case: it stores the value given and publishes `new=value`, so the value
  it holds nearest the one given is the one given.

### patchbay-vital, the first real instrument (read-only)

- **Location:** `../patchbay-vital`, branch
  `feature/7-the-host-and-the-parameter-map-load-vital-through-pedalboard-map-all-903-parameters-to-preset-keys-and-pass-cores-contract-tests-as-a-real-instrument`
  at `84b5ae7`: `src/patchbay_vital/parameters.py` (`_round_half_away`, lines 62-68;
  `NormalizedScale`, 79-123; `to_preset`, 236-250) and `src/patchbay_vital/census.py:22-24`
- **Relevance:** an indexed scale that is neither a boolean nor a named choice is mapped as
  `continuous`, between whole ends, rounded a half away from zero, and its grid lands on halves;
  a display value is inverted through the curve and rounded to float32 on the normalized scale,
  which is affine to the preset's, not in the display's unit.
- **Key patterns:** "nearest as the instrument measures it", and the tie.

### The evidence the issue cites

- **Location:** `../patchbay-vital/agent-os/specs/2026-11-09-1907-the-host-and-the-parameter-map/verification/probes.txt`,
  "probe 4: get after set" (output at its lines 603-609)
- **Relevance:** P0, every bound recovered; P1, P1', P3 and P4, every held value exact; P2, no
  arbitrary display value exact. Nothing there measures nearness.

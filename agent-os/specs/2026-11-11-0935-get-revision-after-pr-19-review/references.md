# References for the revision of issue #18's spec after the first review of PR 19

## Similar Implementations

### The review itself

- **Location:** the comment on fromtheoutfit/patchbay#19 of 2026-11-11 14:06 UTC, "Review of
  6506e1d", 21 findings
- **Relevance:** the scope; `plan.md`'s dispositions number them in its order.

### A revision after a review

- **Location:** `agent-os/specs/2026-11-09-0900-gate-revision-after-pr-15-review/`
- **Relevance:** a new folder on the reviewed branch, the reviewed folder left as its record, a
  dispositions table, every finding reproduced or probed, and the upstream issue (there #27)
  revised in place with a "Revised" paragraph, its numbers kept.

### A correct instrument at the edges

- **Location:** `tests/unit/testing/test_contract_tests.py`, `_WideRange` and
  `test_a_correct_instrument_with_the_widest_bounds_passes`
- **Relevance:** the shape of the new finite-resolution fake and its test: a `FakeInstrument`
  subclass in the test module, widened through `parameters()`, run against every contract test.

### What patchbay-vital holds after a set (read-only, `84b5ae7`)

- **Location:** `../patchbay-vital/src/patchbay_vital/parameters.py`:
  - `DisplayCurve.to_preset` (169-171): the displayed value inverted through the curve and rounded
    to float32, the first rounding;
  - `NormalizedScale.to_normalized` (105-111): that preset value rounded to float32 on the
    normalized scale, the second; `NormalizedScale.to_preset` (100-103) is the plugin's `fma32`
    back;
  - `MappedParameter.to_preset` (234-250), `to_normalized` (252-257) and `from_normalized`
    (259-266).
- **Location:** `../patchbay-vital/src/patchbay_vital/host.py:361-377`: `VitalHost.get` and `set`
  read and write the normalized value through pedalboard's `raw_value`.
- **Relevance:** the path a value takes, which rounds twice (findings 1 and 6), and the readings of
  the floor probe (finding 2).

### The evidence for "a value `get` has returned comes back"

- **Location:** `../patchbay-vital/tests/unit/test_parameters.py`:
  `test_a_value_the_parameter_holds_comes_back_exactly` (a held normalized value's display comes
  back exactly, its preset value too but where `volume`'s offset absorbs it) and
  `test_where_volume_s_offset_absorbs_a_preset` (at 2**-43 two preset values share a display)
- **Location:** `../patchbay-vital/agent-os/specs/2026-11-09-1907-the-host-and-the-parameter-map/`:
  `verification/probes.txt` probe 4 (output at its lines 603-609), and `shape.md` Decision 6
  (line 71), whose "every value comes back exactly" its retrospective corrected at `volume`'s floor
  (line 263)
- **Relevance:** what the issue cites, and where it stops (finding 2).

### Out-of-range values in shipped presets

- **Location:** the comment on fromtheoutfit/patchbay-vital#8 of 2026-11-10, "Out-of-range preset
  values": `flanger_dry_wet` 0.7072 against the host's 0..0.5 in 26 presets, among others
- **Relevance:** findings 2 and 7; the note for #8 in `shape.md`.

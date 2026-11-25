# FD001 Evidence Prompt Specification

## Identity and scope

- Work item: `WO-M4-001-WW-001`, Revision 1.
- Dataset: `NASA_CMAPSS_FD001_LOCAL`.
- Data Contract: `1.0.0`.
- Source policy: `STUDENT_TRUSTED_LOCAL_FILES`; external NASA provenance verification is `NOT_REQUIRED` and is not claimed.
- Generator location: the local read-only FD001 website. It does not call an external LLM or API and does not upload prompt content.

## Valid selection snapshot

A prompt can be generated only after all evidence requests complete for one unchanged snapshot containing:

1. Dataset Split.
2. Engine Unit.
3. Start Cycle.
4. End Cycle.
5. Selected Cycle.
6. Sensor.

Start Cycle and End Cycle are actual Cycles returned for the current Split and Unit. Start Cycle must not exceed End Cycle, and Selected Cycle must be inside the range. A Split, Unit, range, Selected Cycle or Sensor transition increments the request version, aborts applicable prior requests, clears the old evidence view, invalidates the old prompt and disables copying. Stale success and stale error responses cannot restore an invalid prompt.

## Prompt schema

### `OBSERVED_DATA`

- Dataset identity, source trust policy and external-verification status.
- Split, Unit, Start Cycle, End Cycle, Selected Cycle and canonical Sensor field.
- Selected Sensor raw token and parsed value.
- Three Operational Settings.
- Project-relative source file, source SHA-256, 1-based raw line, 0-based parsed row, 1-based raw column, canonical field, raw token and parsed value.
- For Test only: accepted RUL value and the explicit basis that it applies to that Unit's final observed Cycle, not the arbitrary Selected Cycle.
- For Train: RUL is explicitly `NOT_APPLICABLE`.

### `DERIVED_STATISTICS`

- Actual displayed Cycle start/end and actual point count.
- `FULL_UNIT_STATISTICS`: accepted full-Unit start/end values, change, OLS slope, Pearson correlation, direction, sample count and Cycle range from `/api/v1/sensor-trend`.
- `SELECTED_RANGE_STATISTICS`: first value, last value, change, minimum, maximum, arithmetic mean, point count and actual Cycle range, calculated only from API series points whose actual Cycle is inside the selected range.
- Dataset-level quality gate and quality summary, explicitly scoped to the selected Split.

Selected-range arithmetic mean is `sum(values) / sample_count`. Change is `last_value - first_value`. Minimum and maximum operate on displayed points only. A single point has count 1, equal start/end/minimum/maximum/mean and change 0. Empty ranges are rejected as `EMPTY_QUERY_RESULT`. Undefined accepted full-Unit statistics are rendered as `UNDEFINED`, never substituted with zero.

### `ANALYSIS_QUESTIONS`

The prompt asks which descriptive trend is supported, whether the series is fixed or variable, which observations and locators support the analysis, and which conclusions require additional evidence.

### `LIMITATIONS`

The generated text states that local trust is not independent NASA verification; Sensor physical names and units are unverified; descriptive trends are not causal diagnoses; fault causes and unvalidated RUL predictions cannot be confirmed; Train RUL is unavailable; Test RUL is final-Cycle evidence only; and a selected observation or range cannot be generalized to every engine.

## Bounded content and copy behavior

The prompt contains only the selected observation, Operational Settings, locator, range summaries, accepted full-Unit statistics, Split-level quality summary and applicable RUL. It does not serialize the full Sensor Series, full index or raw dataset.

Generate and Copy are explicit user actions. Copy uses `navigator.clipboard.writeText`. A successful write is reported only after the Clipboard promise resolves. Failure leaves the read-only preview available for manual selection and reports failure. Tests read the clipboard back and compare the entire prompt after platform newline normalization.

## Verification

`tests/test_fd001_evidence_prompt.py` covers range boundaries, selected-cycle correction, constant and nonconstant Sensors, single-point SVG safety, statistical scope labels, required prompt fields, RUL semantics, prompt invalidation, bounded content and actual clipboard content. `tests/test_fd001_m4_browser.py` provides the 13-item real-browser acceptance and independent TXT Oracle comparisons.

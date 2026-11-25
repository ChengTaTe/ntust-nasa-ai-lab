# FD001 M4 Evidence Comparison

## Revision 2 independent Oracle

Work item `WO-M4-001-WW-001` Revision 2 closes review findings `M4-R-001` and `M4-R-002`. The browser test reads the authorized ASCII TXT sources and `RUL_FD001.txt` directly, preserves physical line, effective row and raw token, and calculates expected values without using Catalog, API, DOM, SVG or prompt output. Only the required finite cases are summarized; no complete series or raw source is published.

Derived numeric displays use the production eight-significant-digit format. Comparisons use a half-last-place tolerance: `5.1e-9` for zero and `0.51 * 10^(floor(log10(abs(expected))) - 7)` otherwise. Counts, Cycle bounds, locators, source hashes, raw tokens and RUL rows require exact equality.

## Exact comparison matrix

| Case | Field | Independent Expected | DOM Actual | Prompt Actual | Comparison Method | Result |
|---|---|---|---|---|---|---|
| A | Selection | Test / Unit 100 / Cycle 100 / sensor_02 / range 90-110 | Exact selected controls | Exact named selection fields | Exact field map | PASS |
| A | Selected observation | line 12998; row 12997; column 7; token/value 642.62 | Exact 12-field locator map | Exact 8-field locator map and observation | Exact names and values | PASS |
| A | Operational settings | 0.0018, -0.0, 100.0 | Selected record rendered | Exact three named fields | Numeric equality | PASS |
| A | Range scope | 21 samples; Cycles 90-110 | 21; 90-110 | 21; 90-110 | Exact integers | PASS |
| A | Range statistics | start 642.33; end 642.25; change -0.08000000000004093; min 641.86; max 642.83; mean 642.3266666666667 | 642.33; 642.25; -0.08; 641.86; 642.83; 642.32667 | Same displayed values | Defined display tolerance | PASS |
| A | Full Unit scope | 198 samples; Cycles 1-198 | 198; 1-198 | 198; 1-198 | Exact and distinct from range | PASS |
| A | Test RUL | Unit 100 = raw line 100 / effective row 99 / token 20; basis final observed Cycle 198 | 20 cycles | 20; final Cycle 198, not selected Cycle 100 | Direct RUL TXT row plus exact basis parse | PASS |
| B | Selection | Train / Unit 1 / Cycle 96 / sensor_01 / range 90-100 | Exact selected controls | Exact named selection fields | Exact field map | PASS |
| B | Selected observation | line 96; row 95; column 6; token/value 518.67 | Exact 12-field locator map | Exact 8-field locator map and observation | Exact names and values | PASS |
| B | Operational settings | -0.0034, 0.0001, 100.0 | Selected record rendered | Exact three named fields | Numeric equality | PASS |
| B | Range statistics | 11 samples; Cycles 90-100; start/end/min/max/mean 518.67; change 0 | Exact named statistics | Exact named statistics | Exact integers plus defined display tolerance | PASS |
| B | Full Unit scope | 192 samples; Cycles 1-192; constant sensor Pearson undefined | 192; 1-192; `UNDEFINED` | 192; 1-192; `UNDEFINED` | Exact scope and sentinel | PASS |
| B | Train RUL | unavailable | Panel hidden | `NOT_APPLICABLE`; no Test RUL field | Exact absence/sentinel | PASS |
| C | Selection/scope | Train / Unit 1 / Cycle 96 / sensor_01 / range 96-96 | Exact selected controls | Exact named selection fields | Exact field map | PASS |
| C | Range statistics | 1 sample; Cycle 96; start/end/min/max/mean 518.67; change 0 | Exact named statistics | Exact named statistics | Exact integers plus defined display tolerance | PASS |
| C | SVG finite rendering | one constant point | one finite path command and finite dot; no NaN/Infinity | N/A | Parsed SVG coordinates | PASS |

For Cases A-C, source file and SHA-256 also matched the accepted Contract exactly: Test `3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851`; Train `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8`.

## Retained SVG and API coverage

All displayed-range API points remain compared in original order against the direct TXT oracle, including Cycle, parsed value and raw token. Expected SVG coordinates are independently calculated from the 900×350 viewBox and production padding, serialized to two decimals for the path, and compared at 0.0051 pixel tolerance; the selected dot uses unrounded coordinates at 1e-9 tolerance.

## Evidence boundary

Overview and case screenshots remain local private Worker evidence. No screenshot, comparison CSV, complete series, complete index or raw data is committed.

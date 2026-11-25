# FD001 M5 Evidence Matrix

## Independent Oracle method

The M5 test reads the authorized ASCII TXT files directly, splits whitespace tokens, preserves physical line and effective row index, and converts numeric tokens independently. API, Catalog, DOM, SVG and Prompt output are never used to construct expected raw values. All 26 raw-row fields are compared by exact canonical name, raw column, raw token, parsed value, physical line and parsed row.

## Cases A-D

| Case | Selection | Selected locator/value | Operational settings | Range statistics | Full Unit scope | Result |
|---|---|---|---|---|---|---|
| A | Test U100, sensor_02, 90-110, selected 100 | line 12998; row 12997; col 7; `642.62` | `0.0018`, `-0.0`, `100.0` | n=21; start 642.33; end 642.25; change -0.08000000000004093; min 641.86; max 642.83; mean 642.3266666666667 | n=198; Cycle 1-198 | PASS |
| B | Train U1, sensor_01, 90-100, selected 96 | line 96; row 95; col 6; `518.67` | `-0.0034`, `0.0001`, `100.0` | n=11; all 518.67; change 0 | n=192; Cycle 1-192; Pearson undefined | PASS |
| C | Train U1, sensor_01, 96-96, selected 96 | line 96; row 95; col 6; `518.67` | `-0.0034`, `0.0001`, `100.0` | n=1; all 518.67; change 0 | n=192; Cycle 1-192; Pearson undefined | PASS |
| D | Test U50, sensor_21, 74-74, selected 74 | line 6339; row 6338; col 26; raw `23.2910`, parsed 23.291 | `0.0`, `0.0004`, `100.0` | n=1; all 23.291; change 0 | n=74; Cycle 1-74 | PASS |

For every case, the source file and Contract SHA-256, the exact 12-field DOM locator, three named DOM settings, range/full scope, selected dot, four prompt sections and exact prompt field maps matched. SVG path tolerance remained 0.0051 px and selected-dot tolerance remained 1e-9 px.

## RUL and query evidence

- Direct `RUL_FD001.txt` oracle: Test Unit 100, physical line 100, effective row 99, token/value 20.
- DOM and Prompt: 20 cycles; final observed Cycle 198 basis; selected Cycle 100 and range end 110 did not replace the basis.
- Train Prompt: exact `NOT_APPLICABLE`; no fabricated Train RUL.
- Direct invalid HTTP cases verified exact envelope/status/code/message for invalid split, unknown Unit, invalid Cycle, unknown Sensor, missing parameter, duplicate parameter, invalid numeric parameter and unsupported Train RUL.

## M5-F-001 scenarios

| Scenario | Injection / condition | Expected and actual assertion | Result |
|---|---|---|---|
| F001-T01 | selected parsed value `null` | malformed error; view/prompt cleared; Generate/Copy disabled | PASS |
| F001-T02 | operational setting `null` | fail closed | PASS |
| F001-T03 | series point value `null` | fail closed before statistics/SVG | PASS |
| F001-T04 | missing locator source file | fail closed | PASS |
| F001-T05 | locator line numeric string | strict type rejection | PASS |
| F001-T06 | observation numeric string | strict type rejection | PASS |
| F001-T07 | observation boolean | strict type rejection | PASS |
| F001-T08 | missing observation | exact 26-field rejection | PASS |
| F001-T09 | legal JSON number `1e309` parsed non-finite | `Number.isFinite` rejection | PASS |
| F001-T10 | actual constant Pearson JSON `null` | DOM/Prompt `UNDEFINED`, Generate/Copy valid, never 0/NaN/Infinity | PASS |
| F001-T11 | valid prompt followed by malformed current response | old preview invalidated | PASS |
| F001-T12 | malformed current response | Generate and Copy disabled | PASS |
| F001-T13 | restore valid response and requery | current observation/statistics/SVG/locator restored | PASS |
| F001-T14 | recovered copy | Clipboard exactly matched preview after newline normalization | PASS |
| F001-T15 | delayed malformed older response | did not clear newer valid view/prompt | PASS |
| F001-T16 | delayed valid older response | did not overwrite newer malformed error | PASS |
| F001-T17 | malformed current response | rejected, not ignored by race guard | PASS |
| F001-T18 | Test RUL `null` | fail closed; valid RUL recovered afterward | PASS |
| F001-T19 | raw-row Unit identity mismatch | fail closed | PASS |
| F001-T20 | invalid trend and quality fields | both variants rejected | PASS |

All malformed cases produced no uncaught page error. Controlled fault injection does not assert that accepted FD001 contains missing observations; the accepted quality report still states zero missing values.

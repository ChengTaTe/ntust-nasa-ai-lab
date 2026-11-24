# FD001 Integration Evidence

## Evidence identity

- Work item: `WO-M3-001-EW-001` revision 1; parent `WO-M3-001`.
- Initial local and fetched remote SHA: `e4be5af8c2b812639b1a94f5b8115e18d7965cd3`.
- Contract: `1.0.0`; query specifications: 10; contract query boundaries: 7.
- Independent expected values are read directly from ASCII source lines using whitespace tokenization. They are not copied from Catalog or API output.
- Reproducible middle Cycle rule: row at zero-based index `floor((N - 1) / 2)` within the selected split-local Unit, i.e. the lower median observation.

## Source identity

| Split | Local file | SHA-256 | Role |
| --- | --- | --- | --- |
| Train | `data/FD001/train_FD001.txt` | `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8` | observation oracle and validated runtime source |
| Test | `data/FD001/test_FD001.txt` | `3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851` | observation oracle and validated runtime source |
| RUL | `data/FD001/RUL_FD001.txt` | `a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca` | Test Unit-to-RUL oracle |

## Integration evidence matrix

| ID | Requirement / contract reference | Selection | Expected derivation | Verification layers | Tolerance | Result / evidence |
| --- | --- | --- | --- | --- | --- | --- |
| INT-001 | AC-01/02, contract identity | all sources | SHA-256 of local bytes and JSON contract fields | source → API status | exact | PASS; `test_01_sources_contract_and_loopback_boundary` |
| INT-002 | TASK-03, AC-04/06 | Train Unit 1/50/100, first/lower-middle/last | direct raw token and numeric conversion | raw → HTTP API row/locator | exact | PASS; 9 observations × 26 fields |
| INT-003 | TASK-03, AC-04/06 | Test Unit 1/50/100, first/lower-middle/last | direct raw token and numeric conversion | raw → HTTP API row/locator | exact | PASS; 9 observations × 26 fields |
| INT-004 | AC-05 | Test Unit 50 lower-middle, Sensor 01..21 | columns 6..26 from one raw row | raw → sensor dictionary → API locator | exact | PASS; all 21 Sensors |
| INT-005 | TASK-03 | same representative row | columns 3..5 | raw → Catalog/API settings | exact | PASS; all three settings |
| INT-006 | TASK-04, AC-07 | all 10 query names | names loaded from accepted contract JSON | contract → actual HTTP routes | exact | PASS; all routes returned success envelopes |
| INT-007 | TASK-04/07 | seven contract boundaries | accepted contract JSON and isolated failure injection | Catalog/API/HTTP | exact code/status | PASS; six natural invalid requests plus accepted isolated `EMPTY_QUERY_RESULT` regression |
| INT-008 | TASK-06, AC-09 | Train U1 S01; Train U100 S02; Test U50 S07; Test U100 S01 | independent OLS/Pearson calculation from raw rows | raw → API trend | `1e-12` absolute for slope/correlation; exact other fields | PASS; constant/nonconstant, both splits, different lengths |
| INT-009 | TASK-05, AC-08 | Train U50 C100 S21 | Browser request output compared with DOM | API → DOM value/settings/locator | exact numeric conversion | PASS; actual Edge |
| INT-010 | TASK-05/06 | Test U100 C100 S02 | series count and trend fields from API | API series → SVG path/dot/stat DOM | exact count/text | PASS; actual Edge |
| INT-011 | AC-10 | Test Unit 1/50/100; Train Unit 1 | direct RUL row `n → unit_id n`; unsupported Train query | raw RUL → API → Browser | exact | PASS; Train shows no fabricated RUL |
| INT-012 | TASK-05/07 | intercepted integrity failure | isolated Browser route fault | API failure → distinct Browser error state | exact error kind | PASS; normal value cleared |
| INT-013 | TASK-07, AC-11 | missing/mismatch/change/disappearance | temporary roots and method mocks in accepted regression | source guard → sticky API failure | exact | PASS; restart-required behavior verified |
| INT-014 | TASK-05 | delayed Unit/Split/Sensor/Cycle/error requests | deterministic Browser request delays | HTTP → transaction/version guard → DOM | exact final selection | PASS; accepted 19-case Browser suite |
| INT-015 | AC-12/13 | six required suites | actual `unittest` executions | parser/API/Web/Browser/M3 | no failures; no skips | PASS; 74 passed, 0 failed, 0 skipped |

## Raw locator and Sensor mapping

Each of the 18 representative observation rows verifies all of the following fields: split, Unit, Cycle, source file, source SHA-256, raw line number, zero-based parsed row index, one-based raw column index, canonical field name, raw token, and parsed numeric value. Canonical observation order is Unit, Cycle, three Operational Settings, then Sensor 01..21; Sensor raw columns are exactly 6..26.

Train and Test Unit IDs are tested as independent namespaces: identical `(unit_id=1, cycle=1)` selections resolve to different source files and SHA-256 values.

## Trend and statistical consistency

The test oracle computes `N`, Cycle range, start, end, change, OLS slope, and Pearson correlation directly from raw rows. A zero Sensor variance yields `None`/`null` and direction `flat`. Nonconstant cases cover increasing and decreasing patterns across Train and Test and different Unit lengths. Numeric comparison uses `1e-12` absolute tolerance for slope and correlation because the runtime and oracle use the same accepted double-precision formulas but accumulate independently; raw values, counts, ranges, and directions use exact comparison. The tolerance was fixed before execution and was not loosened to obtain a pass.

## Regression and actual Browser results

| Suite | Passed | Failed | Skipped | Exit code |
| --- | ---: | ---: | ---: | ---: |
| `test_fd001.py` | 25 | 0 | 0 | 0 |
| `test_fd001_api.py` | 15 | 0 | 0 | 0 |
| `test_fd001_web.py` | 5 | 0 | 0 | 0 |
| `test_fd001_browser.py` | 19 | 0 | 0 | 0 |
| `test_fd001_integration.py` | 6 | 0 | 0 | 0 |
| `test_fd001_integration_browser.py` | 4 | 0 | 0 | 0 |
| **Total** | **74** | **0** | **0** | **all 0** |

Actual Browser execution used Microsoft Edge `158.0.4370.33` through Playwright `1.55.0`, headless at a 1440×1000 viewport. Browser cases exercised real loopback HTTP, DOM selection, locator/settings rendering, SVG series mapping, Test RUL, Train RUL absence, and an isolated error presentation. No required Browser case was skipped.

## Integrity and fault behavior

- Missing startup source and accepted-hash mismatch: validated snapshot unavailable, normal query HTTP 503.
- Post-start source change or disappearance: snapshot cleared, failure sticky, restart required.
- Invalid Split/Unit/Cycle/Sensor, unsupported Train RUL, missing field, and empty-result injection preserve their expected codes.
- API unavailable/source integrity errors render as errors rather than normal data.
- Formal FD001 sources were never mutated; fault cases used temporary roots, mocks, or Browser request interception.

## Limitations

- Full raw rows, complete indices, and complete Sensor series are intentionally absent from this GitHub-bound evidence summary.
- The suite verifies accepted local source identity and internal traceability; it does not independently establish NASA provenance.
- Descriptive trends do not establish causality, diagnosis, or RUL prediction.
- Worker execution is not Engineering Brain independent execution or acceptance.

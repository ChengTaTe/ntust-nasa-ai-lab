# FD001 Website Actual Browser UAT

## Execution record

- Work Item: `WO-M2-002-WW-001`, Revision `2`
- Test command: `python -m unittest discover -s tests -p "test_fd001_browser.py" -v`
- Exit code: `0`
- Result: `19 passed / 0 failed / 0 skipped`
- Browser automation: Playwright Python `1.55.0`
- Browser engine: Microsoft Edge Chromium `158.0.4370.33`, headless
- Viewport: `1440 × 1000`
- Python: `3.15.2`
- Service: ephemeral loopback port created by the same production `create_server` implementation
- Raw data remained local; no screenshot, complete series, browser binary, or raw data was committed.

## Results

| ID | Operation | Expected result | Actual evidence | Result |
| --- | --- | --- | --- | --- |
| UAT-01 | Navigate to `/`; wait for Ready. | Page and validated Dataset status load. | Title was `FD001 Health Analytics`; status was `LOCAL_DATA_VERIFIED`. | PASS |
| UAT-02 | Change Split from Train to Test. | Test namespace reloads and RUL appears. | Split value became `test`; Test RUL panel became visible. | PASS |
| UAT-03 | Select Engine Unit 50. | Current observation changes to Unit 50. | Selection summary displayed Engine Unit 50 after Ready. | PASS |
| UAT-04 | Select the last available Cycle. | Valid range and current Cycle remain consistent. | Last option was accepted and displayed in the selection summary. | PASS |
| UAT-05 | Inspect all Sensor options; select Sensor 21. | Exactly Sensor 01–21 are selectable. | 21 ordered options matched `sensor_01`–`sensor_21`; selected label updated. | PASS |
| UAT-06 | Compare displayed Sensor 01 value with raw-row API. | Browser value equals API parsed value. | Displayed value numerically equaled API `fields.sensor_01.parsed_value`. | PASS |
| UAT-07 | Switch Sensor 01 to Sensor 02. | Trend redraws for the selected Sensor. | Native SVG path changed and chart title displayed `sensor_02`. | PASS |
| UAT-08 | Inspect Raw Data Locator. | Relative file, line/index/column and raw token are visible. | Panel included `data/FD001/train_FD001.txt`, line and column keys, and raw token `518.67`. | PASS |
| UAT-09 | Compare settings panel with API. | Settings 1–3 exactly match API values. | All three rendered numeric values equaled `operational-settings` response values. | PASS |
| UAT-10 | Enter Test mode and compare Unit 1 RUL. | RUL matches API and is labeled for final observation. | Browser showed the API RUL value with `cycles`; explanatory label remained visible. | PASS |
| UAT-11 | Inspect Train mode. | No fabricated Train RUL is shown. | RUL panel was hidden in Train mode. | PASS |
| UAT-12 | Intercept raw-row with a 503 integrity error. | A clear source-integrity error appears. | Error panel displayed `SOURCE_INTEGRITY_FAILURE` and the test message. | PASS |
| UAT-13 | Delay Unit 2 Cycle response by 700 ms, select Unit 3 with a 30 ms response, then release Unit 2. | No stale Unit 2 response changes the Unit 3 state. | Final selector, complete Cycle list and summary all matched Unit 3 after the delayed Unit 2 response was observed. | PASS |
| UAT-14 | Inspect constant Sensor 01 trend. | Constant line renders; undefined Pearson is not zero. | SVG path existed; Direction was `flat`; Pearson displayed `UNDEFINED`. | PASS |
| UAT-15 | Change to Sensor 02 and inspect console. | No unhandled critical JavaScript errors. | Captured console error list remained empty. | PASS |
| RACE-16 | Delay Test Unit response, switch Train → Test → Train, then release Test. | Final namespace is Train and no stale Test RUL remains. | Split/summary remained Train and RUL stayed hidden after the delayed Test response. | PASS |
| RACE-17 | Delay Sensor 02/Cycle 2 requests, select Sensor 03/Cycle 3, then release stale responses. | Value, chart, statistics, Locator and summary all describe Sensor 03/Cycle 3. | Displayed value matched raw-row API; chart, Locator and summary retained the final selection. | PASS |
| RACE-18 | Return a delayed error for Unit 2 after Unit 3 has succeeded. | Stale error cannot replace current success. | Error panel remained hidden; state and summary remained Ready for Unit 3. | PASS |
| RACE-19 | Inject empty, invalid-selection and unavailable responses. | Error categories remain distinguishable. | DOM error kinds were `empty-result`, `invalid-selection` and `api-unavailable`; source integrity remains separately covered by UAT-12. | PASS |

## Interpretation

These tests use a real local browser engine and DOM interaction; they are not static HTML checks. Revision 2 uses browser init scripts to deterministically delay or fail selected fetch responses while allowing later requests to finish first. The tests observe explicit release markers rather than relying only on natural network order or fixed waits. Browser-to-API checks cover complete Cycle options, selected values, settings, RUL, traceability, trend/statistics, distinct failure states, transaction invalidation and late success/error suppression. Statistical output remains descriptive and is not labeled as a confirmed fault diagnosis.

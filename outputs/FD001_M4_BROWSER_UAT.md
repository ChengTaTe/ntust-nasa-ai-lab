# FD001 M4 Browser UAT

## Environment and method

- Work item: `WO-M4-001-WW-001`, Revision 1.
- Python: 3.15.2.
- Browser: Microsoft Edge Chromium 158.0.4370.33, headless.
- Playwright: 1.55.0.
- Server: real loopback `ThreadingHTTPServer` created by `web.server`; production startup command independently verified at `http://127.0.0.1:8000/`.
- Method: Playwright browser interaction, real loopback HTTP/API, browser Clipboard API, controlled response ordering, and local TXT parsing for the required comparison cases.
- Screenshot evidence: three local PNG files were produced in the private temporary evidence directory; screenshots are not committed.

## Results

| Test ID | Steps and expected result | Actual result | Evidence | Result |
|---|---|---|---|---|
| UAT-M4-01 | Open the real site and query status; expect HTTP 200 and verified data. | Title loaded; status API returned `data_available=true`. | `test_uat_m4_01_real_site_and_http_api_start`, overview screenshot | PASS |
| UAT-M4-02 | Switch Train/Test and compare Unit 1 namespaces. | Split changed; Train/Test source SHA values differed and Test selection rendered. | `test_uat_m4_02_train_test_namespace_separation` | PASS |
| UAT-M4-03 | Change Engine Unit to 100; expect all Cycle selectors rebuilt from actual Cycles. | Start, End and Selected option lists exactly matched the independent Unit 100 TXT Cycle list. | `test_uat_m4_03_engine_unit_rebuilds_valid_cycles` | PASS |
| UAT-M4-04 | Select range 90-100 and Selected Cycle 96, then shrink End to 95. | 11 actual options/samples rendered; Selected Cycle deterministically corrected to 95. | `test_uat_m4_04_range_sample_count_and_selected_boundary` | PASS |
| UAT-M4-05 | Change Sensor inside a fixed range. | SVG path and title updated to the current Sensor. | `test_uat_m4_05_sensor_switch_updates_range_trend` | PASS |
| UAT-M4-06 | CASE A: compare browser, loopback API, independent TXT, locator, SVG and prompt. | All 21 points, selected observation and source locator matched. | `test_uat_m4_06_case_a_api_raw_dom_svg_prompt`, CASE A screenshot | PASS |
| UAT-M4-07 | CASE B and a one-Cycle constant series. | All 11 CASE B points matched; single-point SVG contained finite path/dot coordinates. | `test_uat_m4_07_case_b_constant_and_single_point_svg`, CASE B screenshot | PASS |
| UAT-M4-08 | Generate, preview, copy, read clipboard and compare. | Clipboard read-back equaled the entire preview after CRLF/LF normalization. | `test_uat_m4_08_prompt_preview_and_actual_copy` | PASS |
| UAT-M4-09 | Generate prompt, change Sensor, then regenerate. | Preview cleared immediately, Copy disabled, and regenerated prompt contained the current Sensor. | `test_uat_m4_09_prompt_invalidates_on_selection_change` | PASS |
| UAT-M4-10 | Exercise inconsistent range correction, empty result, unavailable API and integrity failure. | Range corrected deterministically; each error received a distinct UI category; prompt generation remained disabled on failure. | `test_uat_m4_10_invalid_empty_unavailable_and_integrity_errors` | PASS |
| UAT-M4-11 | Compare Test RUL semantics and Train absence. | Test prompt stated final-observed-Cycle basis; Train hid RUL and stated `NOT_APPLICABLE`. | `test_uat_m4_11_test_rul_basis_and_train_absence` | PASS |
| UAT-M4-12 | Release delayed stale success/error after a newer Sensor/Cycle succeeds. | Current Cycle 3/Sensor 03 DOM and prompt remained intact; stale error did not display. | `test_uat_m4_12_controlled_stale_success_and_error_isolation` | PASS |
| UAT-M4-13 | Operate accepted row, locator, statistics and chart features while monitoring console. | No critical console errors; 26 fields, relative locator and full-Unit statistics remained visible. | `test_uat_m4_13_console_clean_and_existing_evidence_visible` | PASS |

Result: **13 passed, 0 failed, 0 skipped**. The tests control delayed response release and do not depend on ordinary network timing. Clipboard acceptance verifies the copied text, not only button presence.

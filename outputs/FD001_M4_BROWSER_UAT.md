# FD001 M4 Browser UAT

## Revision 2 environment and method

- Work item: `WO-M4-001-WW-001`, Revision 2; related review `WO-M4-002`.
- Baseline: `2028f8fbfcab14c0b3be2dfbf6f07971ed257a2e`.
- Python 3.15.2; Microsoft Edge Chromium 158.0.4370.33 headless; Playwright 1.55.0.
- Real loopback `ThreadingHTTPServer`, production website/API, browser Clipboard API, controlled response ordering, and direct local TXT/RUL parsing.
- Three screenshots are retained only in the private temporary evidence directory.

Revision 2 adds independent assertions for every selected-range statistic, full-Unit versus selected-range scope, exact DOM and prompt name/value maps, raw locator fields, operational settings, dataset identity/trust policy, and direct Test RUL row alignment. Assertions no longer accept locator or prompt substring presence as evidence.

## Results

| Test ID | Acceptance focus | Revision 2 actual result | Result |
|---|---|---|---|
| UAT-M4-01 | Real site and status API | HTTP 200; verified data loaded | PASS |
| UAT-M4-02 | Train/Test namespace separation | Independent source hashes and selections remained distinct | PASS |
| UAT-M4-03 | Unit change rebuilds Cycles | Options exactly matched direct TXT Unit Cycles | PASS |
| UAT-M4-04 | Range boundaries and correction | 11 samples; selected Cycle corrected deterministically | PASS |
| UAT-M4-05 | Sensor change | Current SVG path and title updated | PASS |
| UAT-M4-06 | CASE A exact evidence | All raw/API/DOM/SVG/prompt/statistics/locator/RUL fields matched | PASS |
| UAT-M4-07 | CASE B and CASE C | Constant range and one-point statistics matched; finite SVG | PASS |
| UAT-M4-08 | Preview and actual Clipboard | Full read-back equal after platform newline normalization | PASS |
| UAT-M4-09 | Prompt invalidation | Preview cleared and Copy disabled until regeneration | PASS |
| UAT-M4-10 | Invalid/empty/unavailable/integrity errors | Distinct fail-closed UI states; prompt disabled | PASS |
| UAT-M4-11 | RUL semantics | Test final-observed-Cycle basis; Train not applicable | PASS |
| UAT-M4-12 | Stale response isolation | Delayed success/error could not overwrite current state | PASS |
| UAT-M4-13 | Console and retained evidence | No critical console error; evidence views remained visible | PASS |

Targeted Revision 2 browser result: **13 passed, 0 failed, 0 skipped**, Exit Code 0. The final eight-suite regression result is recorded in `FD001_M4_REPORT.md`.

## Review-gap disposition

- `M4-R-001`: closed by direct raw-TXT calculation and named DOM/prompt comparison for start, end, change, minimum, maximum, arithmetic mean, sample count and Cycle bounds across Cases A-C. Full-Unit scope is separately checked.
- `M4-R-002`: closed by exact section parsing and exact field maps for dataset identity, trust policy, selection, observation, operational settings, source locator, derived statistics and Test/Train RUL semantics.
- Production defect: none observed. No production, API, Contract or dependency file was changed.

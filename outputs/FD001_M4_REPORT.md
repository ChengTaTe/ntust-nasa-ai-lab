# FD001 M4 Bounded Rework Report

## Governance and scope

- Parent: `WO-M4-001`; Worker: `WO-M4-001-WW-001`, Revision 2; review: `WO-M4-002`.
- Authorized baseline: `2028f8fbfcab14c0b3be2dfbf6f07971ed257a2e`.
- Data Contract `1.0.0`, raw sources and all production files remain unchanged.
- Findings addressed: `M4-R-001` independent statistics coverage and `M4-R-002` exact prompt/locator field coverage.
- Worker result is submitted as `PENDING_BRAIN_REVIEW`; it is not a Brain `PASS`.

Only the existing M4 browser test and the three authorized M4 evidence reports changed. The optional prompt unit-test file was not changed because browser-level exact prompt verification was sufficient. No new file was created.

## Rework result

The real-browser oracle now calculates Cases A-C directly from the accepted TXT sources. It checks every selected-range statistic, full-Unit/range scope separation, exact DOM locator fields, exact prompt sections and named values, source identity and trust policy, operational settings, and Train/Test RUL semantics. Test Unit 100 RUL is independently read from physical line 100/effective row 99 of `RUL_FD001.txt` and tied to final observed Cycle 198 rather than selected Cycle 100 or range end 110.

The earlier API ordering, raw token, SVG path, selected-dot, Clipboard, error-state, prompt invalidation and stale-response coverage is retained. Constant and one-point cases explicitly verify `UNDEFINED` Pearson semantics and finite SVG output.

## Test summary

Revision 1 historical baseline: **96 passed, 0 failed, 0 skipped**.

Revision 2 final suite commands and results:

| Suite | Tests | Failed | Skipped | Exit Code |
|---|---:|---:|---:|---:|
| `test_fd001.py` | 25 | 0 | 0 | 0 |
| `test_fd001_api.py` | 15 | 0 | 0 | 0 |
| `test_fd001_web.py` | 5 | 0 | 0 | 0 |
| `test_fd001_browser.py` | 19 | 0 | 0 | 0 |
| `test_fd001_integration.py` | 7 | 0 | 0 | 0 |
| `test_fd001_integration_browser.py` | 4 | 0 | 0 | 0 |
| `test_fd001_evidence_prompt.py` | 8 | 0 | 0 | 0 |
| `test_fd001_m4_browser.py` | 13 | 0 | 0 | 0 |
| **Total** | **96** | **0** | **0** | **0** |

The final rerun used Python 3.15.2, Edge 158.0.4370.33 and Playwright 1.55.0. Each suite was invoked separately with `python -m unittest discover -s tests -p <suite> -v`. Exact command/exit evidence accompanies the Worker return.

## Data protection and limitations

- Raw sources remain local, read-only and untracked; no complete index, full series, screenshot or CSV is committed.
- Evidence generation is local and does not upload the prompt.
- Sensor physical identities/units remain unverified; statistics are descriptive, not causal or diagnostic; no RUL prediction is performed.
- Trusted local file identity is not represented as independent NASA provenance verification.
- M4 acceptance remains subject to independent STUDENT-WEB Brain review of the pushed GitHub commit.

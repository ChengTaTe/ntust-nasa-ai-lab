# M3 FD001 Engineering Integration Report

## Work order and decision status

- Project: `NTUST_CMAPSS_HEALTH_ANALYTICS`
- Work item: `WO-M3-001-EW-001`, revision 1
- Parent: `WO-M3-001`
- Authorized by: STUDENT
- STUDENT M3 authorization: approved
- MAIN M3 Execution Release: granted
- Worker submission status: `PENDING_BRAIN_REVIEW`
- Engineering Brain review / Engineering domain acceptance: pending
- Research and Web domain acceptance: pending MAIN coordination
- M3 overall gate: not completed
- M4/M5 authorization: not granted

This Worker report does not declare Engineering Brain PASS or M3 Overall PASS.

### Revision history and current bounded rework

- Revision 1 produced the original M3 integration submission at `a223bb75ca4b97e2e21ea6375d20fd50a7a717d7`.
- Revision 2 resolved Engineering finding `M3-EW-001`; accepted commit `1f6581736bfd08689cb6d8905e11c8c191ea7492` and SVG coordinate verification remain retained.
- Revision 3 addresses only Research review finding `M3-R-001` from `WO-M3-002`: independent raw-text evidence for the complete API Sensor series used by the two accepted SVG cases.
- Revision 3 status is `PENDING_BRAIN_REVIEW`; Engineering rework acceptance and MAIN-coordinated Research recheck remain pending.

## Accepted prerequisites

M0 and M1 final acceptance, M2-G/M2-A/M2-B final acceptance, and M2 overall PASS were supplied as the formal execution basis. Accepted commits used by this integration are:

- M1: `0ba0a16c1e6904a389fef87b66389662cf0737b3`
- M2-A: `0dc22ace2616a4b3efb7caab1050ddb27c6f113c`
- M2-B / initial M3 baseline: `e4be5af8c2b812639b1a94f5b8115e18d7965cd3`

Fetched `origin/main`, local HEAD, and the expected baseline all resolved to the M2-B SHA before implementation. The initial worktree and index were clean, the branch was `main`, no Git index lock existed, and all five M3 output paths were absent.

## Governance and accepted-artifact integrity

The four governance Git Blob SHA values matched the work order exactly. Local SHA-256 baselines were:

| File | SHA-256 |
| --- | --- |
| `AGENTS.md` | `82206b4112ea7cc86f6977a4a4c28aec82809bae580251d4b25239a03406298f` |
| `ROADMAP.md` | `2cf535bb4605cec9451960eb0c42a0496e20dd8fcec89e4f0cfb1d072f63dc07` |
| `WORK_ITEM.md` | `cd77784c74658e3d5fdb99b8ddb9a182f0ad6174f6b7274947333c4856be79d1` |
| `DECISIONS.md` | `7a93b48d858c9631174ca09b9a7b19af94627e731e1fc51daeab469c2dadc43a` |
| `.gitignore` | `a6348a8a50f334e14cdd261e3aedc5b1c984fb64fa2e13883882cf90e80c6264` |

`git diff --exit-code` against the relevant accepted commits returned 0 for the two M1 artifacts, nine M2-A artifacts, fourteen M2-B artifacts, and governance/`.gitignore`. Data Contract JSON reported `contract_version=1.0.0`. No accepted artifact was regenerated or modified.

## Execution environment

- OS execution: Windows PowerShell, project root specified by the work order.
- Python: `3.15.2` at `C:\Users\user\AppData\Local\Python\pythoncore-3.15-64\python.exe`.
- Playwright: `1.55.0`.
- Browser: Microsoft Edge `158.0.4370.33`, headless.
- Server: accepted standard-library `ThreadingHTTPServer`, ephemeral `127.0.0.1` port.
- The PATH `python` command was an inaccessible Windows Store alias, so all actual test commands used the explicit existing interpreter path. No dependency was installed or changed.

## Reproducible commands and actual results

The required commands were executed with the explicit interpreter in place of `python`:

```powershell
& 'C:\Users\user\AppData\Local\Python\pythoncore-3.15-64\python.exe' -m unittest discover -s tests -p "test_fd001.py" -v
& 'C:\Users\user\AppData\Local\Python\pythoncore-3.15-64\python.exe' -m unittest discover -s tests -p "test_fd001_api.py" -v
& 'C:\Users\user\AppData\Local\Python\pythoncore-3.15-64\python.exe' -m unittest discover -s tests -p "test_fd001_web.py" -v
& 'C:\Users\user\AppData\Local\Python\pythoncore-3.15-64\python.exe' -m unittest discover -s tests -p "test_fd001_browser.py" -v
& 'C:\Users\user\AppData\Local\Python\pythoncore-3.15-64\python.exe' -m unittest discover -s tests -p "test_fd001_integration.py" -v
& 'C:\Users\user\AppData\Local\Python\pythoncore-3.15-64\python.exe' -m unittest discover -s tests -p "test_fd001_integration_browser.py" -v
```

The Revision 1/2 executions returned exit code 0: 25 Research regression, 15 API, 5 Website, 19 Browser UAT, 6 M3 HTTP integration, and 4 M3 Browser integration cases passed. Historical total: 74 passed, 0 failed, 0 skipped.

An earlier non-elevated M3 HTTP run returned exit code 1 because the managed sandbox rejected loopback connections with Windows error 10013. The identical suite was rerun with local-loopback permission and passed. This is recorded as an execution-environment constraint, not a product failure; expected values and coverage were not changed. A subsequent small test-harness correction closed `HTTPError` response objects to remove resource warnings and did not change assertions.

## Verification method and result

- Raw-to-API: direct independent tokenization of the local raw files was compared with actual loopback HTTP output for Train/Test, Units 1/50/100, and first/lower-middle/last observations. All 26 columns and their locators were checked.
- Sensor mapping: all 21 Sensors were verified against columns 6..26, including raw token, parsed value, and row/column locator.
- Contract: all ten query specifications were mapped to actual routes. All seven contract error boundaries were covered through natural invalid requests or the accepted isolated empty-result injection.
- Trend/statistics: four representative constant/nonconstant cases across Train/Test and different Unit lengths were independently recomputed. Slope and Pearson tolerance was fixed at `1e-12` absolute; other values were exact.
- RUL: RUL row `n` mapped to Test Unit `n` for Units 1/50/100. Train RUL returned the unsupported boundary and the UI displayed no fabricated RUL.
- API-to-Website: actual Edge verified selected values, settings, raw locator, statistical DOM, SVG point count/dot, RUL, and distinct error rendering.
- SVG coordinate rework `M3-EW-001`: actual Path X/Y coordinates were compared with an independent test oracle for first/lower-middle/last API series points, and selected Cycle dot coordinates were verified for Test Unit 100 Sensor 02 (nonconstant) and Train Unit 1 Sensor 01 (constant). The accepted `toFixed(2)` Path representation uses a fixed `0.0051 px` tolerance; unrounded dot coordinates use `1e-9 px`.
- Raw-to-series rework `M3-R-001` from `WO-M3-002`: Revision 3 independently tokenized the complete raw rows for Test Unit 100/Sensor 02 (198 points) and Train Unit 1/Sensor 01 (192 points). Actual loopback HTTP success envelopes were checked for full series metadata, equal length before iteration, and every point's Cycle, parsed value, raw token, raw line number, and parsed row index in original order. Selected Cycles 100 and 96 were present. Comparisons were exact with no numeric tolerance.
- Integrity: accepted regression verified missing, hash mismatch, post-start change, disappearance, sticky failure, and restart-required behavior using isolation/mocks rather than formal raw mutation.
- Stale requests: accepted Browser regression deterministically verified delayed Split/Unit/Sensor/Cycle success and error responses cannot replace current state.

## Engineering conclusion

Within the authorized M3 scope, the accepted FD001 parser/Catalog, Data Contract v1.0.0, API, local server, Browser DOM/SVG, raw locator, trend statistics, and Test RUL behavior form a reproducible traceability chain. All required regression and M3 suites passed without skips, and no accepted M1/M2 component defect requiring unauthorized correction was found.

The conclusion is limited to the STUDENT-trusted local files and accepted implementation. It is not external source verification, causal diagnosis, or an RUL prediction model.

## Deliverables and limitations

The M3 persistent deliverables are:

1. `tests/test_fd001_integration.py`
2. `tests/test_fd001_integration_browser.py`
3. `outputs/FD001_SYSTEM_INTEGRATION.md`
4. `outputs/FD001_INTEGRATION_EVIDENCE.md`
5. `outputs/FD001_INTEGRATION_REPORT.md`

Final deliverable SHA-256, commit identity/parent/object format, push result, remote file verification, and final worktree status are reported in the Worker Return after commit and remote verification; the report intentionally does not create a follow-up commit merely to embed its own commit SHA.

Revision 2 is a bounded rework for Engineering Brain finding `M3-EW-001`. It modifies only the Browser integration test and the Evidence/Report documents listed by the rework authorization; no M2 website code or accepted raw-data expectation was changed.

Revision 3 is a bounded rework for `M3-R-001`. It modifies only `tests/test_fd001_integration.py` and the Evidence/Report documents. The six Revision 3 executions returned exit code 0: 25 Research, 15 API, 5 Website, 19 Browser UAT, 7 M3 HTTP integration, and 4 M3 Browser integration tests passed, for 75 passed, 0 failed, and 0 skipped. The Revision 2 Browser integration test and `FD001_SYSTEM_INTEGRATION.md` were not modified.

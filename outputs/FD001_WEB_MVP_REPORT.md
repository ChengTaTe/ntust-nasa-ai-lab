# FD001 Local Website MVP Implementation Report

## Governance and release basis

- WORK_ITEM_ID: `WO-M2-002`
- CHILD_WORK_ITEM_ID: `WO-M2-002-WW-001`
- Revision: `1`
- Accepted M2-A Commit: `0dc22ace2616a4b3efb7caab1050ddb27c6f113c`
- Data Contract: `1.0.0`
- MAIN M2-A PASS: confirmed by the formal work order
- STUDENT M2-B authorization: `APPROVED`
- MAIN M2-B Execution Release: `GRANTED`
- Web Brain Governance Preflight: `PASS`
- Initial local/remote main SHA: `0dc22ace2616a4b3efb7caab1050ddb27c6f113c`

Historical pending/not-granted fields in the accepted governance documents were treated as historical snapshots under the explicit work-order release. No governance file was edited.

## Architecture

The backend is Python standard library `ThreadingHTTPServer` plus a bounded `BaseHTTPRequestHandler`. `web.api.FD001API` reuses the accepted `tools.profile_fd001.FD001Catalog`, validates the three accepted source hashes and structural/quality gates, and serves a single in-memory snapshot. Source hashes are checked again for every query; detected changes disable normal queries.

The frontend is semantic HTML, responsive CSS, and vanilla JavaScript. A native SVG chart renders raw per-Cycle values without smoothing, interpolation, normalization, or imputation. `AbortController` plus a monotonic request version prevents stale asynchronous responses from being labeled as a newer selection. No CDN, third-party analytics, cloud database, external data API, or public deployment is used.

## Functional coverage

- Train/Test split, Engine Unit, Cycle and all 21 Sensor selectors.
- Complete 26-column record with raw and parsed values.
- Operational Settings 1–3 and field locators.
- Native SVG Sensor series with selected-Cycle marker.
- Accepted Start, End, Change, OLS slope, Pearson correlation, Direction and sample count.
- Complete selected-field Raw Data Locator with relative source path and SHA-256.
- Structural, quality, constant/near-constant and potential-outlier summary with explicit limits.
- Test-only RUL with final-observed-Cycle explanation; no Train RUL.
- Loading, ready and source/API error states; request cancellation for selector races.

## Data integrity evidence

Accepted source SHA-256 values were verified before implementation and again by the service:

- Train: `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8`
- Test: `3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851`
- RUL: `a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca`

Known Train and Test Unit 1 / Cycle 1 / Sensor 01 locators both resolved to raw line 1, parsed row 0, raw column 6 and raw token `518.67`, while retaining distinct Split namespaces and source hashes. API tests also sample middle/end records, non-constant Sensor 02, differing Unit Cycle maxima, Test RUL alignment and all Sensor raw-column mappings.

## Test results

| Suite | Command | Result |
| --- | --- | --- |
| Research regression | `python -m unittest discover -s tests -p "test_fd001.py" -v` | 25 passed, 0 failed |
| API / contract | `python -m unittest discover -s tests -p "test_fd001_api.py" -v` | 10 passed, 0 failed |
| HTTP / static security | `python -m unittest discover -s tests -p "test_fd001_web.py" -v` | 5 passed, 0 failed |
| Actual Browser UAT | `python -m unittest discover -s tests -p "test_fd001_browser.py" -v` | 15 passed, 0 failed |

Browser evidence: Playwright 1.55.0 drove installed Microsoft Edge Chromium 158.0.4370.33 at 1440×1000. Detailed steps and results are in `outputs/FD001_BROWSER_UAT.md`.

## Authorized scope and limitations

Only the 14 files named in the formal work order were added. Governance files, M1 artifacts, M2-A artifacts and raw files were not edited. Raw data remains untracked and is neither committed nor uploaded.

Limitations:

- This is a local loopback MVP, not a public deployment or multi-user service.
- Source identity follows `STUDENT_TRUSTED_LOCAL_FILES`; independent NASA provenance verification was not required or claimed.
- Sensor physical quantities/units remain `UNVERIFIED`.
- Trends and statistical outliers do not establish causation, faults, or diagnoses.
- RUL prediction, failure models, Evidence Prompt generation, M3, M4 and M5 are outside this work item.

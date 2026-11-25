# FD001 M5 Browser UAT

## Execution identity

- Work item: `WO-M5-001-WW-001`, Revision 2.
- Baseline: `46402aa9dd967bd2da0e497505c56fdfa232b072`.
- Python 3.15.2; Microsoft Edge Chromium 158.0.4370.33; Playwright 1.55.0.
- Automated URL: ephemeral `http://127.0.0.1:<port>`; production startup independently verified at `http://127.0.0.1:8000/`.
- Command: `python -m unittest discover -s tests -p "test_fd001_m5_browser.py" -v`.
- Result: 12 tests passed, 0 failed, 0 errors, 0 skipped, Exit Code 0.

## Revision 1 finding and Revision 2 correction

At baseline SHA `46402aa9...`, controlled injection `raw-row.data.fields.sensor_01.parsed_value=null` produced `資料已就緒`, `UNDEFINED`, enabled Generate, a valid prompt and enabled Copy. Revision 2 validates all evidence responses before rendering or assigning `loadedEvidence`. The same injection now yields an explicit `malformed-response` error, clears observation/chart/prompt, sets `data-valid=false`, disables Generate/Copy and produces no page error. Restoring the valid response permits a current requery, regenerated prompt and exact Clipboard read-back.

## UAT-M5-01 through UAT-M5-15

| UAT ID | Objective / precondition | Execution method and steps | Expected and actual result | Status / evidence |
|---|---|---|---|---|
| UAT-M5-01 | Local startup from accepted baseline | Start `python -m web.server`; GET `/`, GET status; open Edge | HTTP 200, `LOCAL_DATA_VERIFIED`, controls enabled; observed exactly | PASS; `test_m5_01...`, S01 |
| UAT-M5-02 | Train/Test namespaces and Units | Train→Test→Train; compare API and option lists | Unit/Cycle namespaces rebuilt; stale view invalidated | PASS; `test_m5_02...` |
| UAT-M5-03 | First/middle/last and ranges | Direct TXT Cycles; select first/middle/last, multi/single range | Only actual Cycles; Selected Cycle constrained to range | PASS; `test_m5_02...`, `test_m5_03...` |
| UAT-M5-04 | Canonical Sensors | Verify 21 options; switch 01/02/21 | Exact canonical field, column, value, trend and locator | PASS; `test_m5_02...` |
| UAT-M5-05 | Independent rows | Direct ASCII oracle; Cases A-D; compare all 26 fields | Every raw token, parsed value, line, row, column and setting matched | PASS; `test_m5_03...`, S02-S04 |
| UAT-M5-06 | Trend/statistics/SVG | Direct range calculations and independent coordinates | Counts/order/scopes/stats exact; path 0.0051 px; dot 1e-9 px | PASS; `test_m5_04...` |
| UAT-M5-07 | Invalid queries | Eight direct HTTP cases plus controlled browser empty result | Exact status/code/message/envelope; prompt disabled | PASS; `test_m5_05...`, S06 |
| UAT-M5-08 | Null and undefined | Actual constant Pearson plus 20 controlled fault scenarios | Legal Pearson null → `UNDEFINED`; required malformed values fail closed | PASS; `test_m5_06...`, `test_m5_07...`, S05/S10 |
| UAT-M5-09 | Interruption and recovery | Controlled HTTP error; actual secondary server shutdown/restart | Unavailable state invalidated evidence; restored service reloaded valid data | PASS; `test_m5_05...`, `test_m5_12...`, S07/S08 |
| UAT-M5-10 | Stale response guards | Deterministic delayed malformed and valid responses | Old responses did not replace newer valid/error state | PASS; `test_m5_09...`, `test_m5_10...` |
| UAT-M5-11 | Prompt accuracy | Parse exact sections/fields for Cases A-D | Selection, locator, source, settings and both scopes matched oracle | PASS; `test_m5_04...`, S09 |
| UAT-M5-12 | RUL semantics | Direct RUL TXT row 100 and Train absence | Test Unit 100=20 at row 99; final Cycle 198 basis; Train N/A | PASS; `test_m5_11...` |
| UAT-M5-13 | Preview/Clipboard | Generate, copy, read Clipboard; invalidate; recover | Preview equals Clipboard after LF/CRLF normalization; invalid copy blocked | PASS; `test_m5_08...`, `test_m5_12...`, S11 |
| UAT-M5-14 | Data protection | Loopback, static denial, pre/post hashes, no external endpoints | No raw modification/publication, arbitrary access or prompt upload | PASS; `test_m5_01...` |
| UAT-M5-15 | Final user workflow | Start→select→inspect→generate→copy→stop | Complete workflow succeeded; console/page errors empty; server stopped | PASS; `test_m5_12...`, S08 |

## Private screenshots

S01-S11 are actual Edge captures stored only in the private temporary evidence directory. Public evidence records their IDs and SHA-256, not the private absolute path. The manifest records UTC capture time and displayed state. No screenshot is committed.

| ID | State | SHA-256 |
|---|---|---|
| S01 | startup | `c9ef910419bc471a312fc39fb4500f0b915452af13764a548d4734bbe91ff114` |
| S02 | Case A | `e3f81e70764144f7dde4ce2882331a716f3386aed6bcf70cd57e788c671eeba5` |
| S03 | Case B | `eba1c715762a00fcc99d908493c4c118be13d78925b4299cb54520803ebfcc91` |
| S04 | Case C | `4395e3c6fd39db3f7a437c4c5dd5fbe2d24edc0d9171c13363d728ef00703a9d` |
| S05 | legitimate undefined | `89431c8f55f7c36c5e826bba88b09c6b199600415a3aa2e31137b0ee85e2c114` |
| S06 | invalid/error | `ee036d6fed440ae9bfc69ea684071bafa1fc9946877aa178580177c229ba71b7` |
| S07 | actual interruption | `c7250ef42cf24ecd6b1ca820584f3b4d2c37f53d7f644bb813a0ed7956cac956` |
| S08 | service recovery | `7a66e83cd598fbadf01f23ac6238889537d208b296e65ba20cd2b00938bb7aff` |
| S09 | prompt preview | `64f5e58bcd3a9629bf423ba9b82a6dc95b824aa4925bdb4c54760cbd971b6b53` |
| S10 | corrected M5-F-001 | `22a806574dfc472317535c0c39cff2e06dcd056c271af0e3ffebd7a9befcf859` |
| S11 | recovered prompt | `d8596ba4b800a82fbfcdbfdf000196a273c789468a1cb6c152bb89b7a255b609` |

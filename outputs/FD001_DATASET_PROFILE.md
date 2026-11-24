# FD001 Local Dataset Profile

- Execution timestamp: `2026-11-24T15:27:25+08:00`
- Source trust policy: `STUDENT_TRUSTED_LOCAL_FILES`
- External source verification: `NOT_REQUIRED`
- Internet download or replacement: `PROHIBITED`
- Parser: strict ASCII/UTF-8 decode; each nonblank line is split on one or more whitespace characters.
- Header rows: none detected or expected; every effective line is parsed as data.
- Provenance limitation: local file identity and structure are verified, but NASA official provenance was not independently checked.

## File inventory

| Split | Source file | Bytes | SHA-256 | Encoding | Text lines | Blank lines | Blank positions | Trailing-space lines | Trailing-space positions | Parsed rows | Column distribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | data/FD001/train_FD001.txt | 3515356 | 963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8 | ascii | 20631 | 0 | None | 20631 | 1-20631 | 20631 | {"26": 20631} |
| test | data/FD001/test_FD001.txt | 2228855 | 3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851 | ascii | 13096 | 0 | None | 13096 | 1-13096 | 13096 | {"26": 13096} |
| rul | data/FD001/RUL_FD001.txt | 429 | a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca | ascii | 100 | 0 | None | 100 | 1-100 | 100 | {"1": 100} |

## Structural validation

| Split | Rows | Units | Unit min | Unit max | Cycle min | Cycle max | Duplicate keys | Units with missing cycles | Non-monotonic units | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | 20631 | 100 | 1 | 100 | 1 | 362 | 0 | 0 | 0 | PASS |
| test | 13096 | 100 | 1 | 100 | 1 | 303 | 0 | 0 | 0 | PASS |

- RUL rows/columns: `100 × 1`
- RUL non-negative integer validation: `PASS`
- RUL-to-Test-Unit alignment: `PASS`

## Dataset semantics

| Statement | Status |
| --- | --- |
| Train contains split-local Unit, Cycle, three operational-setting columns, and 21 sensor columns. | LOCAL_DATA_VERIFIED |
| Train represents complete run-to-failure trajectories. | FORMAT_CONVENTION |
| Test contains truncated trajectories and its last observed cycle is not a failure cycle. | FORMAT_CONVENTION |
| The nth effective RUL row maps to test Unit ID n after structural alignment checks. | FORMAT_CONVENTION + LOCAL_DATA_VERIFIED alignment |
| Train and Test Unit ID n identify the same physical engine. | UNVERIFIED; explicitly prohibited assumption |
| The files were independently confirmed against NASA official downloads. | UNVERIFIED |

## Field dictionary summary

The complete 26-field dictionary and RUL definition are normative in `contracts/FD001_DATA_CONTRACT.md` and `.json`. Raw columns 1-2 are `unit_id` and `cycle`; columns 3-5 are `op_setting_1..3`; columns 6-26 are `sensor_01..sensor_21`. Physical sensor/setting names and units remain `UNVERIFIED`.

## Limitations

- Structural compatibility does not independently prove NASA official provenance.
- No raw values were corrected, removed, imputed, normalized, or smoothed.
- Full raw rows and full RUL lists are intentionally omitted from this public artifact.

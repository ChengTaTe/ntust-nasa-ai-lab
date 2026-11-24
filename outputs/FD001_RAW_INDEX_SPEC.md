# FD001 Raw Data Index Specification

## Index construction

- Raw line numbers are one-based physical text-line positions.
- Parsed row indexes are zero-based and exclude blank lines.
- Raw column indexes are one-based.
- Blank lines remain part of raw line numbering but do not create parsed rows.
- Train and Test Unit IDs use independent namespaces.
- Raw values preserve the original whitespace-delimited token; parsed and derived values are separately labeled.
- Parsing never sorts, renumbers, or rearranges rows.

## Keys

- Train/Test row: `(dataset_split, unit_id, cycle)`
- Sensor value: `(dataset_split, unit_id, cycle, sensor_id)`
- RUL: `(dataset_split=test, unit_id)`

## Required locator fields

`dataset_id`, `dataset_split`, `source_file`, `source_sha256`, `raw_line_number`, `parsed_row_index`, `unit_id`, `cycle`, `raw_column_index`, `canonical_field_name`, `raw_value`, `parsed_value`, and separately labeled derived values.

## RUL mapping

The nth effective RUL row maps to Test Unit ID n only after confirming Test Unit IDs are exactly 1..N and RUL has N effective rows. This is a validated structural application of the FD001 format convention, not external proof of physical-engine identity.

## Limited traceability examples

| Split | Unit | Cycle | Raw line | Parsed index | Raw column | Field | Raw token | Parsed value | Source SHA-256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | 1 | 1 | 1 | 0 | 6 | sensor_01 | 518.67 | 518.67 | 963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8 |
| train | 52 | 194 | 10316 | 10315 | 6 | sensor_01 | 518.67 | 518.67 | 963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8 |
| train | 100 | 200 | 20631 | 20630 | 6 | sensor_01 | 518.67 | 518.67 | 963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8 |
| test | 1 | 1 | 1 | 0 | 6 | sensor_01 | 518.67 | 518.67 | 3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851 |
| test | 52 | 66 | 6549 | 6548 | 6 | sensor_01 | 518.67 | 518.67 | 3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851 |
| test | 100 | 198 | 13096 | 13095 | 6 | sensor_01 | 518.67 | 518.67 | 3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851 |

These examples cover first, middle, and last parsed rows. The complete index is rebuilt locally in memory and is not committed.

## Local query surface

`FD001Catalog` implements split/unit/cycle/sensor listing, raw-row lookup, operational-setting lookup, sensor-trend lookup, data-quality lookup, Test RUL lookup, and raw-source locator lookup with documented error codes.

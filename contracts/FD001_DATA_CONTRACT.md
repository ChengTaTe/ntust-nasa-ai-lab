# FD001 Data Contract

- Contract version: `1.0.0`
- Status: `PENDING_RESEARCH_BRAIN_REVIEW`

## Dataset identity

| Dataset ID | Split | Source file | SHA-256 | Trust policy | Verification | Rows | Column distribution |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NASA_CMAPSS_FD001_LOCAL | train | data/FD001/train_FD001.txt | 963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8 | STUDENT_TRUSTED_LOCAL_FILES | LOCAL_DATA_VERIFIED | 20631 | {"26": 20631} |
| NASA_CMAPSS_FD001_LOCAL | test | data/FD001/test_FD001.txt | 3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851 | STUDENT_TRUSTED_LOCAL_FILES | LOCAL_DATA_VERIFIED | 13096 | {"26": 13096} |
| NASA_CMAPSS_FD001_LOCAL | rul | data/FD001/RUL_FD001.txt | a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca | STUDENT_TRUSTED_LOCAL_FILES | LOCAL_DATA_VERIFIED | 100 | {"1": 100} |

## Train/Test field dictionary

| Column | Canonical name | 繁體中文 | English | Type | Purpose | Physical quantity | Unit | Nullable | Missing rule | Semantic basis | Confirmation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | unit_id | 引擎單元識別碼 | Engine unit identifier | positive integer | Split-local unit key | identifier/count | dimensionless | NO | Reject absent, invalid, or non-finite tokens; do not impute. | LOCAL_DATA_VERIFIED | LOCAL_DATA_VERIFIED |
| 2 | cycle | 運轉週期 | Operating cycle | positive integer | Ordered cycle within a split-local unit | identifier/count | dimensionless | NO | Reject absent, invalid, or non-finite tokens; do not impute. | LOCAL_DATA_VERIFIED | LOCAL_DATA_VERIFIED |
| 3 | op_setting_1 | 操作設定 1 | Operational setting 1 | finite number | Operational condition input | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 4 | op_setting_2 | 操作設定 2 | Operational setting 2 | finite number | Operational condition input | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 5 | op_setting_3 | 操作設定 3 | Operational setting 3 | finite number | Operational condition input | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 6 | sensor_01 | 感測器 01 | Sensor 01 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 7 | sensor_02 | 感測器 02 | Sensor 02 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 8 | sensor_03 | 感測器 03 | Sensor 03 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 9 | sensor_04 | 感測器 04 | Sensor 04 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 10 | sensor_05 | 感測器 05 | Sensor 05 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 11 | sensor_06 | 感測器 06 | Sensor 06 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 12 | sensor_07 | 感測器 07 | Sensor 07 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 13 | sensor_08 | 感測器 08 | Sensor 08 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 14 | sensor_09 | 感測器 09 | Sensor 09 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 15 | sensor_10 | 感測器 10 | Sensor 10 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 16 | sensor_11 | 感測器 11 | Sensor 11 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 17 | sensor_12 | 感測器 12 | Sensor 12 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 18 | sensor_13 | 感測器 13 | Sensor 13 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 19 | sensor_14 | 感測器 14 | Sensor 14 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 20 | sensor_15 | 感測器 15 | Sensor 15 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 21 | sensor_16 | 感測器 16 | Sensor 16 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 22 | sensor_17 | 感測器 17 | Sensor 17 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 23 | sensor_18 | 感測器 18 | Sensor 18 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 24 | sensor_19 | 感測器 19 | Sensor 19 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 25 | sensor_20 | 感測器 20 | Sensor 20 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |
| 26 | sensor_21 | 感測器 21 | Sensor 21 | finite number | Sensor measurement | UNVERIFIED | UNVERIFIED | NO | Reject absent, invalid, or non-finite tokens; do not impute. | FORMAT_CONVENTION | LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED |

## RUL field and relationships

- Field: `rul_cycles`; type `non-negative integer`; unit `cycle`; nullable `False`.
- Relationship: The nth effective RUL row maps to test unit_id n after alignment validation.
- Namespace rule: Train and test unit IDs are independent namespaces and do not identify the same physical engine.
- Primary keys:
  - `train_test`: `dataset_split, unit_id, cycle`
  - `sensor_value`: `dataset_split, unit_id, cycle, sensor_id`
  - `rul`: `dataset_split=test, unit_id`

## Query specification

| Query | Inputs | Output | Sort | Boundaries | Traceability |
| --- | --- | --- | --- | --- | --- |
| list_dataset_splits | {} | dataset_split | train, test | None | None |
| list_units_by_split | {"split": "string"} | unit_id | unit_id ascending | INVALID_SPLIT | dataset_split |
| list_cycles_by_unit | {"split": "string", "unit_id": "positive integer"} | cycle | cycle ascending in raw order | INVALID_SPLIT, UNKNOWN_UNIT, EMPTY_QUERY_RESULT | dataset_split, unit_id |
| list_sensors | {} | sensor_id, raw_column_index | sensor number ascending | None | canonical_field_name |
| get_raw_row | {"cycle": "positive integer", "split": "string", "unit_id": "positive integer"} | 26 parsed fields, source locator | single row | INVALID_SPLIT, UNKNOWN_UNIT, INVALID_CYCLE, MISSING_DATA | source_file, source_sha256, raw_line_number, parsed_row_index |
| get_sensor_trend | {"sensor_id": "sensor_01..sensor_21", "split": "string", "unit_id": "positive integer"} | cycle range, sample count, start/end/change, slope, correlation, direction, source locator | single result | INVALID_SPLIT, UNKNOWN_UNIT, UNKNOWN_SENSOR, MISSING_DATA | source_sha256, first_raw_line, last_raw_line, raw_column_index |
| get_operational_settings | {"cycle": "positive integer", "split": "string", "unit_id": "positive integer"} | op_setting_1, op_setting_2, op_setting_3, source locator | canonical column order | INVALID_SPLIT, UNKNOWN_UNIT, INVALID_CYCLE, MISSING_DATA | raw_line_number, raw_column_index |
| get_data_quality_summary | {"split": "string"} | quality gate, structural checks, feature statistics | canonical field order | INVALID_SPLIT, EMPTY_QUERY_RESULT | source_file, source_sha256 |
| get_test_rul | {"split": "string", "unit_id": "positive integer"} | rul_cycles, source locator | single result | INVALID_SPLIT, UNKNOWN_UNIT, UNSUPPORTED_RUL_QUERY, MISSING_DATA | source_file, source_sha256, raw_line_number, parsed_row_index, raw_column_index |
| get_raw_source_locator | {"cycle": "positive integer", "field_name": "canonical field name", "split": "string", "unit_id": "positive integer"} | raw and parsed locator/value | single result | INVALID_SPLIT, UNKNOWN_UNIT, INVALID_CYCLE, UNKNOWN_SENSOR, MISSING_DATA | source_file, source_sha256, raw_line_number, parsed_row_index, raw_column_index, raw_value, parsed_value |

## Query boundaries

- `INVALID_SPLIT`: Split is not train or test.
- `UNKNOWN_UNIT`: The unit does not exist in the selected split.
- `INVALID_CYCLE`: The cycle is invalid or absent for the selected unit.
- `UNKNOWN_SENSOR`: The sensor identifier is outside sensor_01..sensor_21.
- `MISSING_DATA`: A required field or source value is absent.
- `EMPTY_QUERY_RESULT`: A valid query has no rows; it is not converted to zero.
- `UNSUPPORTED_RUL_QUERY`: Train RUL is not supplied by RUL_FD001.txt.

## Traceability

- `raw_line_number_base`: 1
- `raw_column_index_base`: 1
- `parsed_row_index_base`: 0
- `blank_lines`: Count in raw line numbering but do not create parsed rows.
- `raw_value`: Original whitespace-delimited token.
- `parsed_value`: Finite numeric conversion of raw_value.
- `derived_value`: Explicitly labeled result calculated from parsed values.
- `required_locator_fields`: ["source_file", "source_sha256", "raw_line_number", "raw_column_index", "parsed_row_index", "unit_id", "cycle", "canonical_field_name"]

## Data integrity

- `raw_data_mode`: read-only
- `fabricated_values`: prohibited
- `silent_correction`: prohibited
- `parser`: UTF-8/ASCII strict decode; nonblank lines split on one or more whitespace characters; finite numeric conversion.
- `train_test_namespace`: independent
- `source_hash_rule`: Recompute SHA-256 before and after analysis and require equality.
- `complete_index_publication`: prohibited; rebuild locally in memory

## Version control

- Compatibility: Patch changes preserve field names, query meanings, keys, and error codes. Breaking changes require a new major version and Brain acceptance.
- `1.0.0` (2026-11-24): Initial validated FD001 local data contract.

Evidence references:
- `outputs/FD001_DATASET_PROFILE.md`
- `outputs/FD001_RAW_INDEX_SPEC.md`
- `outputs/FD001_DATA_QUALITY.md`
- `outputs/FD001_SENSOR_TRENDS.md`

## Limitations

- The three files are trusted by STUDENT; NASA official provenance was not independently verified.
- Physical names and units for operational settings and sensors are UNVERIFIED.
- Test last observed cycle is not a failure cycle.
- Train and test unit IDs are independent namespaces.
- Correlation and trends do not establish causation, fault diagnosis, or an RUL prediction model.

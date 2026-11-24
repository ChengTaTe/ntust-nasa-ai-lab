# FD001 Local Web API Specification

## Identity and transport

- Dataset ID: `NASA_CMAPSS_FD001_LOCAL`
- Data Contract: `1.0.0`
- Source trust policy: `STUDENT_TRUSTED_LOCAL_FILES`
- External source verification: `NOT_REQUIRED`
- Base URL: `http://127.0.0.1:8000`
- Transport: local HTTP, read-only `GET`
- Success envelope: `{"ok":true,"data":...,"error":null}`
- Error envelope: `{"ok":false,"data":null,"error":{"code":"...","message":"..."}}`
- JSON serialization rejects NaN and Infinity; undefined statistics are JSON `null`.

## Endpoints

| Route | Required parameters | Contract mapping / result |
| --- | --- | --- |
| `GET /api/v1/splits` | None | `list_dataset_splits`; ordered Train/Test namespaces |
| `GET /api/v1/units` | `split` | `list_units_by_split`; ascending split-local Unit IDs |
| `GET /api/v1/cycles` | `split`, `unit_id` | `list_cycles_by_unit`; ascending raw-order cycles |
| `GET /api/v1/sensors` | None | `list_sensors`; `sensor_01`–`sensor_21` and raw columns 6–26 |
| `GET /api/v1/raw-row` | `split`, `unit_id`, `cycle` | `get_raw_row`; all 26 canonical fields, raw tokens, parsed values and row locator |
| `GET /api/v1/sensor-trend` | `split`, `unit_id`, `sensor_id` | `get_sensor_trend`; accepted OLS/Pearson statistics and source locator |
| `GET /api/v1/operational-settings` | `split`, `unit_id`, `cycle` | `get_operational_settings`; three settings plus per-field locators |
| `GET /api/v1/data-quality` | `split` | `get_data_quality_summary`; structure, feature statistics, quality gate and limits |
| `GET /api/v1/test-rul` | `split=test`, `unit_id` | `get_test_rul`; RUL row locator and final-observation semantics |
| `GET /api/v1/raw-source-locator` | `split`, `unit_id`, `cycle`, `field_name` | `get_raw_source_locator`; complete raw/parsed locator |
| `GET /api/v1/sensor-series` | `split`, `unit_id`, `sensor_id` | Web display adapter; current Unit/Sensor cycle series with line/index traceability |
| `GET /api/v1/status` | None | Dataset/contract/trust identity, availability and local validation status |

All parameters must appear exactly once. Unknown, empty, duplicate, missing, or route-inapplicable parameters are rejected. Positive integers use canonical decimal form without signs or leading zeroes. Every split-bearing route validates the split through the accepted Catalog query boundary before accessing split-keyed analysis data; `/api/v1/data-quality?split=invalid` therefore returns HTTP 400 with `INVALID_SPLIT`.

## Traceability fields

Raw row fields retain `dataset_id`, `dataset_split`, `source_file`, `source_sha256`, `raw_line_number`, `parsed_row_index`, `unit_id`, `cycle`, `raw_column_index`, `canonical_field_name`, `raw_value`, and `parsed_value`.

- `raw_line_number`: one-based physical text line.
- `raw_column_index`: one-based raw column.
- `parsed_row_index`: zero-based effective parsed row.
- `source_file`: repository-relative path only; private absolute paths are never returned.
- RUL traceability follows its one-column source contract and does not invent a Cycle column.

## Errors and HTTP mapping

| Code | HTTP | Meaning |
| --- | ---: | --- |
| `INVALID_SPLIT` | 400 | Split is not `train` or `test`. |
| `UNKNOWN_UNIT` | 404 | Unit does not exist in the selected split. |
| `INVALID_CYCLE` | 400 | Cycle is invalid or absent for the selected Unit. |
| `UNKNOWN_SENSOR` | 400 | Sensor is outside `sensor_01`–`sensor_21`. |
| `MISSING_DATA` | 503 | A required field/source value is absent. |
| `EMPTY_QUERY_RESULT` | 404 | A valid query has no rows; it is never converted to zero. |
| `UNSUPPORTED_RUL_QUERY` | 400 | Train RUL is not supplied. |
| `INVALID_REQUEST` | 400 | Parameters or query syntax are invalid. |
| `METHOD_NOT_ALLOWED` | 405 | A method other than GET was used. |
| `NOT_FOUND` | 404 | Route/static resource is not allowed. |
| `SOURCE_INTEGRITY_FAILURE` | 503 | Validated source snapshot is unavailable or a source changed. |
| `INTERNAL_ERROR` | 500 | Safe response serialization failed. |

## Integrity and security

At startup, the service verifies accepted SHA-256 values, 26-column Train/Test structure, one-column RUL structure, Unit/Cycle continuity, RUL alignment, and the accepted quality gate through `FD001Catalog` inputs. It serves the resulting validated in-memory snapshot. Each query rechecks source availability and hashes. A missing, mismatched, changed or disappeared source permanently invalidates that process snapshot, clears its Catalog/analysis references and returns `SOURCE_INTEGRITY_FAILURE`. Merely restoring the file cannot resume queries; restart and complete startup validation are required. `/api/v1/status` reports `data_available: false` and `validation_status: SOURCE_INTEGRITY_FAILURE` while disabled.

The bind address is fixed to `127.0.0.1`. Static files use an explicit allowlist. There is no arbitrary path input, directory server, path traversal, upload, mutation, external request, public bind, or complete-dataset download endpoint. A restrictive Content Security Policy permits only same-origin scripts, styles, images and API connections.

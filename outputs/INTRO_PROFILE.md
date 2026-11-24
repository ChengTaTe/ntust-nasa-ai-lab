# Synthetic Sensor Dataset Profile

## Dataset identity

- Dataset type: `Synthetic Sensor Data`
- Source path: `data/synthetic_sensor.csv`
- Source provenance: Local synthetic sensor CSV authorized by the M1 data contract.
- Generation provenance: The file's generator, author, and generation date are not established by the available evidence.
- NASA C-MAPSS FD001 status: This dataset is not identified as NASA C-MAPSS FD001.
- File size: 234 bytes
- Input SHA-256: `cd536b46eb628909fdc986bbad956c24a2e50afb287968998374befc62204377`

## CSV structure

- Parser: Python standard-library `csv.reader` with `csv.Sniffer`
- Encoding: `utf-8`
- Delimiter: `','`
- Header detected: `TRUE`
- Actual data rows (header excluded): 6
- Column count: 4
- Column names: `timestamp`, `load_pct`, `coolant_out_c`, `oil_pressure_bar`
- Blank column-name positions: None
- Duplicate column names: None

## Inferred data types

Missing values are excluded from type inference. Values are trimmed for inference only; the source values are not changed.

| Column | Inferred type | Type consistent | Basis |
| --- | --- | --- | --- |
| `timestamp` | ISO-8601 datetime | YES | Missing values were excluded; remaining trimmed values were tested in order as integer, Decimal-compatible number, ISO-8601 datetime, then text (datetime=6). |
| `load_pct` | integer | YES | Missing values were excluded; remaining trimmed values were tested in order as integer, Decimal-compatible number, ISO-8601 datetime, then text (integer=6). |
| `coolant_out_c` | integer | YES | Missing values were excluded; remaining trimmed values were tested in order as integer, Decimal-compatible number, ISO-8601 datetime, then text (integer=6). |
| `oil_pressure_bar` | number | YES | Missing values were excluded; remaining trimmed values were tested in order as integer, Decimal-compatible number, ISO-8601 datetime, then text (decimal=5). |

## Missing values

A value is missing when it is an empty string, contains only whitespace, or matches one of these case-insensitive textual markers after trimming: `n/a`, `na`, `nan`, `none`, `null`.

- Missing values total: 1
- Blank or whitespace-only values: 1
- Textual missing markers: 0

| Column | Missing count |
| --- | ---: |
| `timestamp` | 0 |
| `load_pct` | 0 |
| `coolant_out_c` | 0 |
| `oil_pressure_bar` | 1 |

Missing positions use one-based data-row positions and exclude the header row.

| Data row | CSV line | Column | Missing kind |
| ---: | ---: | --- | --- |
| 4 | 5 | `oil_pressure_bar` | blank_or_whitespace |

## Duplicate rows

A duplicate is an additional data row whose complete parsed field sequence exactly matches an earlier row. Comparison is case-sensitive and whitespace-preserving.

- Duplicate row count (rows beyond the first occurrence): 1
- Duplicate position groups: [5, 6]

## Format validation

- All data rows have 4 fields: YES
- Row-width mismatches: None
- Header names are nonblank and unique: YES
- Non-missing values are type-consistent within every column: YES
- Overall format validation: PASS

## Expected versus actual

- Expected data rows: 6
- Actual data rows: 6
- Contract result: MATCH

## Execution environment

- Execution timestamp: `2026-11-24T11:20:51+08:00`
- Execution timezone: `Asia/Taipei (UTC+08:00)`
- Python version: `3.15.2`
- Python implementation: `CPython`
- Platform: `Windows-11-10.0.26300-SP0`
- Third-party packages: None; this profiler uses only the Python standard library.
- Reproduction command: `python tools/profile_intro.py --input data/synthetic_sensor.csv --output outputs/INTRO_PROFILE.md --expected-rows 6 --execution-timestamp 2026-11-24T11:20:51+08:00`

## Limitations

- Dataset identity follows the approved M1 contract; the original generator, author, and creation date are not independently traceable from the CSV.
- Type inference is lexical and does not prove physical units, sensor calibration, or semantic validity.
- Missing-value detection is limited to blanks, whitespace-only fields, and the documented textual markers.
- Duplicate detection compares complete parsed rows and does not identify near-duplicates.
- The report contains derived statistics and schema information only; it does not reproduce complete source rows.

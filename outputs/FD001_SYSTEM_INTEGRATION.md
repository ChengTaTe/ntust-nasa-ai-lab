# FD001 System Integration Architecture

## Scope and status

- Work item: `WO-M3-001-EW-001`, revision 1; parent `WO-M3-001`.
- Baseline: M2-A `0dc22ace2616a4b3efb7caab1050ddb27c6f113c`; M2-B `e4be5af8c2b812639b1a94f5b8115e18d7965cd3`.
- Data contract: `1.0.0`.
- This document describes the accepted implementation as verified; it does not redesign or modify M2 components.
- Worker submission status: `PENDING_BRAIN_REVIEW`. Engineering Brain, Research Brain, Web Brain, and M3 overall acceptance remain pending.

## Runtime architecture and responsibility

```text
read-only local FD001 files
  |  strict ASCII/UTF-8 decode, whitespace tokenization, finite numeric conversion
  v
parse_data_file / parse_rul_file
  |-- structural gate: 26 columns, positive Unit/Cycle, unique ordered keys
  |-- quality gate: cycle continuity, missing/duplicate checks, RUL alignment
  v
FD001Catalog (validated in-memory snapshot)
  |-- split-local Unit namespaces
  |-- raw row, settings, Sensor trend, RUL, and raw locator queries
  v
FD001API (contract adapter and integrity guard)
  |-- recomputes source hashes before every normal query
  |-- finite-only JSON values; undefined statistics remain null
  |-- success/error envelopes and HTTP status mapping
  v
ThreadingHTTPServer bound only to 127.0.0.1
  |-- allowlisted static files and GET-only API
  v
Browser UI (DOM + SVG)
  |-- Split / Unit / Cycle / Sensor selection
  |-- observation, settings, RUL, statistics, and raw locator rendering
  |-- transaction version + AbortController stale-response protection
  v
observable local evidence (no upload or dataset-download route)
```

### Component boundaries

| Component | Responsibility | Failure boundary |
| --- | --- | --- |
| Raw FD001 files | Trusted local Train, Test, and RUL input; immutable under this work item | Missing file or wrong SHA-256 disables validated data |
| Parser | Preserve raw token, parsed value, raw line, parsed row, and raw column identity | Invalid encoding, column count, number, Unit, or Cycle raises validation failure |
| Structural gate | Require stable 26-column observations, unique `(split, unit, cycle)`, and ordered contiguous cycles | Invalid structure cannot enter trend analysis or Catalog |
| Data quality gate | Validate duplicate/missing behavior and Test Unit-to-RUL alignment | Failed quality prevents accepted analysis snapshot |
| `FD001Catalog` | Deterministic in-memory contract query layer | Raises one of seven documented query boundaries |
| Data Contract v1.0.0 | Defines schema, 10 queries, 7 boundary codes, traceability, and null semantics | Immutable in M3 |
| `FD001API` | Validate parameters, adapt Catalog results, reject non-finite JSON, preserve error codes | Integrity failure is sticky; restart is required after source loss/change |
| Local HTTP server | Serve API/static allowlist over loopback, apply security headers | Non-loopback bind and non-GET mutations are rejected |
| Browser UI | Render current selection, series, SVG, statistics, RUL, locator, and distinct error state | Stale responses cannot replace current selection; errors are not shown as normal data |
| M3 tests | Independent raw-token oracle plus actual HTTP/Browser comparison | Tests never mutate formal raw files or accepted M1/M2 artifacts |

## Data flow and traceability

1. Startup resolves only `data/FD001/train_FD001.txt`, `test_FD001.txt`, and `RUL_FD001.txt` under the project root.
2. `FD001API` requires the accepted SHA-256 for all three files before building the snapshot.
3. Parser records `source_file`, `source_sha256`, `raw_line_number`, zero-based `parsed_row_index`, tokens, numeric values, Unit, and Cycle.
4. Catalog indexes Train and Test separately. An equal Unit ID across splits is not the same engine identity.
5. The API exposes the accepted ten contract queries plus Web-only `status` and `sensor-series` adapter routes.
6. HTTP success is `{ok:true,data:<value>,error:null}`. Failure is `{ok:false,data:null,error:{code,message}}` with the mapped status.
7. The UI obtains its observation, Sensor series/trend, settings, quality, locator, and Test RUL through HTTP and renders only after all requests for the current transaction complete.
8. Raw locator values remain tied to the exact local source hash and row/column coordinates; no full index is published.

## Query interfaces

The ten contract queries are `list_dataset_splits`, `list_units_by_split`, `list_cycles_by_unit`, `list_sensors`, `get_raw_row`, `get_sensor_trend`, `get_operational_settings`, `get_data_quality_summary`, `get_test_rul`, and `get_raw_source_locator`. They map respectively to `/api/v1/splits`, `/units`, `/cycles`, `/sensors`, `/raw-row`, `/sensor-trend`, `/operational-settings`, `/data-quality`, `/test-rul`, and `/raw-source-locator`. `/api/v1/status` and `/api/v1/sensor-series` are bounded Web adapters, not additions to the Data Contract.

The seven contract error boundaries are `INVALID_SPLIT`, `UNKNOWN_UNIT`, `INVALID_CYCLE`, `UNKNOWN_SENSOR`, `MISSING_DATA`, `EMPTY_QUERY_RESULT`, and `UNSUPPORTED_RUL_QUERY`. HTTP also uses adapter-specific `INVALID_REQUEST`, `NOT_FOUND`, `METHOD_NOT_ALLOWED`, `SOURCE_INTEGRITY_FAILURE`, and `INTERNAL_ERROR` where appropriate.

## Error propagation and restart behavior

- Missing or mismatched sources at startup produce a status response with `data_available=false`; normal queries return `SOURCE_INTEGRITY_FAILURE`.
- A source change or disappearance after startup invalidates the snapshot. The error is sticky even if the source reappears; only a process restart performs the complete validation and constructs a new coherent snapshot.
- Invalid selection errors retain contract codes through Catalog, API envelope, HTTP status, and Browser error classification.
- Browser request abortion and version checks prevent delayed success or delayed failure from overwriting a newer selection.
- Undefined Pearson correlation is Python `None`, JSON `null`, and UI `UNDEFINED`; it is never NaN, Infinity, or fabricated zero.

## Data protection boundary

- Server binding is restricted to `127.0.0.1`.
- Static serving uses an explicit allowlist; arbitrary repository files cannot be fetched.
- Only GET is supported. There is no raw upload, external API, analytics, full-dataset download, or complete-index route.
- The three raw sources remain local and ignored by Git. M3 fault injection uses mocks, request interception, or temporary isolated roots; formal raw files are not modified.
- GitHub evidence is limited to reusable tests and summarized results, not complete time series, complete indices, or raw datasets.

## Verified limitations

- Source policy is `STUDENT_TRUSTED_LOCAL_FILES`; external NASA provenance was not independently verified.
- Sensor physical quantities and units remain unverified.
- Trend statistics are descriptive and are not causation, fault diagnosis, or an RUL prediction model.
- Test RUL is attached to a Test Unit under the accepted file-format convention; the last observed Test cycle is not asserted to be a failure cycle.

# FD001 M4 Evidence Comparison

## Independent Oracle method

The comparison test reads the authorized local ASCII TXT source directly, splits each non-empty line on whitespace, converts tokens independently, and filters by Unit and Cycle range in original file order. It does not use Catalog, API, DOM or SVG output to construct expected values. Only the finite required ranges are summarized here; the full series and raw files are not published.

SVG expectation uses the displayed range only. For viewBox 900 by 350 and padding left 68, right 28, top 24, bottom 48:

- `x = 68 + (cycle - min_cycle) / max(1, max_cycle - min_cycle) * 804`
- `y = 24 + (max_value - value) / (max_value - min_value) * 278`
- Constant values receive the UI's documented margin `max(abs(value) * 0.01, 1)`.
- Path coordinates are serialized to two decimals and compared with 0.0051 pixel tolerance; the selected dot uses the unrounded coordinate and 1e-9 tolerance.

## CASE A

- Selection: Test, Unit 100, Sensor 02, range 90-110, Selected Cycle 100, raw column 7.
- Independent actual point count: **21**.
- Source: `data/FD001/test_FD001.txt`; SHA-256 `3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851`.
- First: Cycle 90, raw token/value `642.33`, expected SVG `(68.0, 167.298969...)`.
- Selected observation: raw line 12998, parsed row 12997, raw token/value `642.62`, Operational Settings `0.0018`, `-0.0`, `100.0`, expected dot `(470.0, 84.185567...)`.
- Last: Cycle 110, raw token/value `642.25`, expected SVG `(872.0, 190.226804...)`.
- Test Unit 100 RUL: 20 Cycles, explicitly tied to the Unit's final observed Cycle rather than Selected Cycle 100.
- Result: API points, order, DOM value, locator, all SVG path coordinates, selected dot, prompt selection, raw token, locator and sample count matched the independent Oracle.

## CASE B

- Selection: Train, Unit 1, Sensor 01, range 90-100, Selected Cycle 96, raw column 6.
- Independent actual point count: **11**.
- Source: `data/FD001/train_FD001.txt`; SHA-256 `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8`.
- First: Cycle 90, raw token/value `518.67`, expected SVG `(68.0, 163.0)`.
- Selected observation: raw line 96, parsed row 95, raw token/value `518.67`, Operational Settings `-0.0034`, `0.0001`, `100.0`, expected dot `(550.4, 163.0)`.
- Last: Cycle 100, raw token/value `518.67`, expected SVG `(872.0, 163.0)`.
- Train RUL: not supplied and explicitly `NOT_APPLICABLE`.
- Result: API points, order, DOM value, locator, all constant-series SVG coordinates, selected dot and prompt evidence matched the independent Oracle. A separate one-Cycle rendering at Cycle 96 produced finite SVG coordinates without NaN or Infinity.

## Evidence boundary

Screenshots for the overview and both cases are retained only as local private Worker evidence. No screenshot, comparison CSV, complete series, complete index or raw data is committed.

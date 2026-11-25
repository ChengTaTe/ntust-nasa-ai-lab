# FD001 Health Analytics — Local MVP

This read-only local application exposes the accepted FD001 Data Contract v1.0.0 through a Python standard-library HTTP server and a dependency-free browser UI.

## Start

From the repository root:

```powershell
python -m web.server
```

Open <http://127.0.0.1:8000/>. The server refuses non-loopback bind addresses. On startup it verifies the three authorized local raw files, validates their structure and RUL alignment, and builds one in-memory snapshot. Normal queries are disabled if a source file is missing, has an unexpected SHA-256, changes, or disappears after startup. Integrity failure is sticky for that process: restoring a file does not silently resume service; restart is required for complete validation and a new snapshot.

The M4 interface adds Start Cycle and End Cycle controls while preserving the accepted Selected Cycle selector and full-unit API behavior. The chart displays only actual observations inside the selected range; it does not interpolate, smooth, normalize, reorder, or fill values. `FULL_UNIT_STATISTICS` remain separate from the arithmetic `SELECTED_RANGE_STATISTICS` shown for the displayed points.

Generate Prompt creates a bounded evidence prompt from the currently loaded Split, Unit, range, Selected Cycle and Sensor snapshot. It separates observed data, derived statistics, analysis questions and limitations. Any selection transition immediately invalidates the preview and disables Copy Prompt until the new evidence is loaded and the user generates a new prompt. Copy uses the browser Clipboard API and reports success or failure without hiding the manually selectable preview.

The raw files remain local and untracked. The server has no upload endpoint, external API, CDN, analytics, or full-dataset download route.

## Browser test dependency

The application itself uses only Python's standard library. Actual Browser UAT uses the pinned development dependency:

```powershell
python -m pip install --user -r web/requirements-dev.txt
```

The test launches the locally installed Microsoft Edge Chromium executable; it does not download or commit a browser binary.

## Reproducible tests

```powershell
python -m unittest discover -s tests -p "test_fd001.py" -v
python -m unittest discover -s tests -p "test_fd001_api.py" -v
python -m unittest discover -s tests -p "test_fd001_web.py" -v
python -m unittest discover -s tests -p "test_fd001_browser.py" -v
python -m unittest discover -s tests -p "test_fd001_integration.py" -v
python -m unittest discover -s tests -p "test_fd001_integration_browser.py" -v
python -m unittest discover -s tests -p "test_fd001_evidence_prompt.py" -v
python -m unittest discover -s tests -p "test_fd001_m4_browser.py" -v
```

All commands must be run from the repository root so `tools.profile_fd001` and the local data paths resolve consistently.

The browser suite retains the original 15 UAT cases and adds deterministic response-order tests. These deliberately release stale Unit, Split, Sensor, Cycle and error responses after the current selection has succeeded, verifying the transaction/version guards without relying on ordinary network timing.

The M4 browser suite adds 13 real Microsoft Edge cases. Its two required comparison cases parse the authorized local TXT files directly as the independent oracle, then compare the bounded range with loopback API, DOM, SVG and generated prompt evidence. Screenshots are written only to a local temporary evidence directory and are not committed.

## Trust and interpretation limits

- Source trust policy: `STUDENT_TRUSTED_LOCAL_FILES`.
- External NASA provenance verification: `NOT_REQUIRED`; the UI does not claim otherwise.
- Sensor physical quantities and units: `UNVERIFIED`.
- Statistical trends and Tukey outliers are descriptive evidence, not confirmed faults or diagnoses.
- Train and Test Unit IDs belong to independent namespaces.
- Test RUL applies to the final observed cycle of a Test Unit; Train RUL is not supplied.

# FD001 Health Analytics — Local MVP

This read-only local application exposes the accepted FD001 Data Contract v1.0.0 through a Python standard-library HTTP server and a dependency-free browser UI.

## Start

From the repository root:

```powershell
python -m web.server
```

Open <http://127.0.0.1:8000/>. The server refuses non-loopback bind addresses. On startup it verifies the three authorized local raw files, validates their structure and RUL alignment, and builds one in-memory snapshot. Normal queries are disabled if a source file is missing, has an unexpected SHA-256, changes, or disappears after startup. Integrity failure is sticky for that process: restoring a file does not silently resume service; restart is required for complete validation and a new snapshot.

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
```

All commands must be run from the repository root so `tools.profile_fd001` and the local data paths resolve consistently.

The browser suite retains the original 15 UAT cases and adds deterministic response-order tests. These deliberately release stale Unit, Split, Sensor, Cycle and error responses after the current selection has succeeded, verifying the transaction/version guards without relying on ordinary network timing.

## Trust and interpretation limits

- Source trust policy: `STUDENT_TRUSTED_LOCAL_FILES`.
- External NASA provenance verification: `NOT_REQUIRED`; the UI does not claim otherwise.
- Sensor physical quantities and units: `UNVERIFIED`.
- Statistical trends and Tukey outliers are descriptive evidence, not confirmed faults or diagnoses.
- Train and Test Unit IDs belong to independent namespaces.
- Test RUL applies to the final observed cycle of a Test Unit; Train RUL is not supplied.

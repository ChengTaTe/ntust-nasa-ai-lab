# FD001 Health Analytics User Guide

## Requirements

- Windows with Microsoft Edge Chromium installed at the standard project-tested location.
- Python 3.15.2 or a compatible Python 3 runtime.
- Local accepted FD001 files at `data/FD001/train_FD001.txt`, `test_FD001.txt` and `RUL_FD001.txt`.
- Browser testing only: `python -m pip install --user -r web/requirements-dev.txt`.

The application itself uses Python's standard library and local Vanilla JavaScript. Do not download replacement raw data or publish the local sources.

## Start and stop

From the repository root:

```powershell
python -m web.server
```

Open `http://127.0.0.1:8000/`. A valid startup shows `LOCAL_DATA_VERIFIED`. Stop the server with `Ctrl+C` in the starting terminal. The server accepts loopback binding only; there is no authorized public deployment.

## Complete workflow

1. Choose Train or Test. Unit IDs belong to separate namespaces.
2. Choose an Engine Unit.
3. Choose Start and End Cycle; only actual observed Cycles are offered.
4. Choose a Selected Cycle inside that range.
5. Choose one of the canonical fields `sensor_01` through `sensor_21`.
6. Inspect the selected value, three operational settings, 26-field raw row, exact source locator and displayed-range chart.
7. Distinguish `FULL_UNIT_STATISTICS` from `SELECTED_RANGE_STATISTICS`.
8. Select Generate Prompt. Review all four sections before copying.
9. Select Copy Prompt. The application does not send it to an external LLM.

Test RUL is supplied only for the final observed Cycle of a Test Unit. It is not a prediction and is not based on the selected Cycle. Train RUL is not applicable.

## Fail-closed behavior and recovery

Required response fields are validated before evidence is rendered. A missing, null, wrong-type, non-finite or inconsistent required observation produces a `malformed-response` error, clears stale observation/chart/prompt evidence and disables Generate and Copy. This is different from legitimate undefined derived statistics: a constant-series Pearson correlation is JSON `null` and displays as `UNDEFINED`.

For an unavailable server, restore the local process and reload the page. For a transient or malformed response, restore the valid service and change/reload the current selection. Generate a new prompt; do not reuse an old preview. A web page cannot retract text copied to the operating-system Clipboard before an error occurred.

## Tests

Run each command from the repository root:

```powershell
python -m unittest discover -s tests -p "test_fd001.py" -v
python -m unittest discover -s tests -p "test_fd001_api.py" -v
python -m unittest discover -s tests -p "test_fd001_web.py" -v
python -m unittest discover -s tests -p "test_fd001_browser.py" -v
python -m unittest discover -s tests -p "test_fd001_integration.py" -v
python -m unittest discover -s tests -p "test_fd001_integration_browser.py" -v
python -m unittest discover -s tests -p "test_fd001_evidence_prompt.py" -v
python -m unittest discover -s tests -p "test_fd001_m4_browser.py" -v
python -m unittest discover -s tests -p "test_fd001_m5_browser.py" -v
```

The M5 suite uses real Edge, controlled response interception and a real secondary loopback-server shutdown/restart. Screenshots are private temporary evidence and are not repository deliverables.

## Protection and interpretation limits

- Raw data remains local, read-only and untracked.
- No full index, full series, CSV or screenshot is published.
- Source policy is `STUDENT_TRUSTED_LOCAL_FILES`, not independent NASA provenance verification.
- Sensor physical names and units remain unverified.
- Statistics are descriptive and do not establish causality, diagnosis or RUL prediction.
- If source integrity fails, restart is required after restoring the accepted files.

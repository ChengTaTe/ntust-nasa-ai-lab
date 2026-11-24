"""Read-only HTTP API adapter for the accepted FD001 data contract."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any, Mapping

from tools import profile_fd001 as fd


EXPECTED_SOURCE_HASHES = {
    "train": "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8",
    "test": "3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851",
    "rul": "a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca",
}
SOURCE_FILES = {
    "train": "data/FD001/train_FD001.txt",
    "test": "data/FD001/test_FD001.txt",
    "rul": "data/FD001/RUL_FD001.txt",
}
ERROR_STATUS = {
    "INVALID_SPLIT": 400,
    "UNKNOWN_UNIT": 404,
    "INVALID_CYCLE": 400,
    "UNKNOWN_SENSOR": 400,
    "MISSING_DATA": 503,
    "EMPTY_QUERY_RESULT": 404,
    "UNSUPPORTED_RUL_QUERY": 400,
    "INVALID_REQUEST": 400,
    "METHOD_NOT_ALLOWED": 405,
    "NOT_FOUND": 404,
    "SOURCE_INTEGRITY_FAILURE": 503,
    "INTERNAL_ERROR": 500,
}


class APIError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _finite(value: Any) -> Any:
    """Recursively reject non-standard JSON numbers instead of emitting NaN."""
    if isinstance(value, float) and not math.isfinite(value):
        raise APIError("MISSING_DATA", "A non-finite value cannot be represented.")
    if isinstance(value, dict):
        return {key: _finite(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_finite(item) for item in value]
    return value


class FD001API:
    """Validated in-memory FD001 snapshot exposed through bounded queries."""

    def __init__(self, project_root: Path | str | None = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parents[1]).resolve()
        self.data_root = self.project_root / "data" / "FD001"
        self._verified_hashes: dict[str, str] = {}
        self.catalog: fd.FD001Catalog | None = None
        self.analysis: dict[str, Any] | None = None
        self.integrity_error: str | None = None
        self._load_snapshot()

    def _current_hashes(self) -> dict[str, str]:
        hashes: dict[str, str] = {}
        for split, relative in SOURCE_FILES.items():
            path = self.project_root / relative
            if not path.is_file():
                raise APIError("SOURCE_INTEGRITY_FAILURE", f"Required {split} source is unavailable.")
            hashes[split] = _sha256(path)
        return hashes

    def _load_snapshot(self) -> None:
        try:
            hashes = self._current_hashes()
            if hashes != EXPECTED_SOURCE_HASHES:
                raise APIError("SOURCE_INTEGRITY_FAILURE", "FD001 source hash validation failed.")
            analysis = fd.build_analysis(self.data_root, self.project_root)
            self.analysis = analysis
            self.catalog = fd.FD001Catalog(
                analysis["datasets"]["train"],
                analysis["datasets"]["test"],
                analysis["datasets"]["rul"],
                analysis["quality"],
                analysis["trends"],
            )
            self._verified_hashes = hashes
            self.integrity_error = None
        except (OSError, fd.ValidationError, APIError) as exc:
            self.catalog = None
            self.analysis = None
            self.integrity_error = str(exc)

    def _require_snapshot(self) -> fd.FD001Catalog:
        if self.integrity_error or self.catalog is None:
            raise APIError("SOURCE_INTEGRITY_FAILURE", "Validated FD001 data is unavailable.")
        try:
            if self._current_hashes() != self._verified_hashes:
                self.integrity_error = "FD001 source changed after snapshot validation."
                self.catalog = None
                raise APIError("SOURCE_INTEGRITY_FAILURE", self.integrity_error)
        except OSError as exc:
            self.integrity_error = str(exc)
            self.catalog = None
            raise APIError("SOURCE_INTEGRITY_FAILURE", "FD001 source revalidation failed.") from exc
        return self.catalog

    @staticmethod
    def _params(params: Mapping[str, list[str]], required: set[str], allowed: set[str]) -> dict[str, str]:
        if set(params) - allowed:
            raise APIError("INVALID_REQUEST", "Unsupported query parameter.")
        if required - set(params):
            raise APIError("INVALID_REQUEST", "A required query parameter is missing.")
        if any(len(values) != 1 or values[0] == "" for values in params.values()):
            raise APIError("INVALID_REQUEST", "Query parameters must be present exactly once.")
        return {key: values[0] for key, values in params.items()}

    @staticmethod
    def _positive(value: str, name: str) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise APIError("INVALID_REQUEST", f"{name} must be a positive integer.") from exc
        if parsed <= 0 or str(parsed) != value:
            raise APIError("INVALID_REQUEST", f"{name} must be a positive integer.")
        return parsed

    @staticmethod
    def _row_payload(row: fd.RawRow) -> dict[str, Any]:
        fields: dict[str, dict[str, Any]] = {}
        for index, name in enumerate(fd.FIELD_NAMES, start=1):
            fields[name] = row.field_locator(index)
        return {
            "dataset_id": fd.DATASET_ID,
            "dataset_split": row.dataset_split,
            "unit_id": row.unit_id,
            "cycle": row.cycle,
            "fields": fields,
            "source_locator": {
                "source_file": row.source_file,
                "source_sha256": row.source_sha256,
                "raw_line_number": row.raw_line_number,
                "parsed_row_index": row.parsed_row_index,
            },
        }

    def query(self, path: str, params: Mapping[str, list[str]]) -> Any:
        if path == "/api/v1/status":
            values = self._params(params, set(), set())
            del values
            available = self.catalog is not None and self.integrity_error is None
            if available:
                self._require_snapshot()
            return {
                "dataset_id": fd.DATASET_ID,
                "contract_version": fd.CONTRACT_VERSION,
                "source_trust_policy": "STUDENT_TRUSTED_LOCAL_FILES",
                "external_source_verification": "NOT_REQUIRED",
                "data_available": self.catalog is not None,
                "validation_status": "LOCAL_DATA_VERIFIED" if self.catalog is not None else "SOURCE_INTEGRITY_FAILURE",
            }

        catalog = self._require_snapshot()
        if path == "/api/v1/splits":
            self._params(params, set(), set())
            return {"dataset_splits": catalog.list_dataset_splits()}
        if path == "/api/v1/sensors":
            self._params(params, set(), set())
            return {"sensors": [{"sensor_id": name, "raw_column_index": index} for index, name in enumerate(catalog.list_sensors(), start=6)]}

        if path in {"/api/v1/units", "/api/v1/data-quality"}:
            values = self._params(params, {"split"}, {"split"})
            split = values["split"]
            if path.endswith("units"):
                return {"dataset_split": split, "units": catalog.list_units(split)}
            dataset = self.analysis["datasets"][split] if self.analysis else None
            quality = catalog.get_data_quality_summary(split)
            return {
                "dataset_split": split,
                "source_file": dataset.relative_path,
                "source_sha256": dataset.sha256,
                "quality_gate": "PASS" if quality["passed"] else "FAIL",
                "structure": self.analysis["structure"][split],
                "quality": quality,
                "limitations": [
                    "Statistical outliers are not confirmed faults.",
                    "Sensor physical names and units remain UNVERIFIED.",
                    "Source identity follows STUDENT_TRUSTED_LOCAL_FILES; external NASA provenance was not independently verified.",
                ],
            }

        if path == "/api/v1/cycles":
            values = self._params(params, {"split", "unit_id"}, {"split", "unit_id"})
            unit_id = self._positive(values["unit_id"], "unit_id")
            return {"dataset_split": values["split"], "unit_id": unit_id, "cycles": catalog.list_cycles(values["split"], unit_id)}

        if path in {"/api/v1/raw-row", "/api/v1/operational-settings"}:
            values = self._params(params, {"split", "unit_id", "cycle"}, {"split", "unit_id", "cycle"})
            unit_id = self._positive(values["unit_id"], "unit_id")
            cycle = self._positive(values["cycle"], "cycle")
            if path.endswith("raw-row"):
                return self._row_payload(catalog.get_raw_row(values["split"], unit_id, cycle))
            row = catalog.get_raw_row(values["split"], unit_id, cycle)
            result = catalog.get_operational_settings(values["split"], unit_id, cycle)
            result["locators"] = [row.field_locator(index) for index in range(3, 6)]
            return result

        if path in {"/api/v1/sensor-trend", "/api/v1/sensor-series"}:
            values = self._params(params, {"split", "unit_id", "sensor_id"}, {"split", "unit_id", "sensor_id"})
            unit_id = self._positive(values["unit_id"], "unit_id")
            sensor = values["sensor_id"]
            if path.endswith("sensor-trend"):
                return catalog.get_sensor_trend(values["split"], unit_id, sensor)
            if sensor not in fd.SENSOR_NAMES:
                raise fd.QueryError("UNKNOWN_SENSOR", f"Unknown sensor: {sensor}")
            rows = catalog.by_unit[catalog._split(values["split"])].get(unit_id)
            if rows is None:
                raise fd.QueryError("UNKNOWN_UNIT", f"Unknown unit {unit_id} in {values['split']}.")
            column = fd.FIELD_NAMES.index(sensor)
            return {
                "dataset_split": values["split"],
                "unit_id": unit_id,
                "sensor_id": sensor,
                "raw_column_index": column + 1,
                "source_file": rows[0].source_file,
                "source_sha256": rows[0].source_sha256,
                "cycle_start": rows[0].cycle,
                "cycle_end": rows[-1].cycle,
                "sample_count": len(rows),
                "points": [{"cycle": row.cycle, "value": row.values[column], "raw_line_number": row.raw_line_number, "parsed_row_index": row.parsed_row_index, "raw_value": row.tokens[column]} for row in rows],
            }

        if path == "/api/v1/test-rul":
            values = self._params(params, {"split", "unit_id"}, {"split", "unit_id"})
            return catalog.get_test_rul(values["split"], self._positive(values["unit_id"], "unit_id"))

        if path == "/api/v1/raw-source-locator":
            values = self._params(params, {"split", "unit_id", "cycle", "field_name"}, {"split", "unit_id", "cycle", "field_name"})
            return catalog.get_raw_source_locator(values["split"], self._positive(values["unit_id"], "unit_id"), self._positive(values["cycle"], "cycle"), values["field_name"])

        raise APIError("NOT_FOUND", "API endpoint not found.")

    def handle(self, path: str, params: Mapping[str, list[str]]) -> tuple[int, dict[str, Any]]:
        try:
            data = _finite(self.query(path, params))
            return 200, {"ok": True, "data": data, "error": None}
        except fd.QueryError as exc:
            return ERROR_STATUS.get(exc.code, 400), {"ok": False, "data": None, "error": {"code": exc.code, "message": str(exc)}}
        except APIError as exc:
            return ERROR_STATUS.get(exc.code, 500), {"ok": False, "data": None, "error": {"code": exc.code, "message": str(exc)}}
        except (KeyError, TypeError, ValueError):
            return 400, {"ok": False, "data": None, "error": {"code": "INVALID_REQUEST", "message": "Invalid request."}}

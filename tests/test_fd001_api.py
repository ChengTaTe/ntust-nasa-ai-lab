from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.profile_fd001 import QueryError
from web.api import FD001API


ROOT = Path(__file__).resolve().parents[1]


class FD001APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.api = FD001API(ROOT)
        if cls.api.integrity_error:
            raise RuntimeError(cls.api.integrity_error)

    def ok(self, path: str, **params):
        status, envelope = self.api.handle(path, {key: [str(value)] for key, value in params.items()})
        self.assertEqual(status, 200, envelope)
        self.assertTrue(envelope["ok"])
        self.assertIsNone(envelope["error"])
        json.dumps(envelope, allow_nan=False)
        return envelope["data"]

    def error(self, code: str, status_expected: int, path: str, **params) -> None:
        status, envelope = self.api.handle(path, {key: [str(value)] for key, value in params.items()})
        self.assertEqual(status, status_expected)
        self.assertFalse(envelope["ok"])
        self.assertIsNone(envelope["data"])
        self.assertEqual(envelope["error"]["code"], code)

    def isolated_snapshot(self) -> FD001API:
        isolated = object.__new__(FD001API)
        isolated.project_root = self.api.project_root
        isolated.data_root = self.api.data_root
        isolated._verified_hashes = dict(self.api._verified_hashes)
        isolated.catalog = self.api.catalog
        isolated.analysis = self.api.analysis
        isolated.integrity_error = None
        return isolated

    def test_status_and_contract_identity(self) -> None:
        data = self.ok("/api/v1/status")
        self.assertEqual(data["dataset_id"], "NASA_CMAPSS_FD001_LOCAL")
        self.assertEqual(data["contract_version"], "1.0.0")
        self.assertEqual(data["validation_status"], "LOCAL_DATA_VERIFIED")

    def test_ten_contract_queries_and_web_series(self) -> None:
        self.assertEqual(self.ok("/api/v1/splits")["dataset_splits"], ["train", "test"])
        self.assertEqual(len(self.ok("/api/v1/units", split="train")["units"]), 100)
        self.assertEqual(self.ok("/api/v1/cycles", split="train", unit_id=1)["cycles"][0], 1)
        self.assertEqual(len(self.ok("/api/v1/sensors")["sensors"]), 21)
        row = self.ok("/api/v1/raw-row", split="train", unit_id=1, cycle=1)
        self.assertEqual(len(row["fields"]), 26)
        self.assertEqual(self.ok("/api/v1/sensor-trend", split="train", unit_id=1, sensor_id="sensor_01")["sample_count"], 192)
        self.assertEqual(len(self.ok("/api/v1/operational-settings", split="train", unit_id=1, cycle=1)["locators"]), 3)
        self.assertEqual(self.ok("/api/v1/data-quality", split="train")["quality_gate"], "PASS")
        self.assertEqual(self.ok("/api/v1/test-rul", split="test", unit_id=1)["rul_cycles"], 112)
        locator = self.ok("/api/v1/raw-source-locator", split="train", unit_id=1, cycle=1, field_name="sensor_01")
        self.assertEqual(locator["raw_column_index"], 6)
        series = self.ok("/api/v1/sensor-series", split="train", unit_id=1, sensor_id="sensor_02")
        self.assertEqual(len(series["points"]), series["sample_count"])

    def test_known_train_and_test_traceability(self) -> None:
        for split in ("train", "test"):
            with self.subTest(split=split):
                locator = self.ok("/api/v1/raw-source-locator", split=split, unit_id=1, cycle=1, field_name="sensor_01")
                self.assertEqual(locator["raw_line_number"], 1)
                self.assertEqual(locator["parsed_row_index"], 0)
                self.assertEqual(locator["raw_column_index"], 6)
                self.assertEqual(locator["raw_value"], "518.67")
                self.assertEqual(locator["parsed_value"], 518.67)

    def test_middle_end_nonconstant_and_cycle_limits(self) -> None:
        for split, unit, cycle in (("train", 50, 100), ("train", 100, 200), ("test", 50, 50), ("test", 100, 100)):
            cycles = self.ok("/api/v1/cycles", split=split, unit_id=unit)["cycles"]
            selected = min(cycle, cycles[-1])
            row = self.ok("/api/v1/raw-row", split=split, unit_id=unit, cycle=selected)
            self.assertEqual(row["cycle"], selected)
        series = self.ok("/api/v1/sensor-series", split="train", unit_id=1, sensor_id="sensor_02")
        self.assertGreater(len({point["value"] for point in series["points"]}), 1)
        self.assertNotEqual(
            self.ok("/api/v1/cycles", split="train", unit_id=1)["cycles"][-1],
            self.ok("/api/v1/cycles", split="train", unit_id=2)["cycles"][-1],
        )

    def test_split_namespace_isolation(self) -> None:
        train = self.ok("/api/v1/raw-row", split="train", unit_id=1, cycle=1)
        test = self.ok("/api/v1/raw-row", split="test", unit_id=1, cycle=1)
        self.assertNotEqual(train["source_locator"]["source_sha256"], test["source_locator"]["source_sha256"])

    def test_all_sensors_and_raw_columns(self) -> None:
        sensors = self.ok("/api/v1/sensors")["sensors"]
        self.assertEqual([item["raw_column_index"] for item in sensors], list(range(6, 27)))
        for item in sensors:
            locator = self.ok("/api/v1/raw-source-locator", split="test", unit_id=1, cycle=1, field_name=item["sensor_id"])
            self.assertEqual(locator["raw_column_index"], item["raw_column_index"])

    def test_constant_sensor_preserves_undefined_correlation(self) -> None:
        trend = self.ok("/api/v1/sensor-trend", split="train", unit_id=1, sensor_id="sensor_01")
        self.assertEqual(trend["direction"], "flat")
        self.assertIsNone(trend["pearson_correlation"])
        self.assertFalse(any(isinstance(value, float) and not math.isfinite(value) for value in trend.values()))

    def test_contract_error_boundaries(self) -> None:
        self.error("INVALID_SPLIT", 400, "/api/v1/units", split="rul")
        self.error("UNKNOWN_UNIT", 404, "/api/v1/cycles", split="train", unit_id=999)
        self.error("INVALID_CYCLE", 400, "/api/v1/raw-row", split="train", unit_id=1, cycle=9999)
        self.error("UNKNOWN_SENSOR", 400, "/api/v1/sensor-trend", split="train", unit_id=1, sensor_id="sensor_99")
        self.error("MISSING_DATA", 503, "/api/v1/raw-source-locator", split="train", unit_id=1, cycle=1, field_name="bad")
        self.error("UNSUPPORTED_RUL_QUERY", 400, "/api/v1/test-rul", split="train", unit_id=1)
        self.error("NOT_FOUND", 404, "/api/v1/nope")

    def test_invalid_split_routes_preserve_contract_error(self) -> None:
        routes = (
            ("/api/v1/units", {"split": "invalid"}),
            ("/api/v1/cycles", {"split": "invalid", "unit_id": 1}),
            ("/api/v1/raw-row", {"split": "invalid", "unit_id": 1, "cycle": 1}),
            ("/api/v1/sensor-trend", {"split": "invalid", "unit_id": 1, "sensor_id": "sensor_01"}),
            ("/api/v1/operational-settings", {"split": "invalid", "unit_id": 1, "cycle": 1}),
            ("/api/v1/data-quality", {"split": "invalid"}),
            ("/api/v1/test-rul", {"split": "invalid", "unit_id": 1}),
            ("/api/v1/raw-source-locator", {"split": "invalid", "unit_id": 1, "cycle": 1, "field_name": "sensor_01"}),
            ("/api/v1/sensor-series", {"split": "invalid", "unit_id": 1, "sensor_id": "sensor_01"}),
        )
        for route, params in routes:
            with self.subTest(route=route):
                self.error("INVALID_SPLIT", 400, route, **params)
        self.assertEqual(self.ok("/api/v1/data-quality", split="train")["quality_gate"], "PASS")

    def test_empty_query_result_boundary_with_isolated_substitute(self) -> None:
        with mock.patch.object(
            self.api.catalog,
            "list_units",
            side_effect=QueryError("EMPTY_QUERY_RESULT", "Valid query returned no rows."),
        ):
            self.error("EMPTY_QUERY_RESULT", 404, "/api/v1/units", split="train")

    def test_invalid_missing_duplicate_and_extra_parameters(self) -> None:
        self.error("INVALID_REQUEST", 400, "/api/v1/units")
        status, payload = self.api.handle("/api/v1/units", {"split": ["train", "test"]})
        self.assertEqual((status, payload["error"]["code"]), (400, "INVALID_REQUEST"))
        self.error("INVALID_REQUEST", 400, "/api/v1/units", split="train", file="secret")
        self.error("INVALID_REQUEST", 400, "/api/v1/cycles", split="train", unit_id="01")

    def test_required_source_missing_disables_queries_and_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            broken = FD001API(Path(temp))
            status, payload = broken.handle("/api/v1/splits", {})
            self.assertEqual(status, 503)
            self.assertEqual(payload["error"]["code"], "SOURCE_INTEGRITY_FAILURE")
            status, payload = broken.handle("/api/v1/status", {})
            self.assertEqual(status, 200)
            self.assertFalse(payload["data"]["data_available"])
            self.assertEqual(payload["data"]["validation_status"], "SOURCE_INTEGRITY_FAILURE")

    def test_existing_sources_with_hash_mismatch_disable_queries(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data_root = root / "data" / "FD001"
            data_root.mkdir(parents=True)
            for filename in ("train_FD001.txt", "test_FD001.txt", "RUL_FD001.txt"):
                (data_root / filename).write_text("present but not accepted\n", encoding="ascii")
            broken = FD001API(root)
            self.assertIn("hash validation failed", broken.integrity_error)
            status, payload = broken.handle("/api/v1/units", {"split": ["train"]})
            self.assertEqual(status, 503)
            self.assertEqual(payload["error"]["code"], "SOURCE_INTEGRITY_FAILURE")

    def test_source_change_after_snapshot_is_sticky(self) -> None:
        isolated = self.isolated_snapshot()
        changed = dict(isolated._verified_hashes)
        changed["train"] = "0" * 64
        with mock.patch.object(isolated, "_current_hashes", return_value=changed):
            status, payload = isolated.handle("/api/v1/splits", {})
        self.assertEqual(status, 503)
        self.assertEqual(payload["error"]["code"], "SOURCE_INTEGRITY_FAILURE")
        self.assertIsNone(isolated.catalog)
        status, payload = isolated.handle("/api/v1/status", {})
        self.assertEqual(status, 200)
        self.assertFalse(payload["data"]["data_available"])
        status, payload = isolated.handle("/api/v1/splits", {})
        self.assertEqual(status, 503)
        self.assertEqual(payload["error"]["code"], "SOURCE_INTEGRITY_FAILURE")

    def test_source_disappearance_after_startup_requires_restart(self) -> None:
        isolated = self.isolated_snapshot()
        with mock.patch.object(isolated, "_current_hashes", side_effect=OSError("source disappeared")):
            status, payload = isolated.handle("/api/v1/units", {"split": ["train"]})
        self.assertEqual(status, 503)
        self.assertEqual(payload["error"]["code"], "SOURCE_INTEGRITY_FAILURE")
        self.assertIn("source disappeared", isolated.integrity_error)
        # Even though the real files are visible again after the substitute is
        # removed, this process cannot resume without full startup validation.
        status, payload = isolated.handle("/api/v1/units", {"split": ["train"]})
        self.assertEqual(status, 503)
        self.assertEqual(payload["error"]["code"], "SOURCE_INTEGRITY_FAILURE")


if __name__ == "__main__":
    unittest.main()

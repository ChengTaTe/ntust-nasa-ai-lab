from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

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

    def test_invalid_missing_duplicate_and_extra_parameters(self) -> None:
        self.error("INVALID_REQUEST", 400, "/api/v1/units")
        status, payload = self.api.handle("/api/v1/units", {"split": ["train", "test"]})
        self.assertEqual((status, payload["error"]["code"]), (400, "INVALID_REQUEST"))
        self.error("INVALID_REQUEST", 400, "/api/v1/units", split="train", file="secret")
        self.error("INVALID_REQUEST", 400, "/api/v1/cycles", split="train", unit_id="01")

    def test_source_hash_failure_disables_queries(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            broken = FD001API(Path(temp))
            status, payload = broken.handle("/api/v1/splits", {})
            self.assertEqual(status, 503)
            self.assertEqual(payload["error"]["code"], "SOURCE_INTEGRITY_FAILURE")


if __name__ == "__main__":
    unittest.main()

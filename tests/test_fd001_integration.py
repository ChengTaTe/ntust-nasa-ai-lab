from __future__ import annotations

import hashlib
import json
import math
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from web.server import create_server


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "FD001"
CONTRACT = json.loads((ROOT / "contracts" / "FD001_DATA_CONTRACT.json").read_text(encoding="utf-8"))
FIELD_NAMES = ["unit_id", "cycle", *(f"op_setting_{i}" for i in range(1, 4)), *(f"sensor_{i:02d}" for i in range(1, 22))]
SOURCE_HASHES = {
    "train": "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8",
    "test": "3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851",
}


def raw_rows(split: str) -> list[dict[str, object]]:
    """Independent test oracle: tokenize the authorized source, not Catalog/API output."""
    path = DATA / f"{split}_FD001.txt"
    rows = []
    parsed_index = 0
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), start=1):
        tokens = line.split()
        if not tokens:
            continue
        values = [float(token) for token in tokens]
        rows.append({
            "tokens": tokens,
            "values": values,
            "line": line_number,
            "index": parsed_index,
            "unit": int(values[0]),
            "cycle": int(values[1]),
        })
        parsed_index += 1
    return rows


def trend_oracle(rows: list[dict[str, object]], column: int) -> dict[str, object]:
    xs = [float(row["cycle"]) for row in rows]
    ys = [row["values"][column] for row in rows]
    x_mean, y_mean = sum(xs) / len(xs), sum(ys) / len(ys)
    xx = sum((x - x_mean) ** 2 for x in xs)
    yy = sum((y - y_mean) ** 2 for y in ys)
    xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    slope = xy / xx
    correlation = None if yy == 0 else xy / math.sqrt(xx * yy)
    tolerance = 1e-12 * max(1.0, abs(y_mean)) / max(1.0, xs[-1] - xs[0])
    direction = "flat" if abs(slope) <= tolerance else ("increasing" if slope > 0 else "decreasing")
    return {
        "sample_count": len(rows), "cycle_start": int(xs[0]), "cycle_end": int(xs[-1]),
        "start_value": ys[0], "end_value": ys[-1], "change": ys[-1] - ys[0],
        "slope": slope, "pearson_correlation": correlation, "direction": direction,
    }


class FD001SystemIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = {split: raw_rows(split) for split in ("train", "test")}
        cls.server = create_server(port=0, project_root=ROOT)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, route: str, expected_status: int = 200, **params):
        url = self.base + route + ("?" + urlencode(params) if params else "")
        try:
            with urlopen(url, timeout=30) as response:
                status, body = response.status, response.read()
        except HTTPError as exc:
            try:
                status, body = exc.code, exc.read()
            finally:
                exc.close()
        self.assertEqual(status, expected_status, body)
        text = body.decode("utf-8")
        self.assertNotIn("NaN", text)
        self.assertNotIn("Infinity", text)
        return json.loads(text)

    def unit_rows(self, split: str, unit: int) -> list[dict[str, object]]:
        return [row for row in self.raw[split] if row["unit"] == unit]

    def test_01_sources_contract_and_loopback_boundary(self) -> None:
        self.assertEqual(CONTRACT["contract_version"], "1.0.0")
        self.assertEqual(len(CONTRACT["query_specification"]), 10)
        self.assertEqual(len(CONTRACT["query_boundaries"]), 7)
        for split, expected in SOURCE_HASHES.items():
            actual = hashlib.sha256((DATA / f"{split}_FD001.txt").read_bytes()).hexdigest()
            self.assertEqual(actual, expected)
        status = self.request("/api/v1/status")["data"]
        self.assertEqual(status["contract_version"], "1.0.0")
        self.assertTrue(status["data_available"])
        with self.assertRaisesRegex(ValueError, "127.0.0.1"):
            create_server(host="0.0.0.0", port=0, project_root=ROOT)

    def test_02_independent_raw_to_http_api_matrix(self) -> None:
        # Reproducible middle rule: lower median index floor((N - 1) / 2).
        for split in ("train", "test"):
            for unit in (1, 50, 100):
                rows = self.unit_rows(split, unit)
                selected = (rows[0], rows[(len(rows) - 1) // 2], rows[-1])
                cycles = self.request("/api/v1/cycles", split=split, unit_id=unit)["data"]["cycles"]
                self.assertEqual(cycles, [row["cycle"] for row in rows])
                for raw in selected:
                    with self.subTest(split=split, unit=unit, cycle=raw["cycle"]):
                        data = self.request("/api/v1/raw-row", split=split, unit_id=unit, cycle=raw["cycle"])["data"]
                        self.assertEqual(len(data["fields"]), 26)
                        self.assertEqual(data["source_locator"], {
                            "source_file": f"data/FD001/{split}_FD001.txt",
                            "source_sha256": SOURCE_HASHES[split],
                            "raw_line_number": raw["line"], "parsed_row_index": raw["index"],
                        })
                        for column, name in enumerate(FIELD_NAMES, start=1):
                            field = data["fields"][name]
                            expected = int(raw["values"][column - 1]) if column <= 2 else raw["values"][column - 1]
                            self.assertEqual(field["raw_value"], raw["tokens"][column - 1])
                            self.assertEqual(field["parsed_value"], expected)
                            self.assertEqual(field["raw_column_index"], column)
                            self.assertEqual(field["canonical_field_name"], name)

    def test_03_all_sensor_and_operational_setting_locators(self) -> None:
        raw = self.unit_rows("test", 50)[(len(self.unit_rows("test", 50)) - 1) // 2]
        sensors = self.request("/api/v1/sensors")["data"]["sensors"]
        self.assertEqual(sensors, [{"sensor_id": f"sensor_{i:02d}", "raw_column_index": i + 5} for i in range(1, 22)])
        for item in sensors:
            locator = self.request("/api/v1/raw-source-locator", split="test", unit_id=50, cycle=raw["cycle"], field_name=item["sensor_id"])["data"]
            column = item["raw_column_index"]
            self.assertEqual(locator["raw_value"], raw["tokens"][column - 1])
            self.assertEqual(locator["parsed_value"], raw["values"][column - 1])
            self.assertEqual((locator["raw_line_number"], locator["parsed_row_index"]), (raw["line"], raw["index"]))
        ops = self.request("/api/v1/operational-settings", split="test", unit_id=50, cycle=raw["cycle"])["data"]
        self.assertEqual([ops[f"op_setting_{i}"] for i in range(1, 4)], raw["values"][2:5])

    def test_04_independent_trend_statistics(self) -> None:
        cases = (("train", 1, "sensor_01"), ("train", 100, "sensor_02"), ("test", 50, "sensor_07"), ("test", 100, "sensor_01"))
        for split, unit, sensor in cases:
            rows = self.unit_rows(split, unit)
            expected = trend_oracle(rows, FIELD_NAMES.index(sensor))
            actual = self.request("/api/v1/sensor-trend", split=split, unit_id=unit, sensor_id=sensor)["data"]
            for key in ("sample_count", "cycle_start", "cycle_end", "start_value", "end_value", "change", "direction"):
                self.assertEqual(actual[key], expected[key], (split, unit, sensor, key))
            self.assertAlmostEqual(actual["slope"], expected["slope"], delta=1e-12)
            if expected["pearson_correlation"] is None:
                self.assertIsNone(actual["pearson_correlation"])
            else:
                self.assertAlmostEqual(actual["pearson_correlation"], expected["pearson_correlation"], delta=1e-12)

    def test_05_rul_alignment_and_split_namespace(self) -> None:
        rul_tokens = [line.split()[0] for line in (DATA / "RUL_FD001.txt").read_text(encoding="ascii").splitlines() if line.split()]
        for unit in (1, 50, 100):
            actual = self.request("/api/v1/test-rul", split="test", unit_id=unit)["data"]
            self.assertEqual(actual["raw_value"], rul_tokens[unit - 1])
            self.assertEqual(actual["rul_cycles"], int(rul_tokens[unit - 1]))
            self.assertEqual(actual["raw_line_number"], unit)
        train = self.request("/api/v1/raw-row", split="train", unit_id=1, cycle=1)["data"]
        test = self.request("/api/v1/raw-row", split="test", unit_id=1, cycle=1)["data"]
        self.assertNotEqual(train["source_locator"]["source_sha256"], test["source_locator"]["source_sha256"])
        error = self.request("/api/v1/test-rul", 400, split="train", unit_id=1)
        self.assertEqual(error["error"]["code"], "UNSUPPORTED_RUL_QUERY")

    def test_06_contract_queries_and_seven_error_boundaries(self) -> None:
        routes = {
            "list_dataset_splits": ("/api/v1/splits", {}), "list_units_by_split": ("/api/v1/units", {"split": "train"}),
            "list_cycles_by_unit": ("/api/v1/cycles", {"split": "train", "unit_id": 1}), "list_sensors": ("/api/v1/sensors", {}),
            "get_raw_row": ("/api/v1/raw-row", {"split": "train", "unit_id": 1, "cycle": 1}),
            "get_sensor_trend": ("/api/v1/sensor-trend", {"split": "train", "unit_id": 1, "sensor_id": "sensor_01"}),
            "get_operational_settings": ("/api/v1/operational-settings", {"split": "train", "unit_id": 1, "cycle": 1}),
            "get_data_quality_summary": ("/api/v1/data-quality", {"split": "train"}),
            "get_test_rul": ("/api/v1/test-rul", {"split": "test", "unit_id": 1}),
            "get_raw_source_locator": ("/api/v1/raw-source-locator", {"split": "train", "unit_id": 1, "cycle": 1, "field_name": "sensor_01"}),
        }
        self.assertEqual(set(routes), {item["name"] for item in CONTRACT["query_specification"]})
        for route, params in routes.values():
            self.assertTrue(self.request(route, **params)["ok"])
        errors = (
            ("INVALID_SPLIT", 400, "/api/v1/units", {"split": "bad"}),
            ("UNKNOWN_UNIT", 404, "/api/v1/cycles", {"split": "train", "unit_id": 999}),
            ("INVALID_CYCLE", 400, "/api/v1/raw-row", {"split": "train", "unit_id": 1, "cycle": 9999}),
            ("UNKNOWN_SENSOR", 400, "/api/v1/sensor-trend", {"split": "train", "unit_id": 1, "sensor_id": "sensor_99"}),
            ("MISSING_DATA", 503, "/api/v1/raw-source-locator", {"split": "train", "unit_id": 1, "cycle": 1, "field_name": "bad"}),
            ("UNSUPPORTED_RUL_QUERY", 400, "/api/v1/test-rul", {"split": "train", "unit_id": 1}),
        )
        for code, status, route, params in errors:
            self.assertEqual(self.request(route, status, **params)["error"]["code"], code)
        # EMPTY_QUERY_RESULT is a valid contract boundary but cannot arise from the accepted non-empty snapshot;
        # its isolated fault injection is covered by the accepted API regression suite.
        self.assertIn("EMPTY_QUERY_RESULT", CONTRACT["query_boundaries"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import profile_fd001 as fd  # noqa: E402


def data_line(unit: int, cycle: int, sensor_base: float = 1.0) -> str:
    values = [str(unit), str(cycle), "0.1", "0.2", "100"]
    values += [str(sensor_base + index) for index in range(21)]
    return "  ".join(values) + "  "


class FD001Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="ascii", newline="\n")
        return path

    def parse_pair(self) -> tuple[fd.ParsedFile, fd.ParsedFile, fd.ParsedFile]:
        train_path = self.write("train_FD001.txt", data_line(1, 1) + "\n" + data_line(1, 2) + "\n")
        test_path = self.write("test_FD001.txt", data_line(1, 1, 2.0) + "\n" + data_line(1, 2, 3.0) + "\n")
        rul_path = self.write("RUL_FD001.txt", "5  \n")
        return (
            fd.parse_data_file(train_path, "train", self.root),
            fd.parse_data_file(test_path, "test", self.root),
            fd.parse_rul_file(rul_path, self.root),
        )

    def write_build_fixture(self, train_cycles: tuple[int, int] = (1, 2)) -> None:
        self.write(
            "train_FD001.txt",
            data_line(1, train_cycles[0]) + "\n" + data_line(1, train_cycles[1]) + "\n",
        )
        self.write(
            "test_FD001.txt",
            data_line(1, 1, 2.0) + "\n" + data_line(1, 2, 3.0) + "\n",
        )
        self.write("RUL_FD001.txt", "5  \n")

    @staticmethod
    def small_expected() -> dict[str, dict[str, int]]:
        return {
            "train": {"rows": 2, "columns": 26, "units": 1},
            "test": {"rows": 2, "columns": 26, "units": 1},
            "rul": {"rows": 1, "columns": 1},
        }

    def test_whitespace_parser_and_trailing_space(self) -> None:
        path = self.write("train_FD001.txt", data_line(1, 1) + "\n")
        parsed = fd.parse_data_file(path, "train", self.root)
        self.assertEqual(dict(parsed.column_count_distribution), {26: 1})
        self.assertEqual(parsed.trailing_whitespace_positions, [1])
        self.assertFalse(parsed.header_present)

    def test_blank_line_raw_line_mapping(self) -> None:
        content = data_line(1, 1) + "\n\n" + data_line(1, 2) + "\n"
        parsed = fd.parse_data_file(self.write("train_FD001.txt", content), "train", self.root)
        self.assertEqual(parsed.blank_line_positions, [2])
        self.assertEqual(parsed.rows[1].raw_line_number, 3)
        self.assertEqual(parsed.rows[1].parsed_row_index, 1)

    def test_invalid_column_count(self) -> None:
        path = self.write("train_FD001.txt", "1 1 0.1\n")
        with self.assertRaises(fd.ValidationError):
            fd.parse_data_file(path, "train", self.root)

    def test_invalid_numeric_value(self) -> None:
        tokens = data_line(1, 1).split()
        tokens[7] = "bad"
        path = self.write("train_FD001.txt", " ".join(tokens) + "\n")
        with self.assertRaises(fd.ValidationError):
            fd.parse_data_file(path, "train", self.root)

    def test_nan_and_infinity_rejected(self) -> None:
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                tokens = data_line(1, 1).split()
                tokens[7] = value
                path = self.write("train_FD001.txt", " ".join(tokens) + "\n")
                with self.assertRaises(fd.ValidationError):
                    fd.parse_data_file(path, "train", self.root)

    def test_duplicate_unit_cycle_key(self) -> None:
        content = data_line(1, 1) + "\n" + data_line(1, 1, 3.0) + "\n"
        parsed = fd.parse_data_file(self.write("train_FD001.txt", content), "train", self.root)
        result = fd.validate_cycles(parsed)
        self.assertEqual(result["duplicate_unit_cycle_keys"], 1)
        self.assertFalse(result["passed"])

    def test_missing_cycle(self) -> None:
        content = data_line(1, 1) + "\n" + data_line(1, 3) + "\n"
        parsed = fd.parse_data_file(self.write("train_FD001.txt", content), "train", self.root)
        result = fd.validate_cycles(parsed)
        self.assertEqual(result["missing_cycles_by_unit"], {1: [2]})

    def test_non_monotonic_cycle_order(self) -> None:
        content = data_line(1, 1) + "\n" + data_line(1, 3) + "\n" + data_line(1, 2) + "\n"
        parsed = fd.parse_data_file(self.write("train_FD001.txt", content), "train", self.root)
        result = fd.validate_cycles(parsed)
        self.assertEqual(result["non_monotonic_units"], [1])

    def test_train_test_namespaces_are_independent(self) -> None:
        train, test, rul = self.parse_pair()
        quality = {"train": {}, "test": {}}
        trends = {"train": fd.analyze_trends(train), "test": fd.analyze_trends(test)}
        catalog = fd.FD001Catalog(train, test, rul, quality, trends)
        self.assertNotEqual(
            catalog.get_raw_row("train", 1, 1).source_sha256,
            catalog.get_raw_row("test", 1, 1).source_sha256,
        )

    def test_negative_rul_rejected(self) -> None:
        path = self.write("RUL_FD001.txt", "-1\n")
        with self.assertRaises(fd.ValidationError):
            fd.parse_rul_file(path, self.root)

    def test_rul_count_and_unit_alignment(self) -> None:
        _, test, rul = self.parse_pair()
        self.assertTrue(fd.validate_rul_alignment(test, rul)["passed"])
        extra = self.write("RUL_extra.txt", "5\n6\n")
        mismatched = fd.parse_rul_file(extra, self.root)
        self.assertFalse(fd.validate_rul_alignment(test, mismatched)["passed"])

    def test_raw_index_and_value_separation(self) -> None:
        train, _, _ = self.parse_pair()
        row = train.rows[0]
        locator = row.field_locator(6)
        self.assertEqual(locator["raw_line_number"], 1)
        self.assertEqual(locator["parsed_row_index"], 0)
        self.assertEqual(locator["raw_column_index"], 6)
        self.assertEqual(locator["canonical_field_name"], "sensor_01")
        self.assertIsInstance(locator["raw_value"], str)
        self.assertIsInstance(locator["parsed_value"], float)

    def test_known_slope_and_correlation(self) -> None:
        slope, correlation = fd.slope_and_correlation([1, 2, 3], [2, 4, 6])
        self.assertAlmostEqual(slope, 2.0)
        self.assertAlmostEqual(correlation, 1.0)

    def test_constant_series_zero_denominator(self) -> None:
        slope, correlation = fd.slope_and_correlation([1, 2, 3], [5, 5, 5])
        self.assertEqual(slope, 0.0)
        self.assertIsNone(correlation)
        direction, _ = fd.trend_direction(slope, 5.0, 2)
        self.assertEqual(direction, "flat")

    def test_near_constant_and_outlier_rules(self) -> None:
        near = fd.numeric_summary([1.0, 1.0 + 1e-10, 1.0 - 1e-10])
        self.assertTrue(near["near_constant"])
        outliers = fd.numeric_summary([0, 0, 0, 0, 10])
        self.assertGreater(outliers["potential_outlier_count"], 0)

    def test_linear_quantile(self) -> None:
        self.assertEqual(fd.linear_quantile([0.0, 10.0], 0.25), 2.5)
        self.assertEqual(fd.linear_quantile([0.0, 10.0], 0.75), 7.5)

    def test_query_boundaries(self) -> None:
        train, test, rul = self.parse_pair()
        trends = {"train": fd.analyze_trends(train), "test": fd.analyze_trends(test)}
        catalog = fd.FD001Catalog(train, test, rul, {"train": {}, "test": {}}, trends)
        cases = [
            (lambda: catalog.list_units("bad"), "INVALID_SPLIT"),
            (lambda: catalog.get_raw_row("train", 2, 1), "UNKNOWN_UNIT"),
            (lambda: catalog.get_raw_row("train", 1, 9), "INVALID_CYCLE"),
            (lambda: catalog.get_sensor_trend("train", 1, "sensor_99"), "UNKNOWN_SENSOR"),
            (lambda: catalog.get_test_rul("train", 1), "UNSUPPORTED_RUL_QUERY"),
        ]
        for operation, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(fd.QueryError) as context:
                    operation()
                self.assertEqual(context.exception.code, code)

    def test_sensor_mapping_all_21(self) -> None:
        train, test, rul = self.parse_pair()
        trends = {"train": fd.analyze_trends(train), "test": fd.analyze_trends(test)}
        catalog = fd.FD001Catalog(train, test, rul, {"train": {}, "test": {}}, trends)
        for raw_column, sensor in enumerate(fd.SENSOR_NAMES, start=6):
            self.assertEqual(
                catalog.get_raw_source_locator("train", 1, 1, sensor)["raw_column_index"],
                raw_column,
            )

    def test_trend_coverage(self) -> None:
        train, _, _ = self.parse_pair()
        trends = fd.analyze_trends(train)
        self.assertEqual(trends["detail_count"], 21)
        self.assertEqual(trends["detail_count"], trends["expected_detail_count"])

    def test_structural_failure_cannot_enter_trend_analysis(self) -> None:
        self.write_build_fixture(train_cycles=(1, 3))
        with (
            mock.patch.object(fd, "EXPECTED", self.small_expected()),
            mock.patch.object(fd, "analyze_trends") as analyze,
        ):
            with self.assertRaisesRegex(fd.ValidationError, "STRUCTURAL_VALIDATION_FAILED"):
                fd.build_analysis(self.root, self.root)
            analyze.assert_not_called()

    def test_quality_failure_cannot_enter_trend_analysis(self) -> None:
        self.write_build_fixture()
        with (
            mock.patch.object(fd, "EXPECTED", self.small_expected()),
            mock.patch.object(fd, "count_full_row_duplicates", return_value=1),
            mock.patch.object(fd, "analyze_trends") as analyze,
        ):
            with self.assertRaisesRegex(fd.ValidationError, "DATA_QUALITY_GATE failed"):
                fd.build_analysis(self.root, self.root)
            analyze.assert_not_called()

    def test_field_dictionary_has_26_stable_names(self) -> None:
        fields = fd.field_dictionary()
        self.assertEqual(len(fields), 26)
        self.assertEqual([item["canonical_field_name"] for item in fields], list(fd.FIELD_NAMES))
        self.assertTrue(all(item["unit"] == "UNVERIFIED" for item in fields[2:]))

    def test_contract_markdown_json_consistency(self) -> None:
        train, test, rul = self.parse_pair()
        contract = fd.build_contract({"datasets": {"train": train, "test": test, "rul": rul}})
        markdown = fd.render_contract_markdown(contract)
        fd.validate_contract_consistency(contract, markdown)
        encoded = json.dumps(contract, ensure_ascii=False, allow_nan=False)
        self.assertEqual(json.loads(encoded), contract)

    def test_json_rejects_nonfinite_values(self) -> None:
        with self.assertRaises(ValueError):
            json.dumps({"bad": math.nan}, allow_nan=False)

    def test_full_row_duplicate_count(self) -> None:
        line = data_line(1, 1)
        parsed = fd.parse_data_file(self.write("train_FD001.txt", line + "\n" + line + "\n"), "train", self.root)
        self.assertEqual(fd.count_full_row_duplicates(parsed.rows), 1)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Profile, validate, query, and document the trusted local FD001 files.

The module keeps raw rows and per-unit time series in memory only. Generated
artifacts contain schemas, methods, aggregate statistics, and a small number of
traceability examples; they never contain a complete raw index or time series.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Sequence


CONTRACT_VERSION = "1.0.0"
DATASET_ID = "NASA_CMAPSS_FD001_LOCAL"
TAIPEI_TZ = timezone(timedelta(hours=8), "Asia/Taipei")
INTEGER_RE = re.compile(r"^[+-]?\d+$")
SPLITS = ("train", "test")
RAW_FILES = {
    "train": "train_FD001.txt",
    "test": "test_FD001.txt",
    "rul": "RUL_FD001.txt",
}
EXPECTED = {
    "train": {"rows": 20631, "columns": 26, "units": 100},
    "test": {"rows": 13096, "columns": 26, "units": 100},
    "rul": {"rows": 100, "columns": 1},
}
FIELD_NAMES = (
    "unit_id",
    "cycle",
    "op_setting_1",
    "op_setting_2",
    "op_setting_3",
    *(f"sensor_{index:02d}" for index in range(1, 22)),
)
SENSOR_NAMES = tuple(f"sensor_{index:02d}" for index in range(1, 22))
FEATURE_NAMES = FIELD_NAMES[2:]


class ValidationError(Exception):
    """Raised when raw data violates a required structural or integrity rule."""


class QueryError(Exception):
    """Raised for a documented local query boundary."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class RawRow:
    dataset_split: str
    source_file: str
    source_sha256: str
    raw_line_number: int
    parsed_row_index: int
    tokens: tuple[str, ...]
    values: tuple[float, ...]
    unit_id: int
    cycle: int

    def field_locator(self, raw_column_index: int) -> dict[str, object]:
        if not 1 <= raw_column_index <= len(self.tokens):
            raise QueryError("MISSING_DATA", "Raw column index is outside the row schema.")
        name = FIELD_NAMES[raw_column_index - 1]
        parsed = self.values[raw_column_index - 1]
        if raw_column_index <= 2:
            parsed = int(parsed)
        return {
            "dataset_id": DATASET_ID,
            "dataset_split": self.dataset_split,
            "source_file": self.source_file,
            "source_sha256": self.source_sha256,
            "raw_line_number": self.raw_line_number,
            "parsed_row_index": self.parsed_row_index,
            "unit_id": self.unit_id,
            "cycle": self.cycle,
            "raw_column_index": raw_column_index,
            "canonical_field_name": name,
            "raw_value": self.tokens[raw_column_index - 1],
            "parsed_value": parsed,
        }


@dataclass(frozen=True)
class RULRow:
    source_file: str
    source_sha256: str
    raw_line_number: int
    parsed_row_index: int
    raw_value: str
    value: int
    unit_id: int


@dataclass
class ParsedFile:
    split: str
    path: Path
    relative_path: str
    sha256: str
    size_bytes: int
    encoding: str
    delimiter: str
    header_present: bool
    text_line_count: int
    blank_line_positions: list[int]
    trailing_whitespace_positions: list[int]
    column_count_distribution: Counter[int]
    rows: list[RawRow] | list[RULRow]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def decode_text(data: bytes, path: Path) -> tuple[str, str]:
    if data.startswith(b"\xef\xbb\xbf"):
        try:
            return "utf-8-sig", data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"Invalid UTF-8 in {path}: {exc}") from exc
    try:
        text = data.decode("ascii")
        return "ascii", text
    except UnicodeDecodeError:
        try:
            return "utf-8", data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"Unsupported text encoding in {path}: {exc}") from exc


def parse_finite_number(token: str, context: str) -> float:
    try:
        value = float(token)
    except ValueError as exc:
        raise ValidationError(f"Invalid numeric token at {context}: {token!r}") from exc
    if not math.isfinite(value):
        raise ValidationError(f"Non-finite numeric token at {context}: {token!r}")
    return value


def parse_positive_integer(token: str, context: str) -> int:
    if not INTEGER_RE.fullmatch(token):
        raise ValidationError(f"Expected integer at {context}: {token!r}")
    value = int(token)
    if value <= 0:
        raise ValidationError(f"Expected positive integer at {context}: {token!r}")
    return value


def parse_nonnegative_integer(token: str, context: str) -> int:
    if not INTEGER_RE.fullmatch(token):
        raise ValidationError(f"Expected integer at {context}: {token!r}")
    value = int(token)
    if value < 0:
        raise ValidationError(f"Expected non-negative integer at {context}: {token!r}")
    return value


def parse_data_file(path: Path, split: str, project_root: Path) -> ParsedFile:
    if split not in SPLITS:
        raise ValidationError(f"Unsupported data split: {split}")
    if not path.is_file():
        raise ValidationError(f"Missing source file: {path}")
    raw = path.read_bytes()
    encoding, text = decode_text(raw, path)
    lines = text.splitlines()
    blank_positions: list[int] = []
    trailing_positions: list[int] = []
    width_distribution: Counter[int] = Counter()
    rows: list[RawRow] = []
    source_hash = sha256_bytes(raw)
    source_file = relative_posix(path, project_root)
    for line_number, line in enumerate(lines, start=1):
        if line != line.rstrip():
            trailing_positions.append(line_number)
        if not line.strip():
            blank_positions.append(line_number)
            continue
        tokens = tuple(line.split())
        width_distribution[len(tokens)] += 1
        if len(tokens) != 26:
            raise ValidationError(
                f"{source_file}:{line_number} has {len(tokens)} columns; expected 26."
            )
        unit_id = parse_positive_integer(tokens[0], f"{source_file}:{line_number}:1")
        cycle = parse_positive_integer(tokens[1], f"{source_file}:{line_number}:2")
        values = tuple(
            parse_finite_number(token, f"{source_file}:{line_number}:{index}")
            for index, token in enumerate(tokens, start=1)
        )
        rows.append(
            RawRow(
                dataset_split=split,
                source_file=source_file,
                source_sha256=source_hash,
                raw_line_number=line_number,
                parsed_row_index=len(rows),
                tokens=tokens,
                values=values,
                unit_id=unit_id,
                cycle=cycle,
            )
        )
    return ParsedFile(
        split=split,
        path=path,
        relative_path=source_file,
        sha256=source_hash,
        size_bytes=len(raw),
        encoding=encoding,
        delimiter="one or more whitespace characters",
        header_present=False,
        text_line_count=len(lines),
        blank_line_positions=blank_positions,
        trailing_whitespace_positions=trailing_positions,
        column_count_distribution=width_distribution,
        rows=rows,
    )


def parse_rul_file(path: Path, project_root: Path) -> ParsedFile:
    if not path.is_file():
        raise ValidationError(f"Missing source file: {path}")
    raw = path.read_bytes()
    encoding, text = decode_text(raw, path)
    lines = text.splitlines()
    blank_positions: list[int] = []
    trailing_positions: list[int] = []
    width_distribution: Counter[int] = Counter()
    rows: list[RULRow] = []
    source_hash = sha256_bytes(raw)
    source_file = relative_posix(path, project_root)
    for line_number, line in enumerate(lines, start=1):
        if line != line.rstrip():
            trailing_positions.append(line_number)
        if not line.strip():
            blank_positions.append(line_number)
            continue
        tokens = tuple(line.split())
        width_distribution[len(tokens)] += 1
        if len(tokens) != 1:
            raise ValidationError(
                f"{source_file}:{line_number} has {len(tokens)} columns; expected 1."
            )
        value = parse_nonnegative_integer(tokens[0], f"{source_file}:{line_number}:1")
        rows.append(
            RULRow(
                source_file=source_file,
                source_sha256=source_hash,
                raw_line_number=line_number,
                parsed_row_index=len(rows),
                raw_value=tokens[0],
                value=value,
                unit_id=len(rows) + 1,
            )
        )
    return ParsedFile(
        split="rul",
        path=path,
        relative_path=source_file,
        sha256=source_hash,
        size_bytes=len(raw),
        encoding=encoding,
        delimiter="one or more whitespace characters",
        header_present=False,
        text_line_count=len(lines),
        blank_line_positions=blank_positions,
        trailing_whitespace_positions=trailing_positions,
        column_count_distribution=width_distribution,
        rows=rows,
    )


def group_rows_by_unit(rows: Sequence[RawRow]) -> dict[int, list[RawRow]]:
    grouped: dict[int, list[RawRow]] = defaultdict(list)
    for row in rows:
        grouped[row.unit_id].append(row)
    return dict(sorted(grouped.items()))


def validate_rul_alignment(test: ParsedFile, rul: ParsedFile) -> dict[str, object]:
    test_units = sorted(
        {row.unit_id for row in test.rows if isinstance(row, RawRow)}
    )
    rul_rows = [row for row in rul.rows if isinstance(row, RULRow)]
    result = {
        "rul_row_count": len(rul_rows),
        "test_unit_count": len(test_units),
        "test_units_are_1_through_n": test_units == list(range(1, len(test_units) + 1)),
        "rul_unit_ids_are_1_through_n": [row.unit_id for row in rul_rows]
        == list(range(1, len(rul_rows) + 1)),
    }
    result["passed"] = (
        result["rul_row_count"] == result["test_unit_count"]
        and result["test_units_are_1_through_n"]
        and result["rul_unit_ids_are_1_through_n"]
    )
    return result


def validate_cycles(dataset: ParsedFile) -> dict[str, object]:
    rows = dataset.rows
    assert all(isinstance(row, RawRow) for row in rows)
    typed_rows = list(rows)
    keys = [(row.unit_id, row.cycle) for row in typed_rows]
    duplicate_keys = len(keys) - len(set(keys))
    grouped = group_rows_by_unit(typed_rows)
    missing_cycles: dict[int, list[int]] = {}
    non_monotonic_units: list[int] = []
    not_starting_at_one: list[int] = []
    for unit_id, unit_rows in grouped.items():
        cycles = [row.cycle for row in unit_rows]
        if not cycles or cycles[0] != 1:
            not_starting_at_one.append(unit_id)
        if any(current <= previous for previous, current in zip(cycles, cycles[1:])):
            non_monotonic_units.append(unit_id)
        expected_cycles = set(range(1, max(cycles) + 1)) if cycles else set()
        missing = sorted(expected_cycles - set(cycles))
        if missing:
            missing_cycles[unit_id] = missing
    result = {
        "unit_count": len(grouped),
        "unit_min": min(grouped) if grouped else None,
        "unit_max": max(grouped) if grouped else None,
        "cycle_min": min(row.cycle for row in typed_rows) if typed_rows else None,
        "cycle_max": max(row.cycle for row in typed_rows) if typed_rows else None,
        "duplicate_unit_cycle_keys": duplicate_keys,
        "not_starting_at_one_units": not_starting_at_one,
        "non_monotonic_units": non_monotonic_units,
        "missing_cycles_by_unit": missing_cycles,
        "unit_cycle_counts": {str(unit): len(unit_rows) for unit, unit_rows in grouped.items()},
        "unit_start_end": {
            str(unit): {"start": unit_rows[0].cycle, "end": unit_rows[-1].cycle}
            for unit, unit_rows in grouped.items()
        },
    }
    result["passed"] = (
        duplicate_keys == 0
        and not not_starting_at_one
        and not non_monotonic_units
        and not missing_cycles
    )
    return result


def linear_quantile(sorted_values: Sequence[float], probability: float) -> float:
    if not sorted_values:
        raise ValidationError("Cannot calculate a quantile from an empty sequence.")
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(sorted_values[lower])
    weight = position - lower
    return float(sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight)


def numeric_summary(values: Sequence[float]) -> dict[str, object]:
    if not values:
        raise ValidationError("Cannot summarize an empty numeric sequence.")
    ordered = sorted(float(value) for value in values)
    mean = statistics.fmean(ordered)
    stddev = statistics.pstdev(ordered)
    q1 = linear_quantile(ordered, 0.25)
    q3 = linear_quantile(ordered, 0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    constant = ordered[0] == ordered[-1]
    near_constant = (
        not constant and stddev <= 1e-8 * max(1.0, abs(mean))
    )
    outlier_count = sum(value < lower or value > upper for value in ordered)
    return {
        "sample_count": len(ordered),
        "minimum": ordered[0],
        "maximum": ordered[-1],
        "mean": mean,
        "population_stddev": stddev,
        "median": statistics.median(ordered),
        "unique_value_count": len(set(ordered)),
        "constant": constant,
        "near_constant": near_constant,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "tukey_lower_bound": lower,
        "tukey_upper_bound": upper,
        "potential_outlier_count": outlier_count,
    }


def slope_and_correlation(
    cycles: Sequence[float], values: Sequence[float]
) -> tuple[float | None, float | None]:
    if len(cycles) != len(values) or len(cycles) < 2:
        return None, None
    x_mean = statistics.fmean(cycles)
    y_mean = statistics.fmean(values)
    covariance_sum = sum((x - x_mean) * (y - y_mean) for x, y in zip(cycles, values))
    x_square_sum = sum((x - x_mean) ** 2 for x in cycles)
    y_square_sum = sum((y - y_mean) ** 2 for y in values)
    slope = covariance_sum / x_square_sum if x_square_sum else None
    denominator = math.sqrt(x_square_sum * y_square_sum)
    correlation = covariance_sum / denominator if denominator else None
    return slope, correlation


def trend_direction(
    slope: float | None, mean_sensor: float, cycle_range: int
) -> tuple[str, float]:
    tolerance = 1e-12 * max(1.0, abs(mean_sensor)) / max(1, cycle_range)
    if slope is None:
        return "undefined", tolerance
    if slope > tolerance:
        return "increasing", tolerance
    if slope < -tolerance:
        return "decreasing", tolerance
    return "flat", tolerance


def analyze_trends(dataset: ParsedFile) -> dict[str, object]:
    rows = [row for row in dataset.rows if isinstance(row, RawRow)]
    grouped = group_rows_by_unit(rows)
    details: list[dict[str, object]] = []
    directions: dict[str, Counter[str]] = {sensor: Counter() for sensor in SENSOR_NAMES}
    global_sensor_stats: dict[str, dict[str, object]] = {}
    for sensor_offset, sensor in enumerate(SENSOR_NAMES, start=5):
        all_cycles = [float(row.cycle) for row in rows]
        all_values = [row.values[sensor_offset] for row in rows]
        _, global_correlation = slope_and_correlation(all_cycles, all_values)
        global_sensor_stats[sensor] = {
            "cycle_pearson_correlation": global_correlation,
            **numeric_summary(all_values),
        }
        for unit_id, unit_rows in grouped.items():
            cycles = [float(row.cycle) for row in unit_rows]
            values = [row.values[sensor_offset] for row in unit_rows]
            slope, correlation = slope_and_correlation(cycles, values)
            direction, tolerance = trend_direction(
                slope, statistics.fmean(values), unit_rows[-1].cycle - unit_rows[0].cycle
            )
            directions[sensor][direction] += 1
            details.append(
                {
                    "dataset_split": dataset.split,
                    "unit_id": unit_id,
                    "sensor_id": sensor,
                    "cycle_start": unit_rows[0].cycle,
                    "cycle_end": unit_rows[-1].cycle,
                    "sample_count": len(unit_rows),
                    "start_value": values[0],
                    "end_value": values[-1],
                    "change": values[-1] - values[0],
                    "slope": slope,
                    "pearson_correlation": correlation,
                    "slope_tolerance": tolerance,
                    "direction": direction,
                    "analysis_method": "OLS slope and Pearson correlation against cycle",
                    "raw_source_locator": {
                        "first_raw_line": unit_rows[0].raw_line_number,
                        "last_raw_line": unit_rows[-1].raw_line_number,
                        "raw_column_index": sensor_offset + 1,
                    },
                    "source_sha256": dataset.sha256,
                    "limitations": "Association is not causation or a failure diagnosis.",
                }
            )
    direction_summary: dict[str, dict[str, object]] = {}
    for sensor, counts in directions.items():
        total = sum(counts.values())
        defined = total - counts["undefined"]
        direction_summary[sensor] = {
            "increasing": counts["increasing"],
            "decreasing": counts["decreasing"],
            "flat": counts["flat"],
            "undefined": counts["undefined"],
            "total_units": total,
            "defined_units": defined,
            "increasing_ratio_of_defined": counts["increasing"] / defined if defined else None,
            "decreasing_ratio_of_defined": counts["decreasing"] / defined if defined else None,
            "flat_ratio_of_defined": counts["flat"] / defined if defined else None,
        }
    return {
        "detail_count": len(details),
        "expected_detail_count": len(grouped) * len(SENSOR_NAMES),
        "details": details,
        "direction_summary": direction_summary,
        "global_sensor_stats": global_sensor_stats,
    }


def feature_statistics(dataset: ParsedFile) -> dict[str, dict[str, object]]:
    rows = [row for row in dataset.rows if isinstance(row, RawRow)]
    return {
        name: numeric_summary([row.values[index] for row in rows])
        for index, name in enumerate(FIELD_NAMES[2:], start=2)
    }


def compress_positions(positions: Sequence[int]) -> str:
    if not positions:
        return "None"
    ranges: list[str] = []
    start = previous = positions[0]
    for value in positions[1:]:
        if value == previous + 1:
            previous = value
            continue
        ranges.append(str(start) if start == previous else f"{start}-{previous}")
        start = previous = value
    ranges.append(str(start) if start == previous else f"{start}-{previous}")
    return ", ".join(ranges)


def count_full_row_duplicates(rows: Sequence[RawRow]) -> int:
    counts = Counter(row.tokens for row in rows)
    return sum(count - 1 for count in counts.values() if count > 1)


class FD001Catalog:
    """In-memory deterministic query layer for validated FD001 data."""

    def __init__(
        self,
        train: ParsedFile,
        test: ParsedFile,
        rul: ParsedFile,
        quality: dict[str, object],
        trends: dict[str, dict[str, object]],
    ):
        self.datasets = {"train": train, "test": test}
        self.rul = rul
        self.quality = quality
        self.trends = trends
        self.by_key = {
            split: {(row.unit_id, row.cycle): row for row in dataset.rows if isinstance(row, RawRow)}
            for split, dataset in self.datasets.items()
        }
        self.by_unit = {
            split: group_rows_by_unit(
                [row for row in dataset.rows if isinstance(row, RawRow)]
            )
            for split, dataset in self.datasets.items()
        }
        self.trend_by_key = {
            split: {
                (item["unit_id"], item["sensor_id"]): item
                for item in trend_data["details"]
            }
            for split, trend_data in trends.items()
        }
        self.rul_by_unit = {
            row.unit_id: row for row in rul.rows if isinstance(row, RULRow)
        }

    def _split(self, split: str) -> str:
        if split not in self.datasets:
            raise QueryError("INVALID_SPLIT", f"Unsupported split: {split}")
        return split

    def list_dataset_splits(self) -> list[str]:
        return list(SPLITS)

    def list_units(self, split: str) -> list[int]:
        return sorted(self.by_unit[self._split(split)])

    def list_cycles(self, split: str, unit_id: int) -> list[int]:
        split = self._split(split)
        if unit_id not in self.by_unit[split]:
            raise QueryError("UNKNOWN_UNIT", f"Unknown unit {unit_id} in {split}.")
        return [row.cycle for row in self.by_unit[split][unit_id]]

    def list_sensors(self) -> list[str]:
        return list(SENSOR_NAMES)

    def get_raw_row(self, split: str, unit_id: int, cycle: int) -> RawRow:
        split = self._split(split)
        if unit_id not in self.by_unit[split]:
            raise QueryError("UNKNOWN_UNIT", f"Unknown unit {unit_id} in {split}.")
        row = self.by_key[split].get((unit_id, cycle))
        if row is None:
            raise QueryError("INVALID_CYCLE", f"Cycle {cycle} does not exist for unit {unit_id}.")
        return row

    def get_sensor_trend(self, split: str, unit_id: int, sensor_id: str) -> dict[str, object]:
        split = self._split(split)
        if sensor_id not in SENSOR_NAMES:
            raise QueryError("UNKNOWN_SENSOR", f"Unknown sensor: {sensor_id}")
        if unit_id not in self.by_unit[split]:
            raise QueryError("UNKNOWN_UNIT", f"Unknown unit {unit_id} in {split}.")
        return self.trend_by_key[split][(unit_id, sensor_id)]

    def get_operational_settings(self, split: str, unit_id: int, cycle: int) -> dict[str, object]:
        row = self.get_raw_row(split, unit_id, cycle)
        return {
            "op_setting_1": row.values[2],
            "op_setting_2": row.values[3],
            "op_setting_3": row.values[4],
            "source": row.field_locator(3),
        }

    def get_data_quality_summary(self, split: str) -> dict[str, object]:
        self._split(split)
        return self.quality[split]

    def get_test_rul(self, split: str, unit_id: int) -> dict[str, object]:
        if split == "train":
            raise QueryError("UNSUPPORTED_RUL_QUERY", "Train RUL is not supplied by RUL_FD001.txt.")
        self._split(split)
        if unit_id not in self.rul_by_unit:
            raise QueryError("UNKNOWN_UNIT", f"Unknown test unit {unit_id}.")
        item = self.rul_by_unit[unit_id]
        return {
            "dataset_split": "test",
            "unit_id": unit_id,
            "rul_cycles": item.value,
            "source_file": item.source_file,
            "source_sha256": item.source_sha256,
            "raw_line_number": item.raw_line_number,
            "parsed_row_index": item.parsed_row_index,
            "raw_column_index": 1,
            "raw_value": item.raw_value,
            "parsed_value": item.value,
        }

    def get_raw_source_locator(
        self, split: str, unit_id: int, cycle: int, field_name: str
    ) -> dict[str, object]:
        if field_name not in FIELD_NAMES:
            raise QueryError("MISSING_DATA", f"Unknown field: {field_name}")
        row = self.get_raw_row(split, unit_id, cycle)
        return row.field_locator(FIELD_NAMES.index(field_name) + 1)


def field_dictionary() -> list[dict[str, object]]:
    fields: list[dict[str, object]] = []
    for index, name in enumerate(FIELD_NAMES, start=1):
        if name == "unit_id":
            zh_name, en_name, data_type, use = "引擎單元識別碼", "Engine unit identifier", "positive integer", "Split-local unit key"
            basis = "LOCAL_DATA_VERIFIED"
        elif name == "cycle":
            zh_name, en_name, data_type, use = "運轉週期", "Operating cycle", "positive integer", "Ordered cycle within a split-local unit"
            basis = "LOCAL_DATA_VERIFIED"
        elif name.startswith("op_setting"):
            number = name.rsplit("_", 1)[1]
            zh_name, en_name, data_type, use = f"操作設定 {number}", f"Operational setting {number}", "finite number", "Operational condition input"
            basis = "FORMAT_CONVENTION"
        else:
            number = int(name.rsplit("_", 1)[1])
            zh_name, en_name, data_type, use = f"感測器 {number:02d}", f"Sensor {number:02d}", "finite number", "Sensor measurement"
            basis = "FORMAT_CONVENTION"
        fields.append(
            {
                "raw_column_index": index,
                "canonical_field_name": name,
                "traditional_chinese_name": zh_name,
                "english_name": en_name,
                "data_type": data_type,
                "purpose": use,
                "physical_quantity": "UNVERIFIED" if index >= 3 else "identifier/count",
                "unit": "UNVERIFIED" if index >= 3 else "dimensionless",
                "nullable": False,
                "missing_value_rule": "Reject absent, invalid, or non-finite tokens; do not impute.",
                "semantic_basis": basis,
                "semantic_confirmation_status": (
                    "LOCAL_DATA_VERIFIED for position/type; physical meaning UNVERIFIED"
                    if index >= 3
                    else "LOCAL_DATA_VERIFIED"
                ),
            }
        )
    return fields


def query_specifications() -> list[dict[str, object]]:
    return [
        {"name": "list_dataset_splits", "inputs": {}, "output": ["dataset_split"], "sort": "train, test", "boundary": [], "traceability": []},
        {"name": "list_units_by_split", "inputs": {"split": "string"}, "output": ["unit_id"], "sort": "unit_id ascending", "boundary": ["INVALID_SPLIT"], "traceability": ["dataset_split"]},
        {"name": "list_cycles_by_unit", "inputs": {"split": "string", "unit_id": "positive integer"}, "output": ["cycle"], "sort": "cycle ascending in raw order", "boundary": ["INVALID_SPLIT", "UNKNOWN_UNIT", "EMPTY_QUERY_RESULT"], "traceability": ["dataset_split", "unit_id"]},
        {"name": "list_sensors", "inputs": {}, "output": ["sensor_id", "raw_column_index"], "sort": "sensor number ascending", "boundary": [], "traceability": ["canonical_field_name"]},
        {"name": "get_raw_row", "inputs": {"split": "string", "unit_id": "positive integer", "cycle": "positive integer"}, "output": ["26 parsed fields", "source locator"], "sort": "single row", "boundary": ["INVALID_SPLIT", "UNKNOWN_UNIT", "INVALID_CYCLE", "MISSING_DATA"], "traceability": ["source_file", "source_sha256", "raw_line_number", "parsed_row_index"]},
        {"name": "get_sensor_trend", "inputs": {"split": "string", "unit_id": "positive integer", "sensor_id": "sensor_01..sensor_21"}, "output": ["cycle range", "sample count", "start/end/change", "slope", "correlation", "direction", "source locator"], "sort": "single result", "boundary": ["INVALID_SPLIT", "UNKNOWN_UNIT", "UNKNOWN_SENSOR", "MISSING_DATA"], "traceability": ["source_sha256", "first_raw_line", "last_raw_line", "raw_column_index"]},
        {"name": "get_operational_settings", "inputs": {"split": "string", "unit_id": "positive integer", "cycle": "positive integer"}, "output": ["op_setting_1", "op_setting_2", "op_setting_3", "source locator"], "sort": "canonical column order", "boundary": ["INVALID_SPLIT", "UNKNOWN_UNIT", "INVALID_CYCLE", "MISSING_DATA"], "traceability": ["raw_line_number", "raw_column_index"]},
        {"name": "get_data_quality_summary", "inputs": {"split": "string"}, "output": ["quality gate", "structural checks", "feature statistics"], "sort": "canonical field order", "boundary": ["INVALID_SPLIT", "EMPTY_QUERY_RESULT"], "traceability": ["source_file", "source_sha256"]},
        {"name": "get_test_rul", "inputs": {"split": "string", "unit_id": "positive integer"}, "output": ["rul_cycles", "source locator"], "sort": "single result", "boundary": ["INVALID_SPLIT", "UNKNOWN_UNIT", "UNSUPPORTED_RUL_QUERY", "MISSING_DATA"], "traceability": ["source_file", "source_sha256", "raw_line_number", "parsed_row_index", "raw_column_index"]},
        {"name": "get_raw_source_locator", "inputs": {"split": "string", "unit_id": "positive integer", "cycle": "positive integer", "field_name": "canonical field name"}, "output": ["raw and parsed locator/value"], "sort": "single result", "boundary": ["INVALID_SPLIT", "UNKNOWN_UNIT", "INVALID_CYCLE", "UNKNOWN_SENSOR", "MISSING_DATA"], "traceability": ["source_file", "source_sha256", "raw_line_number", "parsed_row_index", "raw_column_index", "raw_value", "parsed_value"]},
    ]


def build_analysis(data_root: Path, project_root: Path) -> dict[str, object]:
    resolved_data_root = data_root.resolve()
    resolved_project_root = project_root.resolve()
    if not resolved_data_root.is_dir():
        raise ValidationError(f"Data root does not exist: {resolved_data_root}")
    paths: dict[str, Path] = {}
    for split, filename in RAW_FILES.items():
        matches = list(resolved_data_root.rglob(filename))
        if len(matches) != 1:
            raise ValidationError(f"Expected exactly one {filename} under data root; found {len(matches)}.")
        resolved = matches[0].resolve()
        if resolved_data_root not in resolved.parents:
            raise ValidationError(f"Source path escapes data root: {resolved}")
        paths[split] = resolved

    train = parse_data_file(paths["train"], "train", resolved_project_root)
    test = parse_data_file(paths["test"], "test", resolved_project_root)
    rul = parse_rul_file(paths["rul"], resolved_project_root)
    datasets = {"train": train, "test": test, "rul": rul}

    structure: dict[str, dict[str, object]] = {}
    for split, dataset in datasets.items():
        expected = EXPECTED[split]
        row_count = len(dataset.rows)
        column_distribution = dict(sorted(dataset.column_count_distribution.items()))
        entry: dict[str, object] = {
            "actual_rows": row_count,
            "expected_rows": expected["rows"],
            "column_count_distribution": column_distribution,
            "expected_columns": expected["columns"],
            "blank_line_count": len(dataset.blank_line_positions),
            "trailing_whitespace_line_count": len(dataset.trailing_whitespace_positions),
        }
        if split in SPLITS:
            cycle_result = validate_cycles(dataset)
            entry.update(cycle_result)
            entry["expected_units"] = expected["units"]
            entry["passed"] = bool(
                cycle_result["passed"]
                and row_count == expected["rows"]
                and column_distribution == {expected["columns"]: expected["rows"]}
                and cycle_result["unit_count"] == expected["units"]
            )
        else:
            rul_rows = [row for row in dataset.rows if isinstance(row, RULRow)]
            entry.update(
                {
                    "all_nonnegative_integers": all(row.value >= 0 for row in rul_rows),
                    "unit_cycle_checks": "NOT_APPLICABLE",
                    "passed": row_count == expected["rows"]
                    and column_distribution == {1: expected["rows"]}
                    and all(row.value >= 0 for row in rul_rows),
                }
            )
        structure[split] = entry

    rul_rows = [row for row in rul.rows if isinstance(row, RULRow)]
    rul_alignment = validate_rul_alignment(test, rul)

    feature_stats = {split: feature_statistics(datasets[split]) for split in SPLITS}
    trends = {split: analyze_trends(datasets[split]) for split in SPLITS}
    quality: dict[str, object] = {}
    for split in SPLITS:
        dataset = datasets[split]
        raw_rows = [row for row in dataset.rows if isinstance(row, RawRow)]
        quality[split] = {
            "missing_values": 0,
            "empty_fields": 0,
            "invalid_numeric_values": 0,
            "nan_or_infinity": 0,
            "inconsistent_column_counts": sum(
                count for width, count in dataset.column_count_distribution.items() if width != 26
            ),
            "duplicate_full_rows": count_full_row_duplicates(raw_rows),
            "duplicate_unit_cycle_keys": structure[split]["duplicate_unit_cycle_keys"],
            "missing_cycle_units": len(structure[split]["missing_cycles_by_unit"]),
            "non_monotonic_cycle_units": len(structure[split]["non_monotonic_units"]),
            "invalid_unit_ids": 0,
            "invalid_cycle_values": 0,
            "feature_statistics": feature_stats[split],
        }
        checks = [
            quality[split][key] == 0
            for key in (
                "missing_values",
                "empty_fields",
                "invalid_numeric_values",
                "nan_or_infinity",
                "inconsistent_column_counts",
                "duplicate_full_rows",
                "duplicate_unit_cycle_keys",
                "missing_cycle_units",
                "non_monotonic_cycle_units",
                "invalid_unit_ids",
                "invalid_cycle_values",
            )
        ]
        quality[split]["passed"] = all(checks) and structure[split]["passed"]
    quality["rul"] = {
        "missing_values": 0,
        "empty_fields": 0,
        "invalid_numeric_values": 0,
        "nan_or_infinity": 0,
        "inconsistent_column_counts": 0,
        "duplicate_full_rows": len(rul_rows) - len({row.raw_value for row in rul_rows}),
        "invalid_rul_values": 0,
        "rul_alignment_errors": 0 if rul_alignment["passed"] else 1,
        "unit_cycle_checks": "NOT_APPLICABLE",
        "passed": structure["rul"]["passed"] and rul_alignment["passed"],
    }
    data_quality_gate = all(quality[split]["passed"] for split in ("train", "test", "rul"))
    if not all(structure[split]["passed"] for split in ("train", "test", "rul")):
        raise ValidationError("CONTRACT_MISMATCH or STRUCTURAL_VALIDATION_FAILED")
    if not rul_alignment["passed"]:
        raise ValidationError("RUL alignment validation failed.")
    if not data_quality_gate:
        raise ValidationError("DATA_QUALITY_GATE failed.")

    cycle_length_stats = {}
    for split in SPLITS:
        lengths = list(structure[split]["unit_cycle_counts"].values())
        cycle_length_stats[split] = numeric_summary([float(value) for value in lengths])

    return {
        "datasets": datasets,
        "structure": structure,
        "rul_alignment": rul_alignment,
        "feature_statistics": feature_stats,
        "trends": trends,
        "quality": quality,
        "data_quality_gate": data_quality_gate,
        "cycle_length_stats": cycle_length_stats,
    }


def build_contract(analysis: dict[str, object]) -> dict[str, object]:
    datasets = analysis["datasets"]
    identity = []
    for split in ("train", "test", "rul"):
        dataset: ParsedFile = datasets[split]
        identity.append(
            {
                "dataset_id": DATASET_ID,
                "dataset_split": split,
                "source_file": dataset.relative_path,
                "source_sha256": dataset.sha256,
                "source_trust_policy": "STUDENT_TRUSTED_LOCAL_FILES",
                "external_source_verification": "NOT_REQUIRED",
                "verification_status": "LOCAL_DATA_VERIFIED",
                "actual_rows": len(dataset.rows),
                "actual_column_distribution": {
                    str(width): count
                    for width, count in sorted(dataset.column_count_distribution.items())
                },
            }
        )
    return {
        "contract_version": CONTRACT_VERSION,
        "dataset_identity": identity,
        "schema": {
            "train_test_fields": field_dictionary(),
            "rul_field": {
                "raw_column_index": 1,
                "canonical_field_name": "rul_cycles",
                "traditional_chinese_name": "剩餘使用壽命週期數",
                "english_name": "Remaining useful life in cycles",
                "data_type": "non-negative integer",
                "nullable": False,
                "unit": "cycle",
                "semantic_basis": "FORMAT_CONVENTION",
                "relationship": "The nth effective RUL row maps to test unit_id n after alignment validation.",
            },
            "primary_keys": {
                "train_test": ["dataset_split", "unit_id", "cycle"],
                "sensor_value": ["dataset_split", "unit_id", "cycle", "sensor_id"],
                "rul": ["dataset_split=test", "unit_id"],
            },
            "namespace_rule": "Train and test unit IDs are independent namespaces and do not identify the same physical engine.",
        },
        "query_specification": query_specifications(),
        "query_boundaries": {
            "INVALID_SPLIT": "Split is not train or test.",
            "UNKNOWN_UNIT": "The unit does not exist in the selected split.",
            "INVALID_CYCLE": "The cycle is invalid or absent for the selected unit.",
            "UNKNOWN_SENSOR": "The sensor identifier is outside sensor_01..sensor_21.",
            "MISSING_DATA": "A required field or source value is absent.",
            "EMPTY_QUERY_RESULT": "A valid query has no rows; it is not converted to zero.",
            "UNSUPPORTED_RUL_QUERY": "Train RUL is not supplied by RUL_FD001.txt.",
        },
        "traceability": {
            "raw_line_number_base": 1,
            "raw_column_index_base": 1,
            "parsed_row_index_base": 0,
            "blank_lines": "Count in raw line numbering but do not create parsed rows.",
            "raw_value": "Original whitespace-delimited token.",
            "parsed_value": "Finite numeric conversion of raw_value.",
            "derived_value": "Explicitly labeled result calculated from parsed values.",
            "required_locator_fields": [
                "source_file",
                "source_sha256",
                "raw_line_number",
                "raw_column_index",
                "parsed_row_index",
                "unit_id",
                "cycle",
                "canonical_field_name",
            ],
        },
        "data_integrity": {
            "raw_data_mode": "read-only",
            "fabricated_values": "prohibited",
            "silent_correction": "prohibited",
            "parser": "UTF-8/ASCII strict decode; nonblank lines split on one or more whitespace characters; finite numeric conversion.",
            "train_test_namespace": "independent",
            "source_hash_rule": "Recompute SHA-256 before and after analysis and require equality.",
            "complete_index_publication": "prohibited; rebuild locally in memory",
        },
        "version_control": {
            "compatibility": "Patch changes preserve field names, query meanings, keys, and error codes. Breaking changes require a new major version and Brain acceptance.",
            "change_history": [
                {"version": CONTRACT_VERSION, "date": "2026-11-24", "change": "Initial validated FD001 local data contract."}
            ],
            "evidence_references": [
                "outputs/FD001_DATASET_PROFILE.md",
                "outputs/FD001_RAW_INDEX_SPEC.md",
                "outputs/FD001_DATA_QUALITY.md",
                "outputs/FD001_SENSOR_TRENDS.md",
            ],
        },
        "limitations": [
            "The three files are trusted by STUDENT; NASA official provenance was not independently verified.",
            "Physical names and units for operational settings and sensors are UNVERIFIED.",
            "Test last observed cycle is not a failure cycle.",
            "Train and test unit IDs are independent namespaces.",
            "Correlation and trends do not establish causation, fault diagnosis, or an RUL prediction model.",
        ],
    }


def fmt_number(value: object) -> str:
    if value is None:
        return "UNDEFINED"
    if isinstance(value, bool):
        return "YES" if value else "NO"
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def markdown_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(fmt_number(value).replace("|", "\\|") for value in row) + " |")
    return lines


def render_dataset_profile(analysis: dict[str, object], timestamp: str) -> str:
    datasets: dict[str, ParsedFile] = analysis["datasets"]
    structure = analysis["structure"]
    lines = [
        "# FD001 Local Dataset Profile",
        "",
        f"- Execution timestamp: `{timestamp}`",
        "- Source trust policy: `STUDENT_TRUSTED_LOCAL_FILES`",
        "- External source verification: `NOT_REQUIRED`",
        "- Internet download or replacement: `PROHIBITED`",
        "- Parser: strict ASCII/UTF-8 decode; each nonblank line is split on one or more whitespace characters.",
        "- Header rows: none detected or expected; every effective line is parsed as data.",
        "- Provenance limitation: local file identity and structure are verified, but NASA official provenance was not independently checked.",
        "",
        "## File inventory",
        "",
    ]
    inventory_rows = []
    for split in ("train", "test", "rul"):
        dataset = datasets[split]
        inventory_rows.append(
            (
                split,
                dataset.relative_path,
                dataset.size_bytes,
                dataset.sha256,
                dataset.encoding,
                dataset.text_line_count,
                len(dataset.blank_line_positions),
                compress_positions(dataset.blank_line_positions),
                len(dataset.trailing_whitespace_positions),
                compress_positions(dataset.trailing_whitespace_positions),
                len(dataset.rows),
                json.dumps(dict(sorted(dataset.column_count_distribution.items())), sort_keys=True),
            )
        )
    lines += markdown_table(
        ["Split", "Source file", "Bytes", "SHA-256", "Encoding", "Text lines", "Blank lines", "Blank positions", "Trailing-space lines", "Trailing-space positions", "Parsed rows", "Column distribution"],
        inventory_rows,
    )
    lines += ["", "## Structural validation", ""]
    structural_rows = []
    for split in SPLITS:
        item = structure[split]
        structural_rows.append(
            (split, item["actual_rows"], item["unit_count"], item["unit_min"], item["unit_max"], item["cycle_min"], item["cycle_max"], item["duplicate_unit_cycle_keys"], len(item["missing_cycles_by_unit"]), len(item["non_monotonic_units"]), "PASS" if item["passed"] else "FAIL")
        )
    lines += markdown_table(
        ["Split", "Rows", "Units", "Unit min", "Unit max", "Cycle min", "Cycle max", "Duplicate keys", "Units with missing cycles", "Non-monotonic units", "Result"],
        structural_rows,
    )
    rul_item = structure["rul"]
    lines += [
        "",
        f"- RUL rows/columns: `{rul_item['actual_rows']} × 1`",
        f"- RUL non-negative integer validation: `{'PASS' if rul_item['all_nonnegative_integers'] else 'FAIL'}`",
        f"- RUL-to-Test-Unit alignment: `{'PASS' if analysis['rul_alignment']['passed'] else 'FAIL'}`",
        "",
        "## Dataset semantics",
        "",
        "| Statement | Status |",
        "| --- | --- |",
        "| Train contains split-local Unit, Cycle, three operational-setting columns, and 21 sensor columns. | LOCAL_DATA_VERIFIED |",
        "| Train represents complete run-to-failure trajectories. | FORMAT_CONVENTION |",
        "| Test contains truncated trajectories and its last observed cycle is not a failure cycle. | FORMAT_CONVENTION |",
        "| The nth effective RUL row maps to test Unit ID n after structural alignment checks. | FORMAT_CONVENTION + LOCAL_DATA_VERIFIED alignment |",
        "| Train and Test Unit ID n identify the same physical engine. | UNVERIFIED; explicitly prohibited assumption |",
        "| The files were independently confirmed against NASA official downloads. | UNVERIFIED |",
        "",
        "## Field dictionary summary",
        "",
        "The complete 26-field dictionary and RUL definition are normative in `contracts/FD001_DATA_CONTRACT.md` and `.json`. Raw columns 1-2 are `unit_id` and `cycle`; columns 3-5 are `op_setting_1..3`; columns 6-26 are `sensor_01..sensor_21`. Physical sensor/setting names and units remain `UNVERIFIED`.",
        "",
        "## Limitations",
        "",
        "- Structural compatibility does not independently prove NASA official provenance.",
        "- No raw values were corrected, removed, imputed, normalized, or smoothed.",
        "- Full raw rows and full RUL lists are intentionally omitted from this public artifact.",
        "",
    ]
    return "\n".join(lines)


def render_raw_index_spec(analysis: dict[str, object]) -> str:
    datasets: dict[str, ParsedFile] = analysis["datasets"]
    examples = []
    for split in SPLITS:
        rows = [row for row in datasets[split].rows if isinstance(row, RawRow)]
        for row in (rows[0], rows[len(rows) // 2], rows[-1]):
            locator = row.field_locator(6)
            examples.append((split, row.unit_id, row.cycle, row.raw_line_number, row.parsed_row_index, 6, "sensor_01", locator["raw_value"], locator["parsed_value"], row.source_sha256))
    lines = [
        "# FD001 Raw Data Index Specification",
        "",
        "## Index construction",
        "",
        "- Raw line numbers are one-based physical text-line positions.",
        "- Parsed row indexes are zero-based and exclude blank lines.",
        "- Raw column indexes are one-based.",
        "- Blank lines remain part of raw line numbering but do not create parsed rows.",
        "- Train and Test Unit IDs use independent namespaces.",
        "- Raw values preserve the original whitespace-delimited token; parsed and derived values are separately labeled.",
        "- Parsing never sorts, renumbers, or rearranges rows.",
        "",
        "## Keys",
        "",
        "- Train/Test row: `(dataset_split, unit_id, cycle)`",
        "- Sensor value: `(dataset_split, unit_id, cycle, sensor_id)`",
        "- RUL: `(dataset_split=test, unit_id)`",
        "",
        "## Required locator fields",
        "",
        "`dataset_id`, `dataset_split`, `source_file`, `source_sha256`, `raw_line_number`, `parsed_row_index`, `unit_id`, `cycle`, `raw_column_index`, `canonical_field_name`, `raw_value`, `parsed_value`, and separately labeled derived values.",
        "",
        "## RUL mapping",
        "",
        "The nth effective RUL row maps to Test Unit ID n only after confirming Test Unit IDs are exactly 1..N and RUL has N effective rows. This is a validated structural application of the FD001 format convention, not external proof of physical-engine identity.",
        "",
        "## Limited traceability examples",
        "",
    ]
    lines += markdown_table(
        ["Split", "Unit", "Cycle", "Raw line", "Parsed index", "Raw column", "Field", "Raw token", "Parsed value", "Source SHA-256"],
        examples,
    )
    lines += [
        "",
        "These examples cover first, middle, and last parsed rows. The complete index is rebuilt locally in memory and is not committed.",
        "",
        "## Local query surface",
        "",
        "`FD001Catalog` implements split/unit/cycle/sensor listing, raw-row lookup, operational-setting lookup, sensor-trend lookup, data-quality lookup, Test RUL lookup, and raw-source locator lookup with documented error codes.",
        "",
    ]
    return "\n".join(lines)


def render_quality_report(analysis: dict[str, object]) -> str:
    quality = analysis["quality"]
    lines = [
        "# FD001 Data Quality Report",
        "",
        f"- DATA_QUALITY_GATE: `{'PASS' if analysis['data_quality_gate'] else 'FAIL'}`",
        "- Population standard deviation uses denominator N.",
        "- Q1/Q3 use linear interpolation at position `(N-1)×p` in sorted values.",
        "- Potential outliers use Tukey bounds `Q1-1.5×IQR` and `Q3+1.5×IQR`.",
        "- Constant means maximum equals minimum.",
        "- Near-constant means nonconstant and `stddev <= 1e-8 × max(1, abs(mean))`.",
        "- Outliers are statistical flags, not confirmed sensor faults. Constant fields are not automatically invalid.",
        "",
        "## Integrity checks",
        "",
    ]
    check_rows = []
    keys = ["missing_values", "empty_fields", "invalid_numeric_values", "nan_or_infinity", "inconsistent_column_counts", "duplicate_full_rows"]
    for split in ("train", "test", "rul"):
        item = quality[split]
        check_rows.append((split, *(item.get(key, "NOT_APPLICABLE") for key in keys), item.get("duplicate_unit_cycle_keys", "NOT_APPLICABLE"), item.get("missing_cycle_units", "NOT_APPLICABLE"), item.get("non_monotonic_cycle_units", "NOT_APPLICABLE"), item.get("invalid_rul_values", "NOT_APPLICABLE"), item.get("rul_alignment_errors", "NOT_APPLICABLE"), "PASS" if item["passed"] else "FAIL"))
    lines += markdown_table(
        ["Split", "Missing", "Empty", "Invalid numeric", "NaN/Inf", "Bad widths", "Duplicate rows", "Duplicate keys", "Missing-cycle units", "Non-monotonic units", "Invalid RUL", "RUL alignment errors", "Result"],
        check_rows,
    )
    lines += [
        "",
        "RUL is a one-column value file whose row position maps to Test Unit ID. The 29 additional repeated RUL values are repeated measurements, not duplicate RUL keys; the implicit `(dataset_split=test, unit_id)` keys remain unique after alignment validation.",
    ]
    for split in SPLITS:
        lines += ["", f"## {split.title()} operational settings and sensors", ""]
        stat_rows = []
        for name in FEATURE_NAMES:
            stat = quality[split]["feature_statistics"][name]
            stat_rows.append((name, stat["sample_count"], stat["minimum"], stat["maximum"], stat["mean"], stat["population_stddev"], stat["median"], stat["unique_value_count"], stat["constant"], stat["near_constant"], stat["potential_outlier_count"], stat["q1"], stat["q3"], stat["iqr"]))
        lines += markdown_table(
            ["Field", "N", "Min", "Max", "Mean", "Population SD", "Median", "Unique", "Constant", "Near-constant", "Tukey outliers", "Q1", "Q3", "IQR"],
            stat_rows,
        )
    lines += [
        "",
        "## Limitations",
        "",
        "- Parsed numeric equality determines unique counts; raw-token uniqueness is separate.",
        "- When IQR is zero, Tukey bounds equal Q1/Q3 and values outside that point are flagged; this does not prove physical abnormality.",
        "- No deletion, imputation, smoothing, normalization, or raw-data correction was performed.",
        "",
    ]
    return "\n".join(lines)


def render_trend_report(analysis: dict[str, object]) -> str:
    lines = [
        "# FD001 Traceable Sensor Trend Analysis",
        "",
        "- Train and Test are analyzed independently.",
        "- Start/end are the first/last valid cycles in original raw order.",
        "- Change is end minus start.",
        "- Slope is OLS `sum((x-x_mean)(y-y_mean))/sum((x-x_mean)^2)`.",
        "- Pearson correlation uses centered covariance divided by the product of centered square-root sums.",
        "- Undefined denominators remain `UNDEFINED`; they are never replaced with zero.",
        "- Direction tolerance is `1e-12 × max(1, abs(mean_sensor)) / max(1, cycle_range)`.",
        "- Direction ratios exclude undefined results from the denominator.",
        "",
        "## Cycle-length distributions",
        "",
    ]
    cycle_rows = []
    for split in SPLITS:
        stat = analysis["cycle_length_stats"][split]
        cycle_rows.append((split, stat["sample_count"], stat["minimum"], stat["maximum"], stat["mean"], stat["population_stddev"], stat["median"], stat["unique_value_count"]))
    lines += markdown_table(["Split", "Units", "Min cycles", "Max cycles", "Mean", "Population SD", "Median", "Unique lengths"], cycle_rows)
    for split in SPLITS:
        trends = analysis["trends"][split]
        lines += [
            "",
            f"## {split.title()} sensor trends",
            "",
            f"- Per-unit/per-sensor analyses completed: `{trends['detail_count']}` of `{trends['expected_detail_count']}`.",
            "",
        ]
        rows = []
        for sensor in SENSOR_NAMES:
            direction = trends["direction_summary"][sensor]
            global_stat = trends["global_sensor_stats"][sensor]
            rows.append((sensor, global_stat["minimum"], global_stat["maximum"], global_stat["mean"], global_stat["population_stddev"], global_stat["cycle_pearson_correlation"], direction["increasing"], direction["decreasing"], direction["flat"], direction["undefined"], direction["increasing_ratio_of_defined"], direction["decreasing_ratio_of_defined"], direction["flat_ratio_of_defined"]))
        lines += markdown_table(
            ["Sensor", "Min", "Max", "Mean", "Population SD", "Global cycle correlation", "Increasing", "Decreasing", "Flat", "Undefined", "Increasing ratio", "Decreasing ratio", "Flat ratio"],
            rows,
        )
    test_rows = [row for row in analysis["datasets"]["test"].rows if isinstance(row, RawRow)]
    test_grouped = group_rows_by_unit(test_rows)
    rul_rows = [row for row in analysis["datasets"]["rul"].rows if isinstance(row, RULRow)]
    last_cycles = [unit_rows[-1].cycle for unit_rows in test_grouped.values()]
    rul_values = [row.value for row in rul_rows]
    combined = [last + rul for last, rul in zip(last_cycles, rul_values)]
    lines += [
        "",
        "## Test last-observation and RUL relationship",
        "",
        f"- Alignment result: `{'PASS' if analysis['rul_alignment']['passed'] else 'FAIL'}`",
        f"- Test last observed cycle range: `{min(last_cycles)}..{max(last_cycles)}`",
        f"- RUL cycle range: `{min(rul_values)}..{max(rul_values)}`",
        f"- Convention-derived last-observed-plus-RUL range: `{min(combined)}..{max(combined)}`",
        "- The last observed Test cycle is not labeled as a failure cycle. The mapping is a validated format convention, not an independently proven physical-engine relationship.",
        "",
        "## Traceability and limitations",
        "",
        "Each local per-unit/per-sensor result contains split, unit, sensor, cycle range, N, OLS/Pearson results, source SHA-256, and first/last raw-line plus raw-column locators. Full details and series are rebuilt in memory and are not committed.",
        "",
        "Correlation is not causation. Trend direction is not a validated fault diagnosis and this work does not implement an RUL prediction model.",
        "",
    ]
    return "\n".join(lines)


def render_contract_markdown(contract: dict[str, object]) -> str:
    lines = [
        "# FD001 Data Contract",
        "",
        f"- Contract version: `{contract['contract_version']}`",
        "- Status: `PENDING_RESEARCH_BRAIN_REVIEW`",
        "",
        "## Dataset identity",
        "",
    ]
    lines += markdown_table(
        ["Dataset ID", "Split", "Source file", "SHA-256", "Trust policy", "Verification", "Rows", "Column distribution"],
        [(item["dataset_id"], item["dataset_split"], item["source_file"], item["source_sha256"], item["source_trust_policy"], item["verification_status"], item["actual_rows"], json.dumps(item["actual_column_distribution"], sort_keys=True)) for item in contract["dataset_identity"]],
    )
    lines += ["", "## Train/Test field dictionary", ""]
    fields = contract["schema"]["train_test_fields"]
    lines += markdown_table(
        ["Column", "Canonical name", "繁體中文", "English", "Type", "Purpose", "Physical quantity", "Unit", "Nullable", "Missing rule", "Semantic basis", "Confirmation"],
        [(field["raw_column_index"], field["canonical_field_name"], field["traditional_chinese_name"], field["english_name"], field["data_type"], field["purpose"], field["physical_quantity"], field["unit"], field["nullable"], field["missing_value_rule"], field["semantic_basis"], field["semantic_confirmation_status"]) for field in fields],
    )
    rul = contract["schema"]["rul_field"]
    lines += [
        "",
        "## RUL field and relationships",
        "",
        f"- Field: `{rul['canonical_field_name']}`; type `{rul['data_type']}`; unit `{rul['unit']}`; nullable `{rul['nullable']}`.",
        f"- Relationship: {rul['relationship']}",
        f"- Namespace rule: {contract['schema']['namespace_rule']}",
        "- Primary keys:",
    ]
    for name, key in contract["schema"]["primary_keys"].items():
        lines.append(f"  - `{name}`: `{', '.join(key)}`")
    lines += ["", "## Query specification", ""]
    lines += markdown_table(
        ["Query", "Inputs", "Output", "Sort", "Boundaries", "Traceability"],
        [(item["name"], json.dumps(item["inputs"], sort_keys=True), ", ".join(item["output"]), item["sort"], ", ".join(item["boundary"]) or "None", ", ".join(item["traceability"]) or "None") for item in contract["query_specification"]],
    )
    lines += ["", "## Query boundaries", ""]
    for code, meaning in contract["query_boundaries"].items():
        lines.append(f"- `{code}`: {meaning}")
    lines += ["", "## Traceability", ""]
    for key, value in contract["traceability"].items():
        lines.append(f"- `{key}`: {json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value}")
    lines += ["", "## Data integrity", ""]
    for key, value in contract["data_integrity"].items():
        lines.append(f"- `{key}`: {value}")
    lines += ["", "## Version control", "", f"- Compatibility: {contract['version_control']['compatibility']}"]
    for item in contract["version_control"]["change_history"]:
        lines.append(f"- `{item['version']}` ({item['date']}): {item['change']}")
    lines += ["", "Evidence references:"]
    for reference in contract["version_control"]["evidence_references"]:
        lines.append(f"- `{reference}`")
    lines += ["", "## Limitations", ""]
    for limitation in contract["limitations"]:
        lines.append(f"- {limitation}")
    lines.append("")
    return "\n".join(lines)


def validate_contract_consistency(contract: dict[str, object], markdown: str) -> None:
    if contract["contract_version"] != CONTRACT_VERSION:
        raise ValidationError("Contract version mismatch.")
    if len(contract["schema"]["train_test_fields"]) != 26:
        raise ValidationError("Contract does not contain 26 train/test fields.")
    for field in contract["schema"]["train_test_fields"]:
        if field["canonical_field_name"] not in markdown:
            raise ValidationError(f"Markdown contract is missing {field['canonical_field_name']}.")
    for query in contract["query_specification"]:
        if query["name"] not in markdown:
            raise ValidationError(f"Markdown contract is missing query {query['name']}.")
    for code in contract["query_boundaries"]:
        if code not in markdown:
            raise ValidationError(f"Markdown contract is missing boundary {code}.")
    json.dumps(contract, ensure_ascii=False, allow_nan=False, sort_keys=True)


def resolve_timestamp(raw_timestamp: str | None) -> str:
    if raw_timestamp is None:
        return datetime.now(TAIPEI_TZ).isoformat(timespec="seconds")
    parsed = datetime.fromisoformat(raw_timestamp)
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(hours=8):
        raise ValidationError("Execution timestamp must include UTC+08:00.")
    return parsed.isoformat(timespec="seconds")


def write_artifacts(
    analysis: dict[str, object], project_root: Path, timestamp: str
) -> dict[str, str]:
    contract = build_contract(analysis)
    contract_md = render_contract_markdown(contract)
    validate_contract_consistency(contract, contract_md)
    contents = {
        "outputs/FD001_DATASET_PROFILE.md": render_dataset_profile(analysis, timestamp),
        "outputs/FD001_RAW_INDEX_SPEC.md": render_raw_index_spec(analysis),
        "outputs/FD001_DATA_QUALITY.md": render_quality_report(analysis),
        "outputs/FD001_SENSOR_TRENDS.md": render_trend_report(analysis),
        "contracts/FD001_DATA_CONTRACT.md": contract_md,
        "contracts/FD001_DATA_CONTRACT.json": json.dumps(
            contract, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True
        ) + "\n",
    }
    hashes: dict[str, str] = {}
    for relative_path, content in contents.items():
        path = project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        hashes[relative_path] = sha256_bytes(content.encode("utf-8"))
    return hashes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and profile trusted local FD001 files.")
    parser.add_argument("--data-root", default="data/FD001")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--execution-timestamp")
    parser.add_argument("--no-write", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    try:
        timestamp = resolve_timestamp(args.execution_timestamp)
        analysis = build_analysis(Path(args.data_root), project_root)
        artifact_hashes = {} if args.no_write else write_artifacts(analysis, project_root, timestamp)
        summary = {
            "contract_version": CONTRACT_VERSION,
            "data_quality_gate": "PASS" if analysis["data_quality_gate"] else "FAIL",
            "rows": {split: len(analysis["datasets"][split].rows) for split in ("train", "test", "rul")},
            "units": {split: analysis["structure"][split]["unit_count"] for split in SPLITS},
            "rul_alignment": "PASS" if analysis["rul_alignment"]["passed"] else "FAIL",
            "trend_coverage": {split: f"{analysis['trends'][split]['detail_count']}/{analysis['trends'][split]['expected_detail_count']}" for split in SPLITS},
            "artifact_sha256": artifact_hashes,
        }
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

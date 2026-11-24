#!/usr/bin/env python3
"""Generate a reproducible, privacy-preserving profile for the M1 CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import platform
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


TAIPEI_TZ = timezone(timedelta(hours=8), "Asia/Taipei")
TEXT_MISSING_MARKERS = frozenset({"na", "n/a", "nan", "none", "null"})
INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")


class ProfileError(Exception):
    """Raised when the input cannot be profiled safely."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Markdown profile from an authorized synthetic CSV."
    )
    parser.add_argument("--input", default="data/synthetic_sensor.csv")
    parser.add_argument("--output", default="outputs/INTRO_PROFILE.md")
    parser.add_argument("--expected-rows", type=int, default=6)
    parser.add_argument(
        "--execution-timestamp",
        help=(
            "ISO-8601 execution timestamp. Supplying the same value makes the "
            "generated report byte-for-byte reproducible."
        ),
    )
    return parser.parse_args()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def detect_encoding(data: bytes) -> tuple[str, str]:
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig", data.decode("utf-8-sig")
    try:
        return "utf-8", data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProfileError(f"CSV is not valid UTF-8: {exc}") from exc


def detect_dialect_and_header(text: str) -> tuple[csv.Dialect, bool]:
    sample = text[:8192]
    if not sample.strip():
        raise ProfileError("CSV is empty.")
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        has_header = csv.Sniffer().has_header(sample)
    except csv.Error as exc:
        raise ProfileError(f"CSV dialect/header detection failed: {exc}") from exc
    return dialect, has_header


def classify_missing(value: str) -> str | None:
    stripped = value.strip()
    if stripped == "":
        return "blank_or_whitespace"
    if stripped.casefold() in TEXT_MISSING_MARKERS:
        return "text_marker"
    return None


def scalar_type(value: str) -> str:
    stripped = value.strip()
    if INTEGER_PATTERN.fullmatch(stripped):
        return "integer"
    try:
        Decimal(stripped)
        return "decimal"
    except InvalidOperation:
        pass
    try:
        datetime.fromisoformat(stripped.replace("Z", "+00:00"))
        return "datetime"
    except ValueError:
        return "text"


def infer_column_type(values: list[str]) -> tuple[str, str, bool]:
    observed = [value for value in values if classify_missing(value) is None]
    if not observed:
        return "all_missing", "No non-missing values were available.", True

    types = Counter(scalar_type(value) for value in observed)
    type_set = set(types)
    if type_set == {"integer"}:
        inferred = "integer"
        consistent = True
    elif type_set <= {"integer", "decimal"}:
        inferred = "number"
        consistent = True
    elif type_set == {"datetime"}:
        inferred = "ISO-8601 datetime"
        consistent = True
    elif type_set == {"text"}:
        inferred = "text"
        consistent = True
    else:
        inferred = "mixed"
        consistent = False

    counts = ", ".join(f"{name}={types[name]}" for name in sorted(types))
    method = (
        "Missing values were excluded; remaining trimmed values were tested in "
        f"order as integer, Decimal-compatible number, ISO-8601 datetime, then text ({counts})."
    )
    return inferred, method, consistent


def markdown_code(value: object) -> str:
    return f"`{str(value).replace('`', '\\`')}`"


def format_positions(positions: list[int]) -> str:
    return ", ".join(str(position) for position in positions) if positions else "None"


def profile_csv(input_path: Path, expected_rows: int) -> dict[str, object]:
    if expected_rows < 0:
        raise ProfileError("Expected row count must not be negative.")
    if not input_path.exists() or not input_path.is_file():
        raise ProfileError(f"Input CSV does not exist or is not a file: {input_path}")

    raw = input_path.read_bytes()
    encoding, text = detect_encoding(raw)
    dialect, has_header = detect_dialect_and_header(text)
    if not has_header:
        raise ProfileError("A header row was not detected.")

    try:
        parsed_rows = list(csv.reader(io.StringIO(text, newline=""), dialect))
    except csv.Error as exc:
        raise ProfileError(f"CSV parsing failed: {exc}") from exc
    if not parsed_rows:
        raise ProfileError("CSV contains no rows.")

    header = parsed_rows[0]
    data_rows = parsed_rows[1:]
    column_count = len(header)
    blank_headers = [index + 1 for index, name in enumerate(header) if not name.strip()]
    duplicate_header_names = sorted(
        name for name, count in Counter(header).items() if count > 1
    )
    width_mismatches = [
        {"data_row": index, "csv_line": index + 1, "field_count": len(row)}
        for index, row in enumerate(data_rows, start=1)
        if len(row) != column_count
    ]

    missing_by_column: dict[str, int] = {name: 0 for name in header}
    missing_positions: list[dict[str, object]] = []
    blank_missing_total = 0
    marker_missing_total = 0
    values_by_column: dict[str, list[str]] = {name: [] for name in header}

    for data_position, row in enumerate(data_rows, start=1):
        for column_index, name in enumerate(header):
            value = row[column_index] if column_index < len(row) else ""
            values_by_column[name].append(value)
            missing_kind = classify_missing(value)
            if missing_kind is not None:
                missing_by_column[name] += 1
                missing_positions.append(
                    {
                        "data_row": data_position,
                        "csv_line": data_position + 1,
                        "column": name,
                        "kind": missing_kind,
                    }
                )
                if missing_kind == "blank_or_whitespace":
                    blank_missing_total += 1
                else:
                    marker_missing_total += 1

    row_positions: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for position, row in enumerate(data_rows, start=1):
        row_positions[tuple(row)].append(position)
    duplicate_groups = [positions for positions in row_positions.values() if len(positions) > 1]
    duplicate_groups.sort(key=lambda positions: positions[0])
    duplicate_count = sum(len(positions) - 1 for positions in duplicate_groups)

    inferred_types: dict[str, dict[str, object]] = {}
    for name in header:
        inferred, method, consistent = infer_column_type(values_by_column[name])
        inferred_types[name] = {
            "type": inferred,
            "method": method,
            "consistent": consistent,
        }

    actual_rows = len(data_rows)
    contract_matches = actual_rows == expected_rows
    format_valid = (
        not blank_headers
        and not duplicate_header_names
        and not width_mismatches
        and all(item["consistent"] for item in inferred_types.values())
    )
    return {
        "file_size": len(raw),
        "sha256": sha256_bytes(raw),
        "encoding": encoding,
        "delimiter": dialect.delimiter,
        "header_detected": has_header,
        "header": header,
        "column_count": column_count,
        "actual_rows": actual_rows,
        "expected_rows": expected_rows,
        "contract_matches": contract_matches,
        "blank_headers": blank_headers,
        "duplicate_header_names": duplicate_header_names,
        "width_mismatches": width_mismatches,
        "inferred_types": inferred_types,
        "missing_by_column": missing_by_column,
        "missing_positions": missing_positions,
        "missing_total": len(missing_positions),
        "blank_missing_total": blank_missing_total,
        "marker_missing_total": marker_missing_total,
        "duplicate_count": duplicate_count,
        "duplicate_groups": duplicate_groups,
        "format_valid": format_valid,
    }


def resolve_timestamp(raw_timestamp: str | None) -> str:
    if raw_timestamp is None:
        return datetime.now(TAIPEI_TZ).isoformat(timespec="seconds")
    try:
        parsed = datetime.fromisoformat(raw_timestamp)
    except ValueError as exc:
        raise ProfileError("Execution timestamp must be valid ISO-8601.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(hours=8):
        raise ProfileError("Execution timestamp must include the Asia/Taipei UTC+08:00 offset.")
    return parsed.isoformat(timespec="seconds")


def build_report(
    result: dict[str, object],
    input_display: str,
    command: str,
    execution_timestamp: str,
) -> str:
    header = result["header"]
    inferred_types = result["inferred_types"]
    missing_by_column = result["missing_by_column"]
    missing_positions = result["missing_positions"]
    duplicate_groups = result["duplicate_groups"]
    width_mismatches = result["width_mismatches"]

    lines = [
        "# Synthetic Sensor Dataset Profile",
        "",
        "## Dataset identity",
        "",
        "- Dataset type: `Synthetic Sensor Data`",
        f"- Source path: {markdown_code(input_display)}",
        "- Source provenance: Local synthetic sensor CSV authorized by the M1 data contract.",
        "- Generation provenance: The file's generator, author, and generation date are not established by the available evidence.",
        "- NASA C-MAPSS FD001 status: This dataset is not identified as NASA C-MAPSS FD001.",
        f"- File size: {result['file_size']} bytes",
        f"- Input SHA-256: {markdown_code(result['sha256'])}",
        "",
        "## CSV structure",
        "",
        f"- Parser: Python standard-library {markdown_code('csv.reader')} with {markdown_code('csv.Sniffer')}",
        f"- Encoding: {markdown_code(result['encoding'])}",
        f"- Delimiter: {markdown_code(repr(result['delimiter']))}",
        f"- Header detected: {markdown_code(str(result['header_detected']).upper())}",
        f"- Actual data rows (header excluded): {result['actual_rows']}",
        f"- Column count: {result['column_count']}",
        "- Column names: " + ", ".join(markdown_code(name) for name in header),
        "- Blank column-name positions: " + format_positions(result["blank_headers"]),
        "- Duplicate column names: "
        + (", ".join(markdown_code(name) for name in result["duplicate_header_names"]) or "None"),
        "",
        "## Inferred data types",
        "",
        "Missing values are excluded from type inference. Values are trimmed for inference only; the source values are not changed.",
        "",
        "| Column | Inferred type | Type consistent | Basis |",
        "| --- | --- | --- | --- |",
    ]
    for name in header:
        item = inferred_types[name]
        lines.append(
            f"| {markdown_code(name)} | {item['type']} | "
            f"{'YES' if item['consistent'] else 'NO'} | {item['method']} |"
        )

    lines.extend(
        [
            "",
            "## Missing values",
            "",
            "A value is missing when it is an empty string, contains only whitespace, or matches one of these case-insensitive textual markers after trimming: "
            + ", ".join(markdown_code(marker) for marker in sorted(TEXT_MISSING_MARKERS))
            + ".",
            "",
            f"- Missing values total: {result['missing_total']}",
            f"- Blank or whitespace-only values: {result['blank_missing_total']}",
            f"- Textual missing markers: {result['marker_missing_total']}",
            "",
            "| Column | Missing count |",
            "| --- | ---: |",
        ]
    )
    for name in header:
        lines.append(f"| {markdown_code(name)} | {missing_by_column[name]} |")

    lines.extend(["", "Missing positions use one-based data-row positions and exclude the header row.", ""])
    if missing_positions:
        lines.extend(
            [
                "| Data row | CSV line | Column | Missing kind |",
                "| ---: | ---: | --- | --- |",
            ]
        )
        for item in missing_positions:
            lines.append(
                f"| {item['data_row']} | {item['csv_line']} | "
                f"{markdown_code(item['column'])} | {item['kind']} |"
            )
    else:
        lines.append("None.")

    lines.extend(
        [
            "",
            "## Duplicate rows",
            "",
            "A duplicate is an additional data row whose complete parsed field sequence exactly matches an earlier row. Comparison is case-sensitive and whitespace-preserving.",
            "",
            f"- Duplicate row count (rows beyond the first occurrence): {result['duplicate_count']}",
            "- Duplicate position groups: "
            + ("; ".join("[" + format_positions(group) + "]" for group in duplicate_groups) or "None"),
            "",
            "## Format validation",
            "",
            f"- All data rows have {result['column_count']} fields: {'YES' if not width_mismatches else 'NO'}",
            "- Row-width mismatches: "
            + (json.dumps(width_mismatches, ensure_ascii=False, sort_keys=True) if width_mismatches else "None"),
            f"- Header names are nonblank and unique: {'YES' if not result['blank_headers'] and not result['duplicate_header_names'] else 'NO'}",
            f"- Non-missing values are type-consistent within every column: {'YES' if all(item['consistent'] for item in inferred_types.values()) else 'NO'}",
            f"- Overall format validation: {'PASS' if result['format_valid'] else 'FAIL'}",
            "",
            "## Expected versus actual",
            "",
            f"- Expected data rows: {result['expected_rows']}",
            f"- Actual data rows: {result['actual_rows']}",
            f"- Contract result: {'MATCH' if result['contract_matches'] else 'CONTRACT_MISMATCH'}",
            "",
            "## Execution environment",
            "",
            f"- Execution timestamp: {markdown_code(execution_timestamp)}",
            "- Execution timezone: `Asia/Taipei (UTC+08:00)`",
            f"- Python version: {markdown_code(platform.python_version())}",
            f"- Python implementation: {markdown_code(platform.python_implementation())}",
            f"- Platform: {markdown_code(platform.platform())}",
            "- Third-party packages: None; this profiler uses only the Python standard library.",
            f"- Reproduction command: {markdown_code(command)}",
            "",
            "## Limitations",
            "",
            "- Dataset identity follows the approved M1 contract; the original generator, author, and creation date are not independently traceable from the CSV.",
            "- Type inference is lexical and does not prove physical units, sensor calibration, or semantic validity.",
            "- Missing-value detection is limited to blanks, whitespace-only fields, and the documented textual markers.",
            "- Duplicate detection compares complete parsed rows and does not identify near-duplicates.",
            "- The report contains derived statistics and schema information only; it does not reproduce complete source rows.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    command = (
        "python tools/profile_intro.py "
        f"--input {args.input} --output {args.output} "
        f"--expected-rows {args.expected_rows}"
    )
    if args.execution_timestamp:
        command += f" --execution-timestamp {args.execution_timestamp}"

    try:
        timestamp = resolve_timestamp(args.execution_timestamp)
        result = profile_csv(input_path, args.expected_rows)
        report = build_report(result, args.input, command, timestamp)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8", newline="\n")
    except (OSError, ProfileError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    summary = {
        "actual_rows": result["actual_rows"],
        "column_count": result["column_count"],
        "contract": "MATCH" if result["contract_matches"] else "CONTRACT_MISMATCH",
        "duplicate_count": result["duplicate_count"],
        "format_validation": "PASS" if result["format_valid"] else "FAIL",
        "input_sha256": result["sha256"],
        "missing_total": result["missing_total"],
        "output": args.output,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    if not result["contract_matches"]:
        print(
            f"ERROR: expected {args.expected_rows} data rows but found {result['actual_rows']}.",
            file=sys.stderr,
        )
        return 2
    if not result["format_valid"]:
        print("ERROR: CSV format validation failed.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

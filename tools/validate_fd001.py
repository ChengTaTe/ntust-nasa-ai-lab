#!/usr/bin/env python3
"""Independent local validator for FD001 artifacts and source integrity."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import profile_fd001


AUTHORIZED_ARTIFACTS = (
    "tools/profile_fd001.py",
    "tools/validate_fd001.py",
    "tests/test_fd001.py",
    "outputs/FD001_DATASET_PROFILE.md",
    "outputs/FD001_RAW_INDEX_SPEC.md",
    "outputs/FD001_DATA_QUALITY.md",
    "outputs/FD001_SENSOR_TRENDS.md",
    "contracts/FD001_DATA_CONTRACT.md",
    "contracts/FD001_DATA_CONTRACT.json",
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate FD001 source data and generated artifacts.")
    parser.add_argument("--data-root", default="data/FD001")
    parser.add_argument("--project-root", default=".")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    try:
        before = {
            split: file_sha256(Path(args.data_root) / filename)
            for split, filename in profile_fd001.RAW_FILES.items()
        }
        analysis = profile_fd001.build_analysis(Path(args.data_root), project_root)
        missing = [path for path in AUTHORIZED_ARTIFACTS if not (project_root / path).is_file()]
        if missing:
            raise profile_fd001.ValidationError(f"Missing authorized artifacts: {missing}")

        json_path = project_root / "contracts/FD001_DATA_CONTRACT.json"
        markdown_path = project_root / "contracts/FD001_DATA_CONTRACT.md"
        contract = json.loads(json_path.read_text(encoding="utf-8"))
        markdown = markdown_path.read_text(encoding="utf-8")
        profile_fd001.validate_contract_consistency(contract, markdown)

        expected_contract = profile_fd001.build_contract(analysis)
        if contract != expected_contract:
            raise profile_fd001.ValidationError("Saved JSON contract differs from regenerated contract.")

        catalog = profile_fd001.FD001Catalog(
            analysis["datasets"]["train"],
            analysis["datasets"]["test"],
            analysis["datasets"]["rul"],
            analysis["quality"],
            analysis["trends"],
        )
        query_checks = {
            "splits": catalog.list_dataset_splits() == ["train", "test"],
            "train_units": len(catalog.list_units("train")) == 100,
            "test_units": len(catalog.list_units("test")) == 100,
            "sensors": len(catalog.list_sensors()) == 21,
            "raw_first": catalog.get_raw_row("train", 1, 1).parsed_row_index == 0,
            "raw_middle": catalog.get_raw_row("train", 50, 1).unit_id == 50,
            "raw_last": catalog.get_raw_row("train", 100, analysis["structure"]["train"]["unit_start_end"]["100"]["end"]).unit_id == 100,
            "unit_boundary": catalog.get_raw_row("test", 2, 1).unit_id == 2,
            "sensor_mapping": all(
                catalog.get_raw_source_locator("train", 1, 1, sensor)["raw_column_index"] == index
                for index, sensor in enumerate(profile_fd001.SENSOR_NAMES, start=6)
            ),
            "trend_coverage": all(
                analysis["trends"][split]["detail_count"]
                == analysis["trends"][split]["expected_detail_count"]
                for split in profile_fd001.SPLITS
            ),
            "rul_alignment": analysis["rul_alignment"]["passed"],
            "quality_gate": analysis["data_quality_gate"],
        }
        if not all(query_checks.values()):
            raise profile_fd001.ValidationError(f"Query/coverage checks failed: {query_checks}")

        after = {
            split: file_sha256(Path(args.data_root) / filename)
            for split, filename in profile_fd001.RAW_FILES.items()
        }
        if before != after:
            raise profile_fd001.ValidationError("Raw source SHA-256 changed during validation.")

        result = {
            "status": "PASS",
            "data_quality_gate": "PASS",
            "contract_consistency": "PASS",
            "json_valid": True,
            "query_checks": query_checks,
            "raw_sha256_unchanged": True,
            "artifact_sha256": {
                path: file_sha256(project_root / path) for path in AUTHORIZED_ARTIFACTS
            },
        }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, json.JSONDecodeError, profile_fd001.ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

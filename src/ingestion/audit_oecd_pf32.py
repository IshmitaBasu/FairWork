"""Profile OECD Family Database PF3.2 coverage for the FairWork pilot.

The workbook is a locally retained source snapshot. This audit reports coverage
only; it does not transform or publish source values.
"""

from __future__ import annotations

import csv
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[2]
WORKBOOK_PATH = ROOT / "data" / "raw" / "oecd" / "PF3_2_Enrolment_childcare_preschool.xlsx"
AUDIT_PATH = ROOT / "data" / "processed" / "source_audit" / "oecd_pf32_country_year_coverage.csv"
TARGET_COUNTRIES = {"Germany", "Spain", "France", "Sweden"}
START_YEAR = 2010
END_YEAR = 2023


def header_and_year_columns(rows: list[tuple[Any, ...]]) -> tuple[int, dict[int, int]]:
    for row_index, row in enumerate(rows):
        if row and row[0] == "Country":
            columns = {column_index: value for column_index, value in enumerate(row) if isinstance(value, int)}
            if columns:
                return row_index, columns
    raise ValueError("Could not find a Country/year header row in the PF3.2 workbook")


def coverage_rows(workbook_path: Path) -> list[dict[str, Any]]:
    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    sheet = workbook["Enrolment_0-2-year-olds"]
    rows = list(sheet.iter_rows(values_only=True))
    header_row, year_columns = header_and_year_columns(rows)
    coverage: list[dict[str, Any]] = []
    for row in rows[header_row + 1 :]:
        country = row[0]
        if country not in TARGET_COUNTRIES:
            continue
        for column_index, year in year_columns.items():
            value = row[column_index] if column_index < len(row) else None
            if not START_YEAR <= year <= END_YEAR or value in {None, ".."}:
                continue
            coverage.append(
                {
                    "source_id": "oecd_family_pf3_2",
                    "indicator": "enrolment_0_2_registered_ecec",
                    "country_name": country,
                    "observation_year": year,
                }
            )
    return sorted(coverage, key=lambda row: (row["country_name"], row["observation_year"]))


def main() -> None:
    if not WORKBOOK_PATH.exists():
        raise FileNotFoundError(f"Expected local source snapshot: {WORKBOOK_PATH}")
    rows = coverage_rows(WORKBOOK_PATH)
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    digest = hashlib.sha256(WORKBOOK_PATH.read_bytes()).hexdigest()
    print(f"Wrote {AUDIT_PATH.relative_to(ROOT)} ({len(rows)} country-year rows)")
    print(f"oecd_family_pf3_2: sha256={digest}, audited_at_utc={datetime.now(UTC).isoformat()}")


if __name__ == "__main__":
    main()

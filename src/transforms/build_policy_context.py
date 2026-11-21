"""Standardize the approved OECD PF3.2 policy-context observations."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[2]
COUNTRY_CROSSWALK = ROOT / "data" / "metadata" / "country_crosswalk.csv"
WORKBOOK_PATH = ROOT / "data" / "raw" / "oecd" / "PF3_2_Enrolment_childcare_preschool.xlsx"
OUTPUT_PATH = ROOT / "data" / "processed" / "harmonized" / "fact_policy_indicator.csv"
START_YEAR = 2015
END_YEAR = 2022
INDICATOR = "enrolment_0_2_registered_ecec_pct"


def header_and_year_columns(rows: list[tuple[Any, ...]]) -> tuple[int, dict[int, int]]:
    """Return the header position and a year-to-column lookup from PF3.2."""
    for row_index, row in enumerate(rows):
        if row and row[0] == "Country":
            year_columns = {value: column_index for column_index, value in enumerate(row) if isinstance(value, int)}
            if year_columns:
                return row_index, year_columns
    raise ValueError("Could not find a Country/year header row in the PF3.2 workbook")


def extract_policy_rows(workbook_path: Path, country_name_to_iso3: dict[str, str]) -> list[dict[str, Any]]:
    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        sheet = workbook["Enrolment_0-2-year-olds"]
        rows = list(sheet.iter_rows(values_only=True))
    finally:
        workbook.close()
    header_row, year_columns = header_and_year_columns(rows)
    extracted: list[dict[str, Any]] = []
    for row in rows[header_row + 1 :]:
        country_name = row[0] if row else None
        if country_name not in country_name_to_iso3:
            continue
        for year, column_index in year_columns.items():
            value = row[column_index] if column_index < len(row) else None
            if not START_YEAR <= year <= END_YEAR or value in {None, ".."}:
                continue
            extracted.append(
                {
                    "country_iso3": country_name_to_iso3[country_name],
                    "observation_year": year,
                    "indicator": INDICATOR,
                    "value": value,
                    "unit": "PC",
                    "source_id": "oecd_family_pf3_2",
                }
            )
    return sorted(extracted, key=lambda item: (item["country_iso3"], item["observation_year"]))


def main() -> None:
    if not WORKBOOK_PATH.exists():
        raise FileNotFoundError("Run the Phase 2 OECD audit before building policy context.")
    with COUNTRY_CROSSWALK.open(newline="", encoding="utf-8") as handle:
        country_name_to_iso3 = {row["country_name"]: row["country_iso3"] for row in csv.DictReader(handle)}
    records = extract_policy_rows(WORKBOOK_PATH, country_name_to_iso3)
    expected = len(country_name_to_iso3) * (END_YEAR - START_YEAR + 1)
    if len(records) != expected:
        raise ValueError(f"Expected {expected} approved policy rows; received {len(records)}")
    if any(not 0 <= float(record["value"]) <= 100 for record in records):
        raise ValueError("OECD PF3.2 values must be percentages between 0 and 100")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} policy observations to {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

"""Standardize the approved Eurostat outcome configurations for Phase 3."""

from __future__ import annotations

import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COUNTRY_CROSSWALK = ROOT / "data" / "metadata" / "country_crosswalk.csv"
RAW_DIR = ROOT / "data" / "raw" / "eurostat"
OUTPUT_DIR = ROOT / "data" / "processed" / "harmonized"
START_YEAR = 2010
END_YEAR = 2022
DATASETS = {
    "sdg_05_20": {
        "metric": "unadjusted_gender_pay_gap_pct",
        "required_dimensions": {"freq": "A", "unit": "PC", "nace_r2": "B-S_X_O"},
    },
    "sdg_05_30": {
        "metric": "gender_employment_gap_pp",
        "required_dimensions": {"freq": "A", "age": "Y20-64", "unit": "PC_PNT", "wstatus": "EMP"},
    },
}


def category_codes(dimension: dict[str, Any]) -> list[str]:
    index = dimension["category"]["index"]
    return [code for code, _ in sorted(index.items(), key=lambda item: item[1])] if isinstance(index, dict) else list(index)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def extract_dataset(dataset_id: str, geo_to_iso3: dict[str, str]) -> list[dict[str, Any]]:
    specification = DATASETS[dataset_id]
    payload = json.loads((RAW_DIR / f"{dataset_id}.json").read_text(encoding="utf-8"))
    dimension_ids = payload["id"]
    coordinates = list(
        itertools.product(*(category_codes(payload["dimension"][dimension_id]) for dimension_id in dimension_ids))
    )
    status = payload.get("status", {})
    rows: list[dict[str, Any]] = []
    for index_text, value in payload.get("value", {}).items():
        index = int(index_text)
        coordinate = dict(zip(dimension_ids, coordinates[index], strict=True))
        if any(coordinate.get(key) != expected for key, expected in specification["required_dimensions"].items()):
            continue
        geo = coordinate["geo"]
        year = coordinate["time"]
        if geo not in geo_to_iso3 or not year.isdigit() or not START_YEAR <= int(year) <= END_YEAR:
            continue
        rows.append(
            {
                "country_iso3": geo_to_iso3[geo],
                "observation_year": int(year),
                "metric": specification["metric"],
                "value": value,
                "unit": coordinate["unit"],
                "observation_flag": status.get(index_text, ""),
                "source_id": f"eurostat_{dataset_id}",
            }
        )
    return rows


def main() -> None:
    with COUNTRY_CROSSWALK.open(newline="", encoding="utf-8") as handle:
        geo_to_iso3 = {row["eurostat_geo"]: row["country_iso3"] for row in csv.DictReader(handle)}
    facts = sorted(
        [row for dataset_id in DATASETS for row in extract_dataset(dataset_id, geo_to_iso3)],
        key=lambda row: (row["country_iso3"], row["observation_year"], row["metric"]),
    )
    expected = len(geo_to_iso3) * (END_YEAR - START_YEAR + 1) * len(DATASETS)
    if len(facts) != expected:
        raise ValueError(f"Expected {expected} approved outcome rows; received {len(facts)}")

    by_country_year: dict[tuple[str, int], dict[str, Any]] = defaultdict(dict)
    for fact in facts:
        row = by_country_year[(fact["country_iso3"], fact["observation_year"])]
        row["country_iso3"] = fact["country_iso3"]
        row["observation_year"] = fact["observation_year"]
        prefix = "pay_gap" if fact["metric"] == "unadjusted_gender_pay_gap_pct" else "employment_gap"
        row[f"{prefix}_value"] = fact["value"]
        row[f"{prefix}_flag"] = fact["observation_flag"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUTPUT_DIR / "fact_gender_outcome.csv",
        facts,
        ["country_iso3", "observation_year", "metric", "value", "unit", "observation_flag", "source_id"],
    )
    write_csv(
        OUTPUT_DIR / "country_year_outcomes.csv",
        [by_country_year[key] for key in sorted(by_country_year)],
        ["country_iso3", "observation_year", "pay_gap_value", "pay_gap_flag", "employment_gap_value", "employment_gap_flag"],
    )
    print(f"Wrote {len(facts)} outcome facts and {len(by_country_year)} country-year rows")


if __name__ == "__main__":
    main()

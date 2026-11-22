"""Create local, reviewed CHES party-position facts for dashboard exploration."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COUNTRY_CROSSWALK = ROOT / "data" / "metadata" / "country_crosswalk.csv"
PARTY_CROSSWALK = ROOT / "data" / "processed" / "political_context" / "party_crosswalk_review.csv"
CHES_SOURCE = ROOT / "data" / "raw" / "ches" / "1999-2024_CHES_dataset_meansV2.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "harmonized" / "fact_ches_party_position.csv"
CHES_WAVES = {2010, 2014, 2019}


def optional_float(value: str) -> float | None:
    return float(value) if value not in {"", "..", None} else None


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    required = [COUNTRY_CROSSWALK, PARTY_CROSSWALK, CHES_SOURCE]
    if missing := [str(path.relative_to(ROOT)) for path in required if not path.exists()]:
        raise FileNotFoundError("Build Phase 3 political context first: " + ", ".join(missing))
    with COUNTRY_CROSSWALK.open(newline="", encoding="utf-8") as handle:
        countries = list(csv.DictReader(handle))
    countries_by_ches = {row["ches_country_code"]: row for row in countries}
    with PARTY_CROSSWALK.open(newline="", encoding="utf-8") as handle:
        accepted = {
            (row["country_iso3"], row["ches_party_id"]): row
            for row in csv.DictReader(handle)
            if row["mapping_status"].startswith("accepted_") and row["ches_party_id"]
        }

    positions: list[dict[str, Any]] = []
    with CHES_SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if int(row["year"]) not in CHES_WAVES or row["country"] not in countries_by_ches:
                continue
            country = countries_by_ches[row["country"]]
            accepted_row = accepted.get((country["country_iso3"], row["party_id"]))
            if accepted_row is None or optional_float(row["lrgen"]) is None:
                continue
            positions.append(
                {
                    "country_iso3": country["country_iso3"],
                    "country_name": country["country_name"],
                    "ches_wave": int(row["year"]),
                    "ches_party_id": row["party_id"],
                    "party_name": row["party"],
                    "parlgov_party_name": accepted_row["parlgov_party_name"],
                    "lrgen": optional_float(row["lrgen"]),
                    "vote_share_pct": optional_float(row["vote"]),
                    "seat_share_pct": optional_float(row["seat"]),
                    "womens_rights_position": optional_float(row["womens_rights"]),
                    "mapping_status": accepted_row["mapping_status"],
                    "source_id": "ches_europe_trend_1999_2024",
                }
            )
    positions = sorted(positions, key=lambda row: (row["country_iso3"], row["ches_wave"], row["party_name"]))
    if not positions:
        raise ValueError("No accepted CHES positions found for the pilot parties and selected waves")
    duplicates = {(row["country_iso3"], row["ches_wave"], row["ches_party_id"]) for row in positions}
    if len(duplicates) != len(positions):
        raise ValueError("CHES party positions must be unique by country, wave and party")
    if any(not 0 <= row["lrgen"] <= 10 for row in positions):
        raise ValueError("CHES lrgen values must remain on the documented 0–10 scale")
    write_csv(OUTPUT_PATH, positions)
    print(f"Wrote {len(positions)} reviewed CHES party-position rows to {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

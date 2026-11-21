"""Build dated cabinet periods and a source-identifier party crosswalk.

All cabinet periods are half-open: [start_date, end_date_exclusive). This
avoids inventing a termination date where ParlGov only supplies the next
cabinet's start. Party matches use ParlGov's CHES identifier only; no fuzzy
name matching is performed.
"""

from __future__ import annotations

import csv
import io
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ARCHIVE = ROOT / "data" / "raw" / "parlgov" / "parlgov-development_csv-utf-8.zip"
CHES_SOURCE = ROOT / "data" / "raw" / "ches" / "1999-2024_CHES_dataset_meansV2.csv"
COUNTRY_CROSSWALK = ROOT / "data" / "metadata" / "country_crosswalk.csv"
PARTY_OVERRIDES = ROOT / "data" / "metadata" / "party_crosswalk_overrides.csv"
OUTPUT_DIR = ROOT / "data" / "processed" / "political_context"
START_DATE = date(2010, 1, 1)
END_DATE_EXCLUSIVE = date(2023, 1, 1)
CHES_WAVES = {2010, 2014, 2019}


def read_csv_from_zip(archive: zipfile.ZipFile, name: str) -> list[dict[str, str]]:
    with archive.open(name) as handle:
        return list(csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8-sig", newline="")))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def overlap(start: date, end_exclusive: date | None) -> bool:
    return start < END_DATE_EXCLUSIVE and (end_exclusive is None or end_exclusive > START_DATE)


def load_ches_ids() -> set[tuple[str, str]]:
    with CHES_SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        return {
            (row["country"], row["party_id"])
            for row in csv.DictReader(handle)
            if int(row["year"]) in CHES_WAVES
        }


def load_party_overrides() -> dict[tuple[str, str], dict[str, str]]:
    with PARTY_OVERRIDES.open(newline="", encoding="utf-8") as handle:
        return {
            (row["country_iso3"], row["parlgov_party_id"]): row
            for row in csv.DictReader(handle)
        }


def main() -> None:
    if not SOURCE_ARCHIVE.exists() or not CHES_SOURCE.exists():
        raise FileNotFoundError("Run the Phase 2 source audits before building political context.")

    with COUNTRY_CROSSWALK.open(newline="", encoding="utf-8") as handle:
        countries = list(csv.DictReader(handle))
    by_parlgov_country = {row["parlgov_country_id"]: row for row in countries}
    ches_ids = load_ches_ids()
    party_overrides = load_party_overrides()

    with zipfile.ZipFile(SOURCE_ARCHIVE) as archive:
        cabinets = read_csv_from_zip(archive, "cabinet.csv")
        cabinet_parties = read_csv_from_zip(archive, "cabinet_party.csv")
        parties = read_csv_from_zip(archive, "party.csv")

    cabinets_by_country: dict[str, list[dict[str, str]]] = defaultdict(list)
    for cabinet in cabinets:
        if cabinet["country_id"] in by_parlgov_country:
            cabinets_by_country[cabinet["country_id"]].append(cabinet)

    period_rows: list[dict[str, Any]] = []
    in_scope_cabinet_ids: set[str] = set()
    for country_id, country_cabinets in cabinets_by_country.items():
        ordered = sorted(country_cabinets, key=lambda row: (row["start_date"], row["id"]))
        for index, cabinet in enumerate(ordered):
            start = date.fromisoformat(cabinet["start_date"])
            next_start = date.fromisoformat(ordered[index + 1]["start_date"]) if index + 1 < len(ordered) else None
            if not overlap(start, next_start):
                continue
            country = by_parlgov_country[country_id]
            in_scope_cabinet_ids.add(cabinet["id"])
            period_rows.append(
                {
                    "country_iso3": country["country_iso3"],
                    "parlgov_cabinet_id": cabinet["id"],
                    "cabinet_name": cabinet["name"],
                    "start_date": cabinet["start_date"],
                    "end_date_exclusive": next_start.isoformat() if next_start else "",
                    "caretaker": cabinet["caretaker"],
                    "date_rule": "next_cabinet_start_exclusive",
                }
            )

    party_by_id = {party["id"]: party for party in parties}
    bridge_rows: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    cabinet_country = {row["parlgov_cabinet_id"]: row["country_iso3"] for row in period_rows}
    country_by_iso3 = {row["country_iso3"]: row for row in countries}
    for membership in cabinet_parties:
        cabinet_id = membership["cabinet_id"]
        if cabinet_id not in in_scope_cabinet_ids:
            continue
        party = party_by_id.get(membership["party_id"])
        if party is None:
            continue
        country_iso3 = cabinet_country[cabinet_id]
        pair = (country_iso3, party["id"])
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        country = country_by_iso3[country_iso3]
        ches_party_id = party["chess"].strip()
        has_source_identifier = bool(ches_party_id)
        has_wave_observation = (country["ches_country_code"], ches_party_id) in ches_ids if has_source_identifier else False
        override = party_overrides.get(pair)
        if override:
            ches_party_id = override["ches_party_id"]
            has_wave_observation = (country["ches_country_code"], ches_party_id) in ches_ids
            mapping_method = override["mapping_method"]
            mapping_status = "accepted_manual_continuity_review" if has_wave_observation else "invalid_manual_override"
        else:
            mapping_method = "parlgov_chess_identifier" if has_source_identifier else "none"
            mapping_status = "accepted_source_identifier" if has_wave_observation else "unmatched_or_outside_ches_waves"
        bridge_rows.append(
            {
                "country_iso3": country_iso3,
                "parlgov_party_id": party["id"],
                "parlgov_party_short": party["name_short"],
                "parlgov_party_name": party["name"],
                "ches_party_id": ches_party_id,
                "mapping_method": mapping_method,
                "mapping_status": mapping_status,
                "ches_wave_observation": str(has_wave_observation).lower(),
                "review_action": "none" if mapping_status.startswith("accepted_") else "manual_review_required",
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUTPUT_DIR / "cabinet_periods.csv",
        sorted(period_rows, key=lambda row: (row["country_iso3"], row["start_date"])),
        ["country_iso3", "parlgov_cabinet_id", "cabinet_name", "start_date", "end_date_exclusive", "caretaker", "date_rule"],
    )
    write_csv(
        OUTPUT_DIR / "party_crosswalk_review.csv",
        sorted(bridge_rows, key=lambda row: (row["country_iso3"], row["parlgov_party_name"])),
        [
            "country_iso3",
            "parlgov_party_id",
            "parlgov_party_short",
            "parlgov_party_name",
            "ches_party_id",
            "mapping_method",
            "mapping_status",
            "ches_wave_observation",
            "review_action",
        ],
    )
    accepted = sum(row["mapping_status"].startswith("accepted_") for row in bridge_rows)
    print(f"Wrote {len(period_rows)} cabinet periods and {len(bridge_rows)} unique cabinet-party mappings")
    print(f"Source-identifier matches with a CHES wave observation: {accepted}; review queue: {len(bridge_rows) - accepted}")


if __name__ == "__main__":
    main()

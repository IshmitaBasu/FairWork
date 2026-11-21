"""Retrieve and profile the CHES trend file and ParlGov cabinet release.

The script records coverage and candidate identifiers only. It does not link
parties across sources, select an ideology variable, or infer cabinet exposure.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from collections import Counter, defaultdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
AUDIT_DIR = ROOT / "data" / "processed" / "source_audit"
START_YEAR = 2010
END_YEAR = 2023
TARGETS = {
    "Germany": {"Germany", "DE", "DEU"},
    "Spain": {"Spain", "ES", "ESP"},
    "France": {"France", "FR", "FRA"},
    "Sweden": {"Sweden", "SE", "SWE"},
}
CHES_COUNTRY_CODES = {"3": "Germany", "5": "Spain", "14": "France", "16": "Sweden"}
CHES_URL = (
    "https://github.com/chesdata/chesdata.github.io/releases/download/ches-trend/"
    "1999-2024_CHES_dataset_meansV2.csv"
)
PARLGOV_URL = "https://www.parlgov.org/data/parlgov-development_csv-utf-8.zip"


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "FairWork-source-audit/0.1"})
    with urlopen(request, timeout=120) as response:  # nosec B310: fixed official public endpoints
        return response.read()


def normalize(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def first_column(fieldnames: Iterable[str], candidates: Iterable[str]) -> str | None:
    by_normalized = {normalize(field): field for field in fieldnames}
    for candidate in candidates:
        if normalize(candidate) in by_normalized:
            return by_normalized[normalize(candidate)]
    return None


def country_name(value: str) -> str | None:
    cleaned = value.strip()
    for name, aliases in TARGETS.items():
        if cleaned in aliases:
            return name
    return None


def ches_country_name(value: str) -> str | None:
    """Return a pilot country for the code used in the CHES trend file.

    The mapping must be checked against the downloaded CHES codebook before it
    is used for party matching; here it supports a coverage-only audit.
    """
    return CHES_COUNTRY_CODES.get(value.strip()) or country_name(value)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def audit_ches(body: bytes) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(body.decode("utf-8-sig")))
    fields = reader.fieldnames or []
    country_column = first_column(fields, ["country", "country_name", "countrycode", "country_code"])
    wave_column = first_column(fields, ["year", "survey_year", "wave"])
    party_id_column = first_column(fields, ["party_id", "partyid", "id_party"])
    party_name_column = first_column(fields, ["party", "party_name", "partyname"])
    if not country_column or not wave_column:
        raise ValueError(f"CHES required country/year columns not found; headers: {fields}")

    parties: dict[tuple[str, int], set[str]] = defaultdict(set)
    rows_in_scope: Counter[tuple[str, int]] = Counter()
    for row in reader:
        country = ches_country_name(row[country_column])
        try:
            wave = int(float(row[wave_column]))
        except (TypeError, ValueError):
            continue
        if country is None or not START_YEAR <= wave <= END_YEAR:
            continue
        rows_in_scope[(country, wave)] += 1
        identifier = row.get(party_id_column, "") if party_id_column else ""
        if not identifier and party_name_column:
            identifier = row[party_name_column]
        if identifier:
            parties[(country, wave)].add(identifier)

    rows = [
        {
            "source_id": "ches_europe_trend_1999_2024",
            "country_name": country,
            "survey_wave": wave,
            "party_rows": rows_in_scope[(country, wave)],
            "distinct_party_identifiers": len(parties[(country, wave)]),
        }
        for country, wave in sorted(rows_in_scope)
    ]
    metadata = {
        "source_id": "ches_europe_trend_1999_2024",
        "headers": fields,
        "country_column": country_column,
        "wave_column": wave_column,
        "party_id_column": party_id_column,
        "party_name_column": party_name_column,
        "rows_in_requested_scope": sum(rows_in_scope.values()),
        "country_wave_rows": len(rows),
        "validation_note": "Original scales, codebook, citation and licence remain subject to review.",
    }
    return rows, metadata


def cabinet_member(names: list[str]) -> str:
    preferred = ["cabinet.csv", "view_cabinet.csv"]
    for name in preferred:
        if name in names:
            return name
    candidates = [name for name in names if name.endswith(".csv") and "cabinet" in name.lower()]
    if not candidates:
        raise ValueError("No cabinet CSV found in ParlGov archive")
    return sorted(candidates)[0]


def audit_parlgov(body: bytes) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        member = cabinet_member(archive.namelist())
        with archive.open("country.csv") as handle:
            country_reader = csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8-sig", newline=""))
            country_fields = country_reader.fieldnames or []
            country_id_column = first_column(country_fields, ["id", "country_id"])
            country_name_column = first_column(country_fields, ["name", "country_name"])
            if not country_id_column or not country_name_column:
                raise ValueError(f"ParlGov country columns not found; headers: {country_fields}")
            countries_by_id = {
                row[country_id_column]: row[country_name_column]
                for row in country_reader
                if country_name(row[country_name_column]) is not None
            }
        with archive.open(member) as handle:
            reader = csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8-sig", newline=""))
            fields = reader.fieldnames or []
            country_column = first_column(fields, ["country_id", "country", "country_name"])
            start_column = first_column(fields, ["cabinet_start_date", "start_date", "date_start"])
            cabinet_id_column = first_column(fields, ["cabinet_id", "id"])
            if not country_column or not start_column:
                raise ValueError(f"ParlGov required country/start columns not found; headers: {fields}")

            cabinets_by_country: dict[str, list[tuple[date, str]]] = defaultdict(list)
            for row in reader:
                country = country_name(countries_by_id.get(row[country_column], row[country_column]))
                try:
                    start = date.fromisoformat(row[start_column])
                except ValueError:
                    continue
                if country is None:
                    continue
                cabinet_id = row.get(cabinet_id_column, "") if cabinet_id_column else ""
                cabinets_by_country[country].append((start, cabinet_id))

    window_start = date(START_YEAR, 1, 1)
    window_end = date(END_YEAR, 12, 31)
    cabinet_counts: Counter[str] = Counter()
    for country, cabinets in cabinets_by_country.items():
        ordered = sorted(cabinets)
        for index, (start, _) in enumerate(ordered):
            next_start = ordered[index + 1][0] if index + 1 < len(ordered) else None
            ends_after_window_start = next_start is None or next_start >= window_start
            if start <= window_end and ends_after_window_start:
                cabinet_counts[country] += 1

    rows = [
        {
            "source_id": "parlgov_development_2023_11_04",
            "country_name": country,
            "overlapping_cabinet_periods": cabinet_counts[country],
            "window_start_year": START_YEAR,
            "window_end_year": END_YEAR,
        }
        for country in TARGETS
    ]
    metadata = {
        "source_id": "parlgov_development_2023_11_04",
        "cabinet_file": member,
        "headers": fields,
        "country_column": country_column,
        "start_column": start_column,
        "cabinet_id_column": cabinet_id_column,
        "validation_note": "Cabinet periods are inferred from each next recorded start date only for coverage. Cabinet-party bridging, date verification and release-limit handling remain pending.",
    }
    return rows, metadata


def snapshot_metadata(path: Path, body: bytes, *, reused: bool) -> dict[str, Any]:
    return {
        "snapshot_path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(body).hexdigest(),
        "bytes": len(body),
        "audited_at_utc": datetime.now(UTC).isoformat(),
        "snapshot_reused": reused,
    }


def retrieve_snapshot(path: Path, url: str, *, refresh: bool) -> tuple[bytes, dict[str, Any]]:
    if path.exists() and not refresh:
        body = path.read_bytes()
        return body, snapshot_metadata(path, body, reused=True)
    body = fetch(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return body, snapshot_metadata(path, body, reused=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["ches", "parlgov", "all"], default="all")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Download fresh copies even when a local raw snapshot already exists.",
    )
    args = parser.parse_args()
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit: list[dict[str, Any]] = []

    if args.source in {"ches", "all"}:
        body, metadata = retrieve_snapshot(
            RAW_DIR / "ches" / "1999-2024_CHES_dataset_meansV2.csv", CHES_URL, refresh=args.refresh
        )
        rows, profile = audit_ches(body)
        metadata.update(profile)
        metadata["retrieval_url"] = CHES_URL
        write_csv(
            AUDIT_DIR / "ches_country_wave_coverage.csv",
            rows,
            ["source_id", "country_name", "survey_wave", "party_rows", "distinct_party_identifiers"],
        )
        audit.append(metadata)

    if args.source in {"parlgov", "all"}:
        body, metadata = retrieve_snapshot(
            RAW_DIR / "parlgov" / "parlgov-development_csv-utf-8.zip", PARLGOV_URL, refresh=args.refresh
        )
        rows, profile = audit_parlgov(body)
        metadata.update(profile)
        metadata["retrieval_url"] = PARLGOV_URL
        write_csv(
            AUDIT_DIR / "parlgov_cabinet_coverage.csv",
            rows,
            ["source_id", "country_name", "overlapping_cabinet_periods", "window_start_year", "window_end_year"],
        )
        audit.append(metadata)

    audit_path = AUDIT_DIR / "political_sources_retrieval_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    for record in audit:
        print(f"{record['source_id']}: sha256={record['sha256']}, {record['bytes']} bytes")
    print(f"Wrote {audit_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

"""Download and profile the Eurostat outcome datasets used by FairWork.

This script deliberately audits every returned configuration for the chosen
countries. Choosing the app's final age, unit or other dimension filters is a
separate, documented decision after this evidence gate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import UTC, datetime
from itertools import product
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "eurostat"
AUDIT_DIR = ROOT / "data" / "processed" / "source_audit"
COUNTRIES = {"DE": "Germany", "ES": "Spain", "FR": "France", "SE": "Sweden"}
DATASETS = {
    "sdg_05_20": "unadjusted_gender_pay_gap",
    "sdg_05_30": "gender_employment_gap",
}
API_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "FairWork-source-audit/0.1"})
    with urlopen(request, timeout=60) as response:  # nosec B310: fixed official public endpoints
        return response.read()


def category_codes(dimension: dict[str, Any]) -> list[str]:
    index = dimension["category"]["index"]
    if isinstance(index, dict):
        return [code for code, _ in sorted(index.items(), key=lambda item: item[1])]
    return list(index)


def dataset_dimensions(payload: dict[str, Any]) -> dict[str, list[str]]:
    return {
        dimension_id: category_codes(payload["dimension"][dimension_id])
        for dimension_id in payload["id"]
    }


def value_items(values: Any) -> list[tuple[int, float]]:
    if isinstance(values, dict):
        return [(int(index), value) for index, value in values.items()]
    if isinstance(values, list):
        return [(index, value) for index, value in enumerate(values) if value is not None]
    raise TypeError("Eurostat JSON-stat 'value' must be a mapping or list")


def coverage_rows(payload: dict[str, Any], dataset_id: str) -> tuple[list[dict[str, Any]], int]:
    dimensions = dataset_dimensions(payload)
    dimension_ids = payload["id"]
    if "geo" not in dimensions or "time" not in dimensions:
        raise ValueError(f"{dataset_id} did not include required geo and time dimensions")

    codes_by_dimension = [dimensions[dimension_id] for dimension_id in dimension_ids]
    positions = list(product(*codes_by_dimension))
    observed_configurations: dict[tuple[str, str], set[tuple[str, ...]]] = defaultdict(set)
    flagged_configurations: dict[tuple[str, str], set[tuple[str, ...]]] = defaultdict(set)
    flags_by_country_year: dict[tuple[str, str], set[str]] = defaultdict(set)
    status = payload.get("status", {})
    observed_values = 0

    for index, value in value_items(payload.get("value", {})):
        if value is None or index >= len(positions):
            continue
        coordinate = dict(zip(dimension_ids, positions[index], strict=True))
        country = coordinate["geo"]
        year = coordinate["time"]
        if country not in COUNTRIES or not year.isdigit() or not 2010 <= int(year) <= 2023:
            continue
        configuration = tuple(
            f"{dimension_id}={coordinate[dimension_id]}"
            for dimension_id in dimension_ids
            if dimension_id not in {"geo", "time"}
        )
        observed_configurations[(country, year)].add(configuration)
        flag = status.get(str(index)) if isinstance(status, dict) else None
        if flag:
            flagged_configurations[(country, year)].add(configuration)
            flags_by_country_year[(country, year)].add(str(flag))
        observed_values += 1

    rows = [
        {
            "source_id": f"eurostat_{dataset_id}",
            "metric": DATASETS[dataset_id],
            "country_iso2": country,
            "country_name": COUNTRIES[country],
            "observation_year": int(year),
            "observed_configurations": len(configurations),
            "flagged_configurations": len(flagged_configurations[(country, year)]),
            "observation_flags": "|".join(sorted(flags_by_country_year[(country, year)])),
        }
        for (country, year), configurations in sorted(observed_configurations.items())
    ]
    return rows, observed_values


def download_and_audit(dataset_id: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    query = "&".join(["lang=en", *(f"geo={country}" for country in COUNTRIES)])
    url = f"{API_BASE}/{dataset_id}?{query}"
    body = fetch(url)
    payload = json.loads(body)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = RAW_DIR / f"{dataset_id}.json"
    snapshot_path.write_bytes(body)

    rows, observed_values = coverage_rows(payload, dataset_id)
    dimensions = dataset_dimensions(payload)
    metadata = {
        "source_id": f"eurostat_{dataset_id}",
        "retrieval_url": url,
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "snapshot_path": str(snapshot_path.relative_to(ROOT)).replace("\\", "/"),
        "sha256": hashlib.sha256(body).hexdigest(),
        "bytes": len(body),
        "dimension_categories": {key: len(value) for key, value in dimensions.items()},
        "observations_in_requested_scope": observed_values,
        "country_year_rows": len(rows),
        "validation_note": "Dimension, unit and flag selection remains pending review.",
    }
    return rows, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        choices=[*DATASETS, "all"],
        default="all",
        help="Eurostat dataset to retrieve (default: all).",
    )
    args = parser.parse_args()
    requested_datasets = list(DATASETS) if args.dataset == "all" else [args.dataset]

    all_rows: list[dict[str, Any]] = []
    audit: list[dict[str, Any]] = []
    for dataset_id in requested_datasets:
        rows, metadata = download_and_audit(dataset_id)
        all_rows.extend(rows)
        audit.append(metadata)

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    coverage_path = AUDIT_DIR / "eurostat_country_year_coverage.csv"
    with coverage_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "source_id",
                "metric",
                "country_iso2",
                "country_name",
                "observation_year",
                "observed_configurations",
                "flagged_configurations",
                "observation_flags",
            ],
        )
        writer.writeheader()
        writer.writerows(all_rows)

    audit_path = AUDIT_DIR / "eurostat_retrieval_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {coverage_path.relative_to(ROOT)} ({len(all_rows)} country-year rows)")
    print(f"Wrote {audit_path.relative_to(ROOT)}")
    for record in audit:
        print(
            f"{record['source_id']}: {record['observations_in_requested_scope']} observations, "
            f"sha256={record['sha256']}"
        )


if __name__ == "__main__":
    main()

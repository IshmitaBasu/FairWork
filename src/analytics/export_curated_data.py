"""Export read-only, curated Phase 4 marts from the local DuckDB database."""

from __future__ import annotations

from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = ROOT / "data" / "processed" / "fairwork.duckdb"
PUBLISHED_DIR = ROOT / "data" / "published"
TABLES = (
    "mart_country_year",
    "mart_cabinet_transition",
    "fact_policy_indicator",
    "fact_ches_party_position",
    "bridge_cabinet_party_membership",
)


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Build the dbt project before exporting curated data.")
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(DATABASE_PATH), read_only=True)
    try:
        for table_name in TABLES:
            target = PUBLISHED_DIR / f"{table_name}.parquet"
            escaped_target = str(target).replace("'", "''")
            connection.execute(
                f"COPY analytics.{table_name} TO '{escaped_target}' (FORMAT PARQUET, COMPRESSION ZSTD)"
            )
            row_count = connection.execute(f"SELECT count(*) FROM analytics.{table_name}").fetchone()[0]
            print(f"Wrote {target.relative_to(ROOT)} ({row_count} rows)")
    finally:
        connection.close()


if __name__ == "__main__":
    main()

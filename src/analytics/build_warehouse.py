"""Build and validate the local FairWork DuckDB analytics warehouse.

This module is deliberately executable without dbt so a restricted local Python
environment cannot prevent the project from producing its documented, tested
analytics tables.  The dbt project mirrors these staged and mart grains.
"""

from __future__ import annotations

from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = ROOT / "data" / "processed" / "fairwork.duckdb"
INPUTS = {
    "country": ROOT / "data" / "metadata" / "country_crosswalk.csv",
    "gender_outcome": ROOT / "data" / "processed" / "harmonized" / "fact_gender_outcome.csv",
    "country_year": ROOT / "data" / "processed" / "harmonized" / "country_year_outcomes.csv",
    "policy": ROOT / "data" / "processed" / "harmonized" / "fact_policy_indicator.csv",
    "cabinet": ROOT / "data" / "processed" / "political_context" / "cabinet_periods.csv",
    "cabinet_party_membership": ROOT / "data" / "processed" / "political_context" / "cabinet_party_membership.csv",
    "party_crosswalk": ROOT / "data" / "processed" / "political_context" / "party_crosswalk_review.csv",
    "ches_position": ROOT / "data" / "processed" / "harmonized" / "fact_ches_party_position.csv",
}
PILOT_COUNTS = {
    "dim_country": 4,
    "fact_gender_outcome": 104,
    "stg_country_year_outcomes": 52,
    "fact_policy_indicator": 32,
    "fact_ches_party_position": 54,
    "bridge_cabinet_party_membership": 83,
    "mart_country_year": 52,
    "mart_cabinet_transition": 34,
}


def sql_path(path: Path) -> str:
    return str(path).replace("'", "''")


def assert_zero(connection: duckdb.DuckDBPyConnection, name: str, query: str) -> None:
    failures = connection.execute(query).fetchone()[0]
    if failures:
        raise ValueError(f"Validation failed: {name} ({failures} invalid row(s))")


def build_warehouse(
    inputs: dict[str, Path] = INPUTS,
    database_path: Path = DATABASE_PATH,
    expected_counts: dict[str, int] | None = PILOT_COUNTS,
) -> dict[str, int]:
    """Build the warehouse from a supplied input map and return table counts.

    Production uses the approved local input paths and their fixed pilot counts.
    Tests pass small, invented fixture files and set ``expected_counts`` to
    ``None`` so structural validation can run without real source data.
    """
    missing = [str(path) for path in inputs.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Build Phase 3 and policy-context inputs first: {', '.join(missing)}")

    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(database_path))
    try:
        connection.execute("DROP SCHEMA IF EXISTS analytics CASCADE")
        connection.execute("CREATE SCHEMA analytics")
        connection.execute(
            f"""
            CREATE TABLE analytics.dim_country AS
            SELECT country_iso3, country_name, eurostat_geo,
                   cast(ches_country_code AS integer) AS ches_country_code,
                   cast(parlgov_country_id AS integer) AS parlgov_country_id,
                   parlgov_country_short
            FROM read_csv_auto('{sql_path(inputs['country'])}', header = true)
            """
        )
        connection.execute(
            f"""
            CREATE TABLE analytics.bridge_cabinet_party_membership AS
            SELECT country_iso3, cast(parlgov_cabinet_id AS integer) AS parlgov_cabinet_id,
                   cabinet_name, cast(start_date AS date) AS start_date,
                   nullif(cast(end_date_exclusive AS varchar), '')::date AS end_date_exclusive,
                   cast(parlgov_party_id AS integer) AS parlgov_party_id,
                   parlgov_party_short, parlgov_party_name,
                   nullif(cast(ches_party_id AS varchar), '')::integer AS ches_party_id,
                   mapping_status, review_action
            FROM read_csv_auto('{sql_path(inputs['cabinet_party_membership'])}', header = true)
            """
        )
        connection.execute(
            f"""
            CREATE TABLE analytics.fact_ches_party_position AS
            SELECT country_iso3, country_name, cast(ches_wave AS integer) AS ches_wave,
                   cast(ches_party_id AS integer) AS ches_party_id, party_name, parlgov_party_name,
                   cast(lrgen AS double) AS lrgen, cast(vote_share_pct AS double) AS vote_share_pct,
                   cast(seat_share_pct AS double) AS seat_share_pct,
                   cast(womens_rights_position AS double) AS womens_rights_position,
                   mapping_status, source_id
            FROM read_csv_auto('{sql_path(inputs['ches_position'])}', header = true)
            """
        )
        connection.execute(
            f"""
            CREATE TABLE analytics.fact_gender_outcome AS
            SELECT country_iso3, cast(observation_year AS integer) AS observation_year,
                   metric, cast(value AS double) AS value, unit, observation_flag, source_id
            FROM read_csv_auto('{sql_path(inputs['gender_outcome'])}', header = true)
            """
        )
        connection.execute(
            f"""
            CREATE TABLE analytics.stg_country_year_outcomes AS
            SELECT country_iso3, cast(observation_year AS integer) AS observation_year,
                   cast(pay_gap_value AS double) AS pay_gap_value, pay_gap_flag,
                   cast(employment_gap_value AS double) AS employment_gap_value, employment_gap_flag
            FROM read_csv_auto('{sql_path(inputs['country_year'])}', header = true)
            """
        )
        connection.execute(
            f"""
            CREATE TABLE analytics.fact_policy_indicator AS
            SELECT country_iso3, cast(observation_year AS integer) AS observation_year,
                   indicator, cast(value AS double) AS value, unit, source_id
            FROM read_csv_auto('{sql_path(inputs['policy'])}', header = true)
            """
        )
        connection.execute(
            f"""
            CREATE TABLE analytics.stg_cabinet_period AS
            SELECT country_iso3, cast(parlgov_cabinet_id AS integer) AS parlgov_cabinet_id,
                   cabinet_name, cast(start_date AS date) AS start_date,
                   nullif(cast(end_date_exclusive AS varchar), '')::date AS end_date_exclusive,
                   cast(caretaker AS boolean) AS caretaker, date_rule
            FROM read_csv_auto('{sql_path(inputs['cabinet'])}', header = true)
            """
        )
        connection.execute(
            f"""
            CREATE TABLE analytics.bridge_party_crosswalk AS
            SELECT country_iso3, cast(parlgov_party_id AS integer) AS parlgov_party_id,
                   parlgov_party_short, parlgov_party_name, ches_party_id,
                   mapping_method, mapping_status,
                   cast(ches_wave_observation AS boolean) AS ches_wave_observation, review_action
            FROM read_csv_auto('{sql_path(inputs['party_crosswalk'])}', header = true)
            """
        )
        connection.execute(
            """
            CREATE TABLE analytics.mart_country_year AS
            SELECT outcomes.country_iso3, country.country_name, outcomes.observation_year,
                   outcomes.pay_gap_value, outcomes.pay_gap_flag,
                   outcomes.employment_gap_value, outcomes.employment_gap_flag,
                   policy.value AS enrolment_0_2_registered_ecec_pct,
                   policy.source_id AS policy_source_id
            FROM analytics.stg_country_year_outcomes AS outcomes
            INNER JOIN analytics.dim_country AS country USING (country_iso3)
            LEFT JOIN analytics.fact_policy_indicator AS policy
                ON outcomes.country_iso3 = policy.country_iso3
                AND outcomes.observation_year = policy.observation_year
                AND policy.indicator = 'enrolment_0_2_registered_ecec_pct'
            """
        )
        connection.execute(
            """
            CREATE TABLE analytics.mart_cabinet_transition AS
            WITH periods AS (
                SELECT *,
                       lag(parlgov_cabinet_id) OVER (
                           PARTITION BY country_iso3 ORDER BY start_date, parlgov_cabinet_id
                       ) AS previous_parlgov_cabinet_id,
                       lag(cabinet_name) OVER (
                           PARTITION BY country_iso3 ORDER BY start_date, parlgov_cabinet_id
                       ) AS previous_cabinet_name
                FROM analytics.stg_cabinet_period
            )
            SELECT *,
                   CASE WHEN previous_parlgov_cabinet_id IS NULL THEN 'first_observed_period'
                        ELSE 'cabinet_change' END AS transition_type
            FROM periods
            """
        )

        table_names = (
            "dim_country",
            "fact_gender_outcome",
            "stg_country_year_outcomes",
            "fact_policy_indicator",
            "fact_ches_party_position",
            "bridge_cabinet_party_membership",
            "mart_country_year",
            "mart_cabinet_transition",
        )
        table_counts = {
            table_name: connection.execute(f"SELECT count(*) FROM analytics.{table_name}").fetchone()[0]
            for table_name in table_names
        }
        if expected_counts is not None:
            for table_name, expected in expected_counts.items():
                actual = table_counts[table_name]
                if actual != expected:
                    raise ValueError(f"Expected {expected} rows in {table_name}; received {actual}")
        assert_zero(
            connection,
            "country identifiers are unique and populated",
            """SELECT count(*) FROM (
                   SELECT country_iso3 FROM analytics.dim_country
                   GROUP BY country_iso3 HAVING country_iso3 IS NULL OR count(*) != 1
               )""",
        )
        assert_zero(
            connection,
            "cabinet-party membership keys",
            """SELECT count(*) FROM (
                   SELECT parlgov_cabinet_id, parlgov_party_id FROM analytics.bridge_cabinet_party_membership
                   GROUP BY 1, 2 HAVING count(*) != 1
               )""",
        )
        assert_zero(
            connection,
            "CHES party-position keys",
            """SELECT count(*) FROM (
                   SELECT country_iso3, ches_wave, ches_party_id FROM analytics.fact_ches_party_position
                   GROUP BY 1, 2, 3 HAVING count(*) != 1
               )""",
        )
        assert_zero(
            connection,
            "CHES left-right scale",
            "SELECT count(*) FROM analytics.fact_ches_party_position WHERE lrgen < 0 OR lrgen > 10",
        )
        assert_zero(
            connection,
            "gender outcome country-year-metric keys",
            """SELECT count(*) FROM (
                   SELECT country_iso3, observation_year, metric FROM analytics.fact_gender_outcome
                   GROUP BY 1, 2, 3 HAVING count(*) != 1
               )""",
        )
        assert_zero(
            connection,
            "metric-to-unit definitions",
            """SELECT count(*) FROM analytics.fact_gender_outcome
               WHERE (metric = 'unadjusted_gender_pay_gap_pct' AND unit != 'PC')
                  OR (metric = 'gender_employment_gap_pp' AND unit != 'PC_PNT')""",
        )
        assert_zero(
            connection,
            "outcome ranges",
            "SELECT count(*) FROM analytics.fact_gender_outcome WHERE value < -100 OR value > 100",
        )
        assert_zero(
            connection,
            "policy country-year-indicator keys",
            """SELECT count(*) FROM (
                   SELECT country_iso3, observation_year, indicator FROM analytics.fact_policy_indicator
                   GROUP BY 1, 2, 3 HAVING count(*) != 1
               )""",
        )
        assert_zero(
            connection,
            "policy ranges",
            "SELECT count(*) FROM analytics.fact_policy_indicator WHERE value < 0 OR value > 100",
        )
        assert_zero(
            connection,
            "country-year mart grain",
            """SELECT count(*) FROM (
                   SELECT country_iso3, observation_year FROM analytics.mart_country_year
                   GROUP BY 1, 2 HAVING count(*) != 1
               )""",
        )
        assert_zero(
            connection,
            "cabinet date bounds",
            """SELECT count(*) FROM analytics.mart_cabinet_transition
               WHERE start_date >= coalesce(end_date_exclusive, date '9999-12-31')""",
        )
        connection.commit()
        return table_counts
    finally:
        connection.close()


def main() -> None:
    table_counts = build_warehouse()
    print(f"Built and validated {DATABASE_PATH.relative_to(ROOT)}")
    for table_name, row_count in table_counts.items():
        print(f"analytics.{table_name}: {row_count} rows")


if __name__ == "__main__":
    main()

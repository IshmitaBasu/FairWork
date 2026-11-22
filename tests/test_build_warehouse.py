"""End-to-end structural test using invented, committed warehouse inputs."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import duckdb

from src.analytics.build_warehouse import build_warehouse


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "warehouse"
FIXTURE_INPUTS = {
    "country": FIXTURE_DIR / "country.csv",
    "gender_outcome": FIXTURE_DIR / "gender_outcome.csv",
    "country_year": FIXTURE_DIR / "country_year.csv",
    "policy": FIXTURE_DIR / "policy.csv",
    "cabinet": FIXTURE_DIR / "cabinet.csv",
    "cabinet_party_membership": FIXTURE_DIR / "cabinet_party_membership.csv",
    "party_crosswalk": FIXTURE_DIR / "party_crosswalk.csv",
    "ches_position": FIXTURE_DIR / "ches_position.csv",
}


class WarehouseFixtureTests(unittest.TestCase):
    def test_builds_structural_marts_from_synthetic_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "fixture.duckdb"

            table_counts = build_warehouse(FIXTURE_INPUTS, database_path, expected_counts=None)

            self.assertEqual(1, table_counts["dim_country"])
            self.assertEqual(4, table_counts["fact_gender_outcome"])
            self.assertEqual(2, table_counts["mart_country_year"])
            self.assertEqual(2, table_counts["mart_cabinet_transition"])
            connection = duckdb.connect(str(database_path), read_only=True)
            try:
                transitions = connection.execute(
                    "SELECT transition_type FROM analytics.mart_cabinet_transition ORDER BY start_date"
                ).fetchall()
                policy_values = connection.execute(
                    "SELECT enrolment_0_2_registered_ecec_pct FROM analytics.mart_country_year "
                    "ORDER BY observation_year"
                ).fetchall()
            finally:
                connection.close()

        self.assertEqual([("first_observed_period",), ("cabinet_change",)], transitions)
        self.assertEqual([(45.0,), (None,)], policy_values)

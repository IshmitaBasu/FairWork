"""Tests for dashboard data transformations."""

from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from src.dashboard.data import exclude_flagged_observations, filter_years, metric_frame, required_paths


ROOT = Path(__file__).resolve().parents[1]


class DashboardDataTests(unittest.TestCase):
    def test_metric_frame_selects_metric_and_preserves_flag(self) -> None:
        source = pd.DataFrame(
            {
                "country_iso3": ["DEU"],
                "country_name": ["Germany"],
                "observation_year": [2020],
                "pay_gap_value": [19.2],
                "pay_gap_flag": ["b"],
                "employment_gap_value": [7.9],
                "employment_gap_flag": [""],
            }
        )

        actual = metric_frame(source, "Unadjusted gender pay gap (%)")

        self.assertEqual(["country_iso3", "country_name", "observation_year", "value", "observation_flag"], list(actual))
        self.assertEqual(19.2, actual.loc[0, "value"])
        self.assertEqual("b", actual.loc[0, "observation_flag"])

    def test_filter_years_is_inclusive(self) -> None:
        source = pd.DataFrame({"observation_year": [2019, 2020, 2021]})

        actual = filter_years(source, 2020, 2021)

        self.assertEqual([2020, 2021], actual.observation_year.tolist())

    def test_exclude_flagged_observations_keeps_blank_and_missing_flags(self) -> None:
        source = pd.DataFrame(
            {
                "observation_year": [2019, 2020, 2021],
                "observation_flag": ["b", "", None],
            }
        )

        actual = exclude_flagged_observations(source)

        self.assertEqual([2020, 2021], actual.observation_year.tolist())

    @unittest.skipUnless(all(path.exists() for path in required_paths().values()), "requires local curated dashboard files")
    def test_streamlit_app_renders_from_curated_data(self) -> None:
        from streamlit.testing.v1 import AppTest

        app = AppTest.from_file(str(ROOT / "app.py"))
        app.run(timeout=20)

        self.assertFalse(app.exception)
        self.assertEqual("FairWork", app.title[0].value)

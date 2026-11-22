"""Tests for descriptive summary helpers."""

from __future__ import annotations

import unittest

from src.analysis.run_descriptive_analysis import first_last_summary


class DescriptiveAnalysisTests(unittest.TestCase):
    def test_first_last_summary_keeps_actual_observation_window(self) -> None:
        rows = [
            {"country_iso3": "DEU", "observation_year": 2010, "value": 20.0, "flag": ""},
            {"country_iso3": "DEU", "observation_year": 2012, "value": 17.5, "flag": "b"},
            {"country_iso3": "ESP", "observation_year": 2010, "value": 25.0, "flag": ""},
            {"country_iso3": "ESP", "observation_year": 2012, "value": 24.0, "flag": ""},
        ]

        summary = first_last_summary(rows, "value", "flag", "Example measure")

        germany = next(row for row in summary if row["country_iso3"] == "DEU")
        self.assertEqual(2010, germany["first_year"])
        self.assertEqual(2012, germany["last_year"])
        self.assertEqual(-2.5, germany["net_change"])
        self.assertEqual(1, germany["flagged_observations"])

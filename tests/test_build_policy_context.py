"""Tests for the OECD PF3.2 policy-context transform."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from src.transforms.build_policy_context import INDICATOR, extract_policy_rows


class PolicyContextTests(unittest.TestCase):
    def test_extracts_supported_values_at_country_year_indicator_grain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "policy.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Enrolment_0-2-year-olds"
            sheet.append(["Metadata"])
            sheet.append(["Country", "Note", 2014, 2015, 2022, 2023])
            sheet.append(["Germany", None, 20.0, 30.0, 40.0, 50.0])
            sheet.append(["France", None, 20.0, "..", 55.0, 60.0])
            sheet.append(["Outside pilot", None, 20.0, 20.0, 20.0, 20.0])
            workbook.save(path)
            workbook.close()

            records = extract_policy_rows(path, {"Germany": "DEU", "France": "FRA"})

        self.assertEqual(3, len(records))
        self.assertEqual(
            [
                ("DEU", 2015, 30.0),
                ("DEU", 2022, 40.0),
                ("FRA", 2022, 55.0),
            ],
            [(row["country_iso3"], row["observation_year"], row["value"]) for row in records],
        )
        self.assertTrue(all(row["indicator"] == INDICATOR and row["unit"] == "PC" for row in records))

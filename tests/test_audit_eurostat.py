import unittest

from src.ingestion.audit_eurostat import coverage_rows


class CoverageRowsTests(unittest.TestCase):
    def test_groups_configurations_and_retains_status_flags(self) -> None:
        payload = {
            "id": ["freq", "wstatus", "geo", "time"],
            "dimension": {
                "freq": {"category": {"index": {"A": 0}}},
                "wstatus": {"category": {"index": {"EMP": 0, "EMP_PT": 1}}},
                "geo": {"category": {"index": {"DE": 0, "FR": 1}}},
                "time": {"category": {"index": {"2010": 0}}},
            },
            "value": {"0": 1.0, "1": 2.0, "2": 3.0, "3": 4.0},
            "status": {"2": "p", "3": "b"},
        }

        rows, observations = coverage_rows(payload, "sdg_05_30")

        self.assertEqual(observations, 4)
        self.assertEqual(
            rows,
            [
                {
                    "source_id": "eurostat_sdg_05_30",
                    "metric": "gender_employment_gap",
                    "country_iso2": "DE",
                    "country_name": "Germany",
                    "observation_year": 2010,
                    "observed_configurations": 2,
                    "flagged_configurations": 1,
                    "observation_flags": "p",
                },
                {
                    "source_id": "eurostat_sdg_05_30",
                    "metric": "gender_employment_gap",
                    "country_iso2": "FR",
                    "country_name": "France",
                    "observation_year": 2010,
                    "observed_configurations": 2,
                    "flagged_configurations": 1,
                    "observation_flags": "b",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()

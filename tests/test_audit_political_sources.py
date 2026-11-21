import io
import unittest
import zipfile

from src.ingestion.audit_political_sources import audit_ches, audit_parlgov


class PoliticalSourceAuditTests(unittest.TestCase):
    def test_ches_uses_trend_country_codes_and_excludes_2024(self) -> None:
        body = b"year,country,party_id,party\n2010,3,1,Party A\n2014,5,2,Party B\n2019,16,3,Party C\n2024,14,4,Party D\n"

        rows, metadata = audit_ches(body)

        self.assertEqual(metadata["country_column"], "country")
        self.assertEqual(
            [(row["country_name"], row["survey_wave"]) for row in rows],
            [("Germany", 2010), ("Spain", 2014), ("Sweden", 2019)],
        )

    def test_parlgov_counts_cabinet_periods_not_cabinet_party_rows(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("country.csv", "id,name\n1,Germany\n2,Spain\n")
            archive.writestr(
                "cabinet.csv",
                "id,country_id,start_date\n10,1,2009-05-01\n11,1,2011-01-01\n12,1,2024-01-01\n20,2,2015-06-01\n",
            )

        rows, metadata = audit_parlgov(buffer.getvalue())
        counts = {row["country_name"]: row["overlapping_cabinet_periods"] for row in rows}

        self.assertEqual(metadata["cabinet_file"], "cabinet.csv")
        self.assertEqual(counts, {"Germany": 2, "Spain": 1, "France": 0, "Sweden": 0})


if __name__ == "__main__":
    unittest.main()

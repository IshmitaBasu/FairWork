# Phase 3 harmonization and political-join result

**Status:** Complete for the approved MVP scope.

## Outputs

| Output | Grain | Validation result |
|---|---|---|
| `data/metadata/country_crosswalk.csv` | One canonical pilot country | Four countries mapped across Eurostat, CHES and ParlGov identifiers. |
| `data/processed/harmonized/fact_gender_outcome.csv` | Country × year × metric | 104 facts: 4 countries × 13 years (2010–2022) × 2 approved metrics. |
| `data/processed/harmonized/country_year_outcomes.csv` | Country × year | 52 rows with separate values and observation flags. |
| `data/processed/political_context/cabinet_periods.csv` | One dated cabinet period | 34 periods; each uses a half-open `[start, next start)` interval. |
| `data/processed/political_context/party_crosswalk_review.csv` | Country × cabinet-party identity | 26 unique cabinet parties: 19 accepted links and 7 quarantined rows. |

## Country and cabinet rules

- Country keys use ISO3 (`DEU`, `ESP`, `FRA`, `SWE`) internally while retaining source keys in the canonical crosswalk.
- The current CHES trend-file code for France is `6`; it is not the legacy country-level `chess` value in ParlGov. This was checked against the party identifiers in the downloaded CHES source.
- Cabinet periods are not collapsed into annual assignments. The end is represented as the next cabinet's start date, exclusive.

## Party matching decision

Only direct ParlGov `chess` identifiers that occur in a pilot-country CHES wave are accepted automatically. One reviewed France continuity match links ParlGov's `REM|R` (La République En Marche / Renaissance) to CHES 2019 `LREM` party ID `626`; its rationale is versioned in `data/metadata/party_crosswalk_overrides.csv`.

Seven parties remain quarantined because a defensible CHES party-wave observation was not established: Spanish `ECP`, `EM|GCE`, `UP`, and French `agir`, `H`, `NC`, `PE`. They will be displayed as unmatched or omitted from party-position aggregation, never mapped by name similarity.

## Reproducible build

```powershell
python -m src.transforms.build_political_context
python -m src.transforms.build_outcome_panel
python -m unittest discover -s tests -v
```

The transformation scripts validate the expected approved outcome count and retain the original Eurostat status flags. Phase 4 can now build staged and mart models from these harmonized outputs.

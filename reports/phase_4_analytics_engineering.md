# Phase 4 analytics engineering

**Status:** Complete for the approved MVP scope.  
**Build date:** 21 November 2026

## Delivered assets

- `src/transforms/build_policy_context.py` standardizes OECD Family Database PF3.2 enrolment for ages 0–2, 2015–2022.
- `src/analytics/build_warehouse.py` creates and validates the ignored local DuckDB database at `data/processed/fairwork.duckdb`.
- `src/analytics/export_curated_data.py` produces ignored, read-only Parquet outputs in `data/published/`.
- `src/transforms/build_party_positions.py` derives local CHES party-wave facts only for accepted ParlGov-to-CHES mappings.
- `dbt_project.yml`, `dbt/profiles.yml`, `dbt/models/` and `dbt/tests/` provide a matching dbt implementation for a standard dbt environment.

## Analytical grains and outputs

| Asset | Grain | Validated count | Rule |
|---|---:|---:|---|
| `analytics.fact_gender_outcome` | country, year, metric | 104 | Eurostat flags retained. |
| `analytics.fact_policy_indicator` | country, year, indicator | 32 | OECD PF3.2, ages 0–2, 2015–2022 only. |
| `analytics.fact_ches_party_position` | country, CHES wave, party | 54 | Original 2010, 2014 and 2019 survey-wave positions; accepted crosswalks only. |
| `analytics.bridge_cabinet_party_membership` | dated cabinet period, party | 83 | ParlGov cabinet membership with accepted/review-needed crosswalk status retained. |
| `analytics.mart_country_year` | country, year | 52 | Outcomes and policy context only; no cabinet join. |
| `analytics.mart_cabinet_transition` | country, dated cabinet period | 34 | Half-open periods; no annualisation. |

The local exports are `mart_country_year.parquet` (52 rows), `mart_cabinet_transition.parquet` (34 rows), `fact_policy_indicator.parquet` (32 rows), `fact_ches_party_position.parquet` (54 rows) and `bridge_cabinet_party_membership.parquet` (83 rows). They are ignored and must not be published without a source-term review.

## Validation

The executable DuckDB build rejects unexpected counts, duplicate keys, invalid metric-unit pairings, values outside plausible percentage/percentage-point bounds, invalid cabinet dates and duplicate country-year mart rows. It also retains the project rule that a yearly outcome is not duplicated across cabinets when a government changes during that year.

Run the reproducible local build from the repository root:

```powershell
python -m src.transforms.build_policy_context
python -m src.analytics.build_warehouse
python -m src.analytics.export_curated_data
python -m unittest discover -s tests -v
```

## dbt compatibility note

The checked-in dbt project contains corresponding staging models, marts, schema tests and custom SQL tests. On this Windows environment, installing the latest dbt packages was blocked by an upstream certificate error while its installer fetched `dbt-core-experimental-parser` from GitHub. The tested Python/DuckDB build is therefore the required local execution path; no source, model or export depends on an untested dbt invocation. In a normal dbt environment, use:

```powershell
dbt build --project-dir . --profiles-dir dbt
```

No cloud storage integration was added because it is explicitly optional and the local curated exports meet the MVP requirement.

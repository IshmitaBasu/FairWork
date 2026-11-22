# Project tracking

The GitHub repository is connected. A hosted project board is optional and has not been created.

| Phase | Status | Evidence | Next work |
|---|---|---|---|
| 1. Scope and foundation | Complete | Planning documents, project structure and Git setup | — |
| 2. Source audit and scope | Complete | `reports/phase_2_scope_decision.md` | — |
| 3. Harmonization and political joins | Complete | `reports/phase_3_harmonization.md` | — |
| 4. Analytics engineering | Complete | `reports/phase_4_analytics_engineering.md` | — |
| 5. Research | Complete | `reports/phase_5_descriptive_results.md` | — |
| 6. Dashboard | Complete locally | `reports/phase_6_dashboard.md` | — |
| 7. Quality and automation | In progress | `.github/workflows/ci.yml`, `tests/fixtures/warehouse/` | Add source-monitoring design |
| 8. Release | In preparation | Detailed case study, evaluation and screenshot guide | Complete manual checks and data-terms gate before publishing |

## Current data decisions

- Countries: Germany, France, Spain and Sweden.
- Core outcome and political context: 2010–2022.
- Comparative policy-context panel: OECD PF3.2, 2015–2022.
- CHES party-position waves: 2010, 2014 and 2019 only.
- EIGE is excluded from the MVP because of its 2025 methodology reset.
- The party crosswalk accepts 19 links and quarantines 7 unsupported links.

## Phase 4 delivered

- Built the ignored local `data/processed/fairwork.duckdb` database and staged the approved country, outcome, policy, cabinet and party-crosswalk inputs.
- Built a 52-row `mart_country_year` and a separate 34-row `mart_cabinet_transition`; cabinet periods were never annualised or joined into the country-year mart.
- Added unique-key, metric-unit, range, date-bound and country-relationship checks to the executable warehouse build, plus matching dbt SQL tests.
- Exported local Parquet snapshots for the country-year mart, cabinet-transition mart and policy fact table.

## Phase 5 delivered

- Generated reproducible outcome, policy-context and cabinet-period figures from the validated marts.
- Documented 52 country-year rows, 32 policy observations, 34 cabinet periods, source flags and flag-exclusion sensitivity results.
- Kept outcomes, party survey positions, cabinet timing and policy indicators conceptually separate; no causal model or party ranking was produced.

## Phase 6 delivered

- Built a local Streamlit dashboard from curated Parquet outputs, not raw source snapshots.
- Added country/year/metric controls, cabinet context, policy context, comparison, data download and methods views.
- Displayed source definitions, flags, coverage and descriptive-only caveats alongside charts.

## Phase 7 progress

- GitHub Actions runs syntax, unit tests and a fixture-based DuckDB warehouse build on pull requests and `main` without accessing ignored data snapshots.
- Committed Testland fixture records are invented structural data, not source extracts or derivatives; they verify cabinet transitions and the policy left join end to end.
- Raw source snapshots remain excluded from CI until their terms permit a compliant retrieval strategy.
- Next: design a permitted upstream source-monitoring workflow.

## Phase 8 preparation

- Added a detailed case study with outcome, policy-context and cabinet-timeline visuals, an image archive and an evidence-based release evaluation.
- Public dashboard deployment and public data screenshots remain blocked pending the source-terms and hosted-data checks.
- Remaining release work: manual UI and source reconciliation checks, followed by a decision on a licensed hosted-data strategy.

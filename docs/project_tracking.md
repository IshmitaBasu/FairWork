# Project tracking

The GitHub repository is connected. A hosted project board is optional and has not been created.

| Phase | Status | Evidence | Next work |
|---|---|---|---|
| 1. Scope and foundation | Complete | Planning documents, project structure and Git setup | — |
| 2. Source audit and scope | Complete | `reports/phase_2_scope_decision.md` | — |
| 3. Harmonization and political joins | Complete | `reports/phase_3_harmonization.md` | — |
| 4. Analytics engineering | Complete | `reports/phase_4_analytics_engineering.md` | — |
| 5. Research | Next | None yet | Descriptive analysis and sensitivity checks |
| 6. Dashboard | Not started | — | Local Streamlit explorer |
| 7. Quality and automation | Not started | — | CI and reproducible checks |
| 8. Release | Not started | — | Demo, documentation and portfolio case study |

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

## Phase 5 entry conditions

- Use the curated outputs for descriptive exploration only.
- Keep outcomes, party survey positions, cabinet timing and policy indicators conceptually separate.
- Document missingness, flags and the limited four-country sample in every analytical output.

# Project tracking

The GitHub repository is connected. A hosted project board is optional and has not been created.

| Phase | Status | Evidence | Next work |
|---|---|---|---|
| 1. Scope and foundation | Complete | Planning documents, project structure and Git setup | — |
| 2. Source audit and scope | Complete | `reports/phase_2_scope_decision.md` | — |
| 3. Harmonization and political joins | Complete | `reports/phase_3_harmonization.md` | — |
| 4. Analytics engineering | Next | None yet | DuckDB staging, marts, tests and curated exports |
| 5. Research | Not started | — | Descriptive analysis and sensitivity checks |
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

## Phase 4 entry conditions

- Build a local DuckDB database from the harmonized facts and cabinet-period data.
- Keep cabinet periods separate from annual outcomes.
- Add unique-key, accepted-value, range and referential-integrity checks.
- Materialize country-year and cabinet-transition marts, then export curated files.

# FairWork

FairWork is a reproducible exploratory data project about governing coalitions, selected policy context and women's economic outcomes in Europe. It will present documented associations without treating them as causal effects or ranking parties or ideologies.

## Current status

**Phase 5 descriptive research is complete; Phase 6 dashboard work is next.** The approved pilot is Germany, France, Spain and Sweden. Core outcomes and political context cover 2010–2022; the comparative OECD policy-context panel covers 2015–2022. No causal statistical analysis or public dashboard has been published.

Phase 3 produced a 52-row country-year outcome panel, 34 dated cabinet periods, and a reviewed party crosswalk with 19 accepted links. Seven unsupported party links remain quarantined. Phase 4 adds 32 OECD policy facts, a validated local DuckDB warehouse and curated Parquet exports. Phase 5 adds reproducible descriptive figures, coverage summaries and flag-sensitivity checks.

## Planned MVP

- Explore unadjusted gender pay gaps and gender employment gaps from Eurostat.
- Show documented cabinet periods from ParlGov alongside outcome observations.
- Present CHES party positions only with their original survey wave and scale.
- Add a policy panel only where definitions and country-year coverage support a fair comparison.
- Provide source citations, data-quality context and reproducible transformation steps.

## Principles

- Missing observations stay missing.
- Party positions, governing participation, enacted policy and observed outcomes are distinct concepts.
- Trends and models are descriptive unless a separately justified causal design is added later.
- Every displayed value must retain source, version, definition, unit and applicable flags.

## Project map

- [Roadmap](Project%20Roadmap.md) — phases, delivery criteria, risks and planned stack.
- [Requirements](docs/requirements.md) — MVP user and release requirements.
- [Architecture](docs/architecture.md) — local Python, DuckDB, dbt and Streamlit design.
- [Methodology](docs/methodology_plan.md) — source and inference safeguards.
- [Project tracking](docs/project_tracking.md) — current status and next actions.
- [Phase 2 scope decision](reports/phase_2_scope_decision.md) — approved data scope and exclusions.
- [Phase 3 harmonization report](reports/phase_3_harmonization.md) — panel, cabinet-period and party-crosswalk results.
- [Phase 4 analytics-engineering report](reports/phase_4_analytics_engineering.md) — warehouse grain, validation and exports.
- [Phase 5 descriptive results](reports/phase_5_descriptive_results.md) — trends, cabinet context, sensitivity checks and limits.

## Next step

Start Phase 6: build the local Streamlit dashboard around the curated marts and Phase 5 descriptive outputs; retain flags, source context and non-causal interpretation notices.

## Intended local setup

The implementation environment is declared in `pyproject.toml`; the `audit` extra includes `openpyxl` and the `pipeline` extra includes DuckDB. Raw source snapshots and credentials remain outside version control.

## Rebuild the local analytics assets

After completing the source and Phase 3 transforms, run:

```powershell
python -m src.transforms.build_policy_context
python -m src.analytics.build_warehouse
python -m src.analytics.export_curated_data
```

This creates ignored local files: `data/processed/fairwork.duckdb` and three Parquet exports in `data/published/`. The checked-in dbt project mirrors the same staging and mart grains; its setup is documented in the Phase 4 report.

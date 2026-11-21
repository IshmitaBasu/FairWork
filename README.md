# FairWork

FairWork is a reproducible exploratory data project about governing coalitions, selected policy context and women's economic outcomes in Europe. It will present documented associations without treating them as causal effects or ranking parties or ideologies.

## Current status

**Phase 1 complete locally; Phase 2 is in progress.** The proposed pilot is Germany, France, Spain and Sweden from 2010–2023, pending a complete source-coverage and licensing audit. Initial Eurostat snapshots have been audited locally; no analysis has been performed or published.

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

## Next step

Complete the Phase 2 source-overlap audit: record source terms and versions, profile CHES and ParlGov identifiers and coverage, and build the full country × year × source × metric availability matrix before finalising the pilot scope.

## Intended local setup

The implementation environment will be pinned in `pyproject.toml` as the data pipeline begins. Until then, this repository deliberately contains no unverified source data or credentials.

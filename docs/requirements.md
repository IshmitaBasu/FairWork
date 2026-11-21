# FairWork MVP requirements

**Status:** Updated after Phase 4, 21 November 2026. The approved core scope is 2010–2022; redistribution conditions remain enforced.

## Purpose and scope

FairWork will let students, researchers, journalists and interested members of the public explore documented political and policy context alongside women's economic outcomes. It will explain measurement and limitations without ranking parties or implying that political context caused an observed change.

The approved pilot is Germany, France, Spain and Sweden for 2010–2022. The policy-context comparison panel is limited to 2015–2022. The minimum useful release needs at least one adequately documented outcome and cabinet timeline for each retained country; it must show gaps rather than fill them with invented observations.

## User requirements

1. Select a country, outcome and available years; see a trend with units, population, source and missingness.
2. See factual cabinet transition markers and inspect cabinet membership and source dates.
3. Inspect party positions on their original CHES scale and survey wave, with unmatched parties identified.
4. Compare available countries using the same metric definition and display coverage limitations.
5. Explore a policy indicator only if its definition and country-year coverage support comparison.
6. Read a concise evidence summary, methodology, source citations and limitations; export a chart or its underlying displayed data with context.
7. Find a documented path to reproduce the published results from source snapshots and transformations.

## Quality and release requirements

- Each displayed value must be traceable to a source, version, observation year, definition and applicable flags. Missing data remain missing.
- Country-year and political joins must be audited for duplicate multiplication and unresolved mappings. Cabinet changes within a year must remain visible.
- Charts must label pay gap as unadjusted and employment gap in percentage points; show uncertainty where available and avoid causal or partisan claims.
- Empty selections and unavailable data must produce understandable messages. The interface must be usable on a typical laptop and a narrow mobile screen.
- The executable Python/DuckDB checks must pass; the matching dbt checks must also pass before any public release. A clean environment must be able to reproduce the published data and app. Source licences and redistribution permissions must be checked before publication.
- The portfolio release will include a public Streamlit Community Cloud demo, subject to its available resources, plus setup instructions and methods. Local execution is the fallback during development.

## Out of scope

Electoral recommendations, party rankings, individual discrimination estimates, personal political profiles, unsupported causal claims, automatic extension of ParlGov beyond its verified release, and incompatible historical index splicing are excluded. Formal causal evaluation and a separate static frontend are post-MVP ideas.

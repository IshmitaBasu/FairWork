# Phase 2 source and coverage decision

**Decision date:** 21 November 2026
**Status:** Complete for MVP scoping; publication conditions remain enforced.

## Approved MVP scope

| Component | Approved scope | Why |
|---|---|---|
| Countries | Germany, Spain, France and Sweden | Each has the required Eurostat outcome coverage, CHES waves and ParlGov cabinet-period coverage. |
| Core outcome and political window | 2010–2022 | Eurostat outcomes are available through 2023, but the available ParlGov development release is dated 4 November 2023 and the later stable release only covers cabinets through June 2023. A complete 2023 political timeline is therefore not accepted without primary-source validation. |
| Party-position context | CHES waves 2010, 2014 and 2019 | The trend file contains all four countries in those waves. These remain wave-specific measurements, never annual imputations. |
| Policy-context panel | OECD PF3.2, registered ECEC enrolment of children aged 0–2, 2015–2022 | All four countries share annual observations from 2015–2022. The common 2010 observation is retained in source data but excluded from comparative trend analysis because it is separated from the later run. |
| EIGE Index | Excluded from the MVP | EIGE revised the Index methodology in 2025, so it is not admitted to the historical panel without a documented comparable bridge. |

## Metric decisions

- **Pay gap:** retain Eurostat `sdg_05_20`, annual percentage (`PC`), economic activity `B-S_X_O`.
- **Employment gap:** retain Eurostat `sdg_05_30`, annual percentage points (`PC_PNT`), age `Y20-64`, `wstatus=EMP`. Other returned work-status configurations are not substitutes for the headline employment gap.
- **Flags:** retain the raw Eurostat status codes. In published outputs, `b` means a break in series, `d` a differing definition and `p` a provisional value; flags accompany rather than alter an observation.

## Source and reuse handling

Eurostat permits reuse of its statistical data and metadata with source acknowledgement. CHES, ParlGov and OECD raw files and their codebooks are kept out of Git and public app artifacts pending confirmation of their precise redistribution terms. The project may document reproducible retrieval and use locally generated aggregates only after each transformation and source condition is reviewed.

Downloaded local snapshots and their SHA-256 hashes are recorded in `data/metadata/source_manifest.yml`; the raw files are intentionally ignored by Git.

## Cross-source overlap

| Requirement | Available period | Scope decision |
|---|---|---|
| Eurostat pay and employment outcomes | 2010–2023, all pilot countries | Retain 2010–2022 for integration with political context |
| ParlGov cabinet periods | Covers pilot window, but current releases do not establish a complete 2023 timeline | Cap political comparisons at 2022 |
| CHES party positions | 2010, 2014, 2019 | Display by wave only |
| OECD PF3.2 age 0–2 | Common: 2010 and 2015–2023 | Use 2015–2022 comparative policy panel |

## Phase 3 entry conditions

1. Build ISO country mappings and preserve original source identifiers.
2. Convert ParlGov cabinet rows into dated cabinet periods; do not assign a single cabinet to a year without an explicit rule.
3. Create and manually review the CHES-to-ParlGov party crosswalk. Unmatched and ambiguous parties must remain visible.
4. Build fact tables and tests for the approved metrics, flags and approved time windows.

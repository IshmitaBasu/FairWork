# Source coverage audit — initial Eurostat result

**Audit date:** 21 November 2026  
**Scope:** Germany (DE), Spain (ES), France (FR) and Sweden (SE), 2010–2023

This is an initial evidence gate, not a final admission decision. Raw snapshots are retained locally and excluded from version control pending source-licence and redistribution review. The reproducible command is:

```powershell
python -m src.ingestion.audit_eurostat
```

## Result

Both planned Eurostat outcome datasets contain an observation for every proposed country-year in the requested window: 4 countries × 14 years = **56 country-year records** per metric.

| Source | Metric | Returned configuration(s) | Requested-scope observations | Country-year availability | Decision |
|---|---|---|---:|---:|---|
| `sdg_05_20` | Unadjusted gender pay gap | `freq=A`; `unit=PC`; `nace_r2=B-S_X_O` | 56 | 56/56 | Eligible for definition and flag review |
| `sdg_05_30` | Gender employment gap | `freq=A`; `age=Y20-64`; `unit=PC_PNT`; `wstatus=EMP, EMP_PT, EMP_TEMP, UEMP_PT` | 224 | 56/56 | Final work-status filter must be selected and documented |

The raw response includes observation-status codes. The audit artifact retains the codes by country-year and configuration; it does not interpret them. This prevents provisional values, breaks and definition changes from being silently lost.

## Political-context coverage

The downloaded CHES 1999–2024 trend file contains each pilot country in the three waves that fall within the proposed 2010–2023 window: **2010, 2014 and 2019**. These are survey waves, not annual observations. The audit found 6–14 party records per country-wave; party identifiers remain unlinked to ParlGov until the codebooks and a reviewed crosswalk are complete.

The downloaded ParlGov development release contains cabinet periods overlapping the proposed window for every pilot country. Coverage-only counts are 5 periods for Germany, 8 for Spain, 13 for France and 8 for Sweden. Period ends are inferred from the subsequent recorded cabinet start for this audit; they are not yet validated transition dates. ParlGov's release date limits it to the development version dated 4 November 2023.

## Provenance

| Source | Retrieval time (UTC) | SHA-256 |
|---|---|---|
| `sdg_05_20` | 2026-11-21 14:35:24 | `0e7f38c4eae5eaf3d0c5522b4030f0c4f57fa22fac813e776f5c24ededf7e23c` |
| `sdg_05_30` | 2026-11-21 14:35:25 | `2a2df029fb637b1bef7fda5464541e0e6713a02b7ce5b8d05146d12535c2239e` |

## Remaining gate conditions

- Inspect Eurostat metadata and confirm status-flag meanings, release/version information, licensing and redistribution terms.
- Review the downloaded CHES and ParlGov codebooks; verify country-code mappings, party identifiers, cabinet end dates, original scales and reuse terms.
- Select a single OECD policy indicator only after its definition and country-year overlap are established; assess EIGE separately because of methodology comparability.

**Pilot conclusion:** the planned four-country, 2010–2023 scope remains provisional. Eurostat outcome coverage does not itself establish political or policy-data overlap.

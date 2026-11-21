# Project tracking

This is a local planning board. The GitHub repository is connected; a hosted project board has not been created.

## Current delivery status — 21 November 2026

- [x] Phase 1 — local repository foundation and planning artefacts.
- [x] Phase 2 — source audit and MVP scope decision; see `reports/phase_2_scope_decision.md`.
- [x] Phase 3 — country harmonization, cabinet periods and reviewed party crosswalk; see `reports/phase_3_harmonization.md`.
- [ ] Phase 4 — analytics engineering and tested curated marts.

| Milestone | Status | Next evidence |
|---|---|---|
| Week 1: scope and design | Local repository and planning documents ready | Create a hosted repository/project board when an account and remote are selected. |
| Week 2: ingestion and coverage | In progress — initial Eurostat audit complete | Profile CHES and ParlGov releases; complete licence review and the cross-source coverage matrix. |
| Week 3: harmonization | Not started | Reviewed party crosswalk, cabinet periods and join audit. |
| Week 4: analytics engineering | Not started | Tested dbt marts and curated exports. |
| Week 5: research | Not started | Descriptive analysis, sensitivity checks and limitations. |
| Week 6: dashboard | Not started | Working local explorer with source and missingness context. |
| Week 7: quality and automation | Not started | Reproducible checks and CI configuration. |
| Week 8: release | Not started | Public demo, verified claims and portfolio documentation. |

## Week 2 starting tasks

- Inspect Eurostat dimensions and download outcome observations and metadata.
- Inspect CHES and ParlGov releases, identifiers, codebooks and reuse terms.
- Evaluate candidate OECD measures and EIGE methodology and reuse terms.
- Record versions, hashes, provenance, flags and failed retrievals.
- Create a coverage matrix and recommend any scope reduction before analysis.

## Week 2 progress — 21 November 2026

- [x] Retrieved local Eurostat snapshots for `sdg_05_20` and `sdg_05_30` and recorded SHA-256 hashes.
- [x] Confirmed country-year availability for all four proposed countries across 2010–2023, without selecting a final employment work-status configuration.
- [x] Added a reproducible audit command and a tracked summary in `reports/source_coverage.md`.
- [x] Retrieved and schema-profiled the CHES trend file and ParlGov development archive; recorded local snapshot hashes and initial pilot coverage.
- [ ] Confirm Eurostat licence, release/version metadata and flag meanings.
- [ ] Review CHES and ParlGov codebooks, licences and redistribution terms; build a reviewed party crosswalk.
- [ ] Complete the cross-source country-year availability matrix and recommend final pilot scope.

## Phase 1 completion record

- [x] Scope, requirements, architecture, metric dictionary and methodology drafted.
- [x] Local Git repository, README, ignore rules and implementation skeleton created.
- [x] Empty data directories and a source-manifest template created; no source observations have been retrieved.
- [ ] Create and connect a hosted Git repository and project board (requires a chosen remote/account).

## Open decisions

- Final countries and years depend on verified overlap and source comparability.
- Select policy measures and any model controls only after source inspection.
- Finalize the CHES-to-cabinet temporal matching convention after reviewing wave coverage.
- Confirm which snapshots and curated data may be redistributed and how the app will access them.

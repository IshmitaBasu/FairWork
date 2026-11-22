# Methodology plan

## Source and coverage gate

**Completed through descriptive research on 22 November 2026.** The approved scope and exclusions are in `reports/phase_2_scope_decision.md`; the harmonized output and party-link quarantine are in `reports/phase_3_harmonization.md`; tested grains and exports are in `reports/phase_4_analytics_engineering.md`; descriptive outputs and limitations are in `reports/phase_5_descriptive_results.md`.

In Week 2, inventory source release, download location, retrieval date, licence, redistribution conditions, dimensions, units, flags and country-year coverage. Construct a country × year × source × metric availability matrix before choosing the final pilot. Confirm the Eurostat age, economic activity and other dimensions from the actual files. Verify ParlGov cabinet end dates and CHES party identifiers against downloaded codebooks. Document reasons for exclusions and revisions; no values or coverage are assumed confirmed yet.

## Data preparation

1. Preserve source snapshots where permitted, with hashes and a manifest; otherwise document reproducible retrieval and version information.
2. Standardize country identifiers and retain original identifiers, time, units, source dimensions and observation flags. Never replace missing values with zero.
3. Retain cabinets as dated periods and their parties as separate bridge records. Review a versioned ParlGov-to-CHES crosswalk; quarantine uncertain matches.
4. Preserve CHES survey waves and original scales. Any rule linking a wave to a cabinet must specify direction, maximum age and missingness; do not present interpolated values as observed. Finalize the rule after inspecting coverage.
5. Build analysis marts with explicit grains and tests for keys, referential integrity, ranges and unexpected join multiplication. The implemented country-year and cabinet-transition marts retain multiple cabinet periods separately from annual outcomes.

## Analysis and reporting

Coverage is described before trends. The Phase 5 baseline uses consistent definitions, retains flags, plots each country's own transition dates against annual observations and avoids attributing a yearly outcome to a single cabinet. It reports flag-exclusion sensitivity as a transparency check, not a causal robustness result.

For policy comparisons, select only indicators with documented, comparable definitions and enough observations; otherwise omit the panel and explain why. If an exploratory model is feasible, document specification, controls, sample, missing-data handling, uncertainty and sensitivity to choices before interpreting it. Country and year effects cannot resolve all confounding. With few countries, avoid confident inferential claims and fall back to descriptive analysis when uncertainty cannot be estimated defensibly.

Every chart or summary will include the period, source, definition and applicable caveats. Report null or ambiguous findings and unresolved mappings. A later causal study would need its own treatment definition, credible comparison, implementation dates and identification assumptions; it is not an MVP deliverable.

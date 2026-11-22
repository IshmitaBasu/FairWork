# Research questions and scope

**Pilot:** Germany, France, Spain and Sweden. Core outcome/political context covers 2010–2022; the OECD policy-context panel covers 2015–2022. Observations are aggregate and primarily country-year; cabinet periods and CHES waves retain their own dates.

## Questions

1. How do unadjusted gender pay gaps and gender employment gaps change within and across pilot countries over the available period?
2. What outcome trends surround documented cabinet transitions, and what party membership and expert-assessed positions are recorded for those cabinets?
3. Where comparable observations exist, how do selected childcare or parental-leave measures vary alongside employment gaps?
4. How do missing observations, unmatched parties, changes in definitions and alternative time windows affect what can be described?

## Predefined exploratory analyses

| Analysis | Unit and comparison | Interpretation and feasibility gate |
|---|---|---|
| Outcome trends | Country × year, separately for each metric | Plot observed values and flags; compare only consistent populations and units. No causal attribution. |
| Cabinet transitions | Cabinet start date, with observed annual outcomes before and after | Show actual timing and available observations; multiple changes in a year remain visible. Descriptive only; do not assume an immediate effect. |
| Policy and employment | Country × year for an eligible policy indicator and employment gap | Show coverage and definitions first; descriptive scatter or trends only if country-year matches are meaningful. |
| Political context | Cabinet-party records joined to CHES party-wave observations | Show original survey year and scale, reviewed match status and missingness. Do not fabricate annual party scores. |

## Implemented descriptive baseline

Phase 5 implements the first three feasible descriptive views: outcome trends with country-specific cabinet markers, OECD PF3.2 policy-context trends, and a dated cabinet-period timeline. It also publishes coverage and flag-exclusion sensitivity tables. The local dashboard adds a separate interactive CHES `lrgen` spectrum, keeping original 2010, 2014 and 2019 survey waves separate. A panel model was deliberately not fitted: four countries and unmeasured confounding do not support a credible causal interpretation. See `reports/phase_5_descriptive_results.md`.

Controls to consider for an exploratory panel model are country and year effects and, where defensible and available, GDP per capita, unemployment and relevant demographic composition. Define their sources, units, coverage, timing and rationale before use; report sample size and missingness. With only four tentative countries and limited years, model complexity, standard errors and inference may be unreliable. If data or sample size are inadequate, publish descriptive results instead.

## Neutrality and inference

CHES expert assessments describe parties, not FairWork endorsements; cabinet membership is not evidence of enacted policy. Governments may inherit trends and face confounders. Changes before or after a transition, correlations and regression coefficients do not establish causal effects. No party or ideology will be scored as better for women, and aggregate gaps cannot identify individual discrimination.

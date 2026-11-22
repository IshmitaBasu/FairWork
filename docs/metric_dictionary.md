# Initial measurement dictionary

These definitions reflect the approved Phase 2/3 MVP scope. Source snapshots, hashes, configurations and publication conditions are recorded in `data/metadata/source_manifest.yml`.

| Measure | Planned source | Grain / unit | Definition and cautions |
|---|---|---|---|
| Unadjusted gender pay gap | Eurostat `sdg_05_20` | Country × year; percent | Approved configuration: annual, `PC`, `B-S_X_O`, 2010–2022. Unadjusted; not a measure of equal pay for equal work. Preserve flags. |
| Gender employment gap | Eurostat `sdg_05_30` | Country × year; percentage points | Approved configuration: annual, age `Y20-64`, `wstatus=EMP`, `PC_PNT`, 2010–2022. Percentage points are not percent change. Preserve flags. |
| Cabinet | ParlGov | Country × dated cabinet period | Government start and end dates and membership as recorded by the source. Multiple cabinets can occur in one year; verify coverage and treatment of ongoing terms. |
| Party position | CHES-Europe trend file | Country × party × survey wave × question; original scale | The local dashboard visualizes approved-party `lrgen` on its original 0 (left) to 10 (right) general left-right scale at 2010, 2014 or 2019 survey waves. It is not an annual observation, enacted policy or party ranking. |
| Family policy indicator | OECD PF3.2 | Country × observation year; percent | Registered ECEC enrolment for children aged 0–2; implemented as `enrolment_0_2_registered_ecec_pct`, comparative panel limited to 2015–2022. Context only, not an intervention. |
| Gender Equality Index | EIGE | — | Excluded from the MVP because the 2025 methodology reset is not treated as a comparable historical bridge. |

For every admitted metric record the source title, URL, release/version, retrieval date, original code, population, dimensions, units, flags, missingness, transformation and licence. Store both observation year and release date where available. Do not silently convert unavailable observations to zero.

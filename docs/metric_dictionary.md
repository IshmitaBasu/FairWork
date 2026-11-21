# Initial measurement dictionary

These are planning definitions, not verified extracts. The source-specific codebook, population, available dimensions, flags and licences must be checked in Week 2 and recorded in the source manifest.

| Measure | Planned source | Grain / unit | Definition and cautions |
|---|---|---|---|
| Unadjusted gender pay gap | Eurostat `sdg_05_20` | Country × year × selected dimensions; percent | Difference between average gross hourly earnings of male and female paid employees as a percentage of male earnings. Unadjusted; not a measure of equal pay for equal work. Confirm coverage and flags. |
| Gender employment gap | Eurostat `sdg_05_30` | Country × year × selected dimensions; percentage points | Difference between men's and women's employment rates. Confirm the age group and other dimensions in the extract; percentage points are not percent change. |
| Cabinet | ParlGov | Country × dated cabinet period | Government start and end dates and membership as recorded by the source. Multiple cabinets can occur in one year; verify coverage and treatment of ongoing terms. |
| Party position | CHES-Europe trend file | Country × party × survey wave × question; original scale | Expert assessment for a specific wave and dimension. Retain question, scale direction, uncertainty if supplied and wave year; not an annual observation or enacted policy. |
| Family policy indicator | OECD Family Database, measure to be selected | Country × observation year × measure; source unit | Candidate childcare or parental-leave measure. Eligibility, generosity, timing and comparability must be checked before selection. |
| Gender Equality Index | EIGE, optional | Country × release/observation year × dimension; source scale | Context only if usable; do not merge incompatible historical and revised methodology series without a valid official bridge. |

For every admitted metric record the source title, URL, release/version, retrieval date, original code, population, dimensions, units, flags, missingness, transformation and licence. Store both observation year and release date where available. Do not silently convert unavailable observations to zero.

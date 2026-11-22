# Political-context transformation

From the repository root, build the Phase 3 political-context intermediates:

```powershell
python -m src.transforms.build_political_context
```

The command creates ignored local files in `data/processed/political_context/`:

- `cabinet_periods.csv`: dated, half-open cabinet periods.
- `party_crosswalk_review.csv`: only direct ParlGov `chess` identifier links are accepted automatically; every missing or unavailable link is a manual-review item.
- `cabinet_party_membership.csv`: parties recorded in each dated cabinet period, retaining mapping status and review action.

Reviewed continuity overrides are stored separately in `data/metadata/party_crosswalk_overrides.csv`; they require an explicit rationale and still must resolve to a party observed in a pilot CHES wave.

Build the approved outcome facts and country-year panel:

```powershell
python -m src.transforms.build_outcome_panel
```

The country-year panel contains only approved Eurostat outcome configurations for 2010–2022. Cabinet periods remain in their own dated table and are not collapsed into one cabinet per year.

Build the approved OECD PF3.2 policy-context facts:

```powershell
python -m src.transforms.build_policy_context
```

The command creates the ignored local file `data/processed/harmonized/fact_policy_indicator.csv`. It retains the approved 2015–2022 country-year scope, represents enrolment of children aged 0–2 in registered ECEC as a percentage, and rejects unexpected gaps or out-of-range values.

Build reviewed CHES party-position facts for the local dashboard:

```powershell
python -m src.transforms.build_party_positions
```

This local-only output contains parties with accepted ParlGov-to-CHES mappings at the original 2010, 2014 and 2019 CHES waves. `lrgen` remains on its original 0–10 general left–right scale; it is never interpolated into an annual ideology score.

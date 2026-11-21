# Political-context transformation

From the repository root, build the Phase 3 political-context intermediates:

```powershell
python -m src.transforms.build_political_context
```

The command creates ignored local files in `data/processed/political_context/`:

- `cabinet_periods.csv`: dated, half-open cabinet periods.
- `party_crosswalk_review.csv`: only direct ParlGov `chess` identifier links are accepted automatically; every missing or unavailable link is a manual-review item.

Reviewed continuity overrides are stored separately in `data/metadata/party_crosswalk_overrides.csv`; they require an explicit rationale and still must resolve to a party observed in a pilot CHES wave.

Build the approved outcome facts and country-year panel:

```powershell
python -m src.transforms.build_outcome_panel
```

The country-year panel contains only approved Eurostat outcome configurations for 2010–2022. Cabinet periods remain in their own dated table and are not collapsed into one cabinet per year.

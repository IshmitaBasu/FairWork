# Phase 3 party-crosswalk review

The crosswalk uses ParlGov's `chess` party identifier as the primary matching key. It does not use fuzzy matching.

- Accepted source-identifier matches must exist in a CHES pilot-country wave (2010, 2014 or 2019).
- A manually reviewed continuity override is allowed only when it records its rationale in `data/metadata/party_crosswalk_overrides.csv`.
- Coalition, regional, recently created and otherwise unsupported parties remain quarantined. They are never silently mapped to a similar party.

The current review output is generated with:

```powershell
python -m src.transforms.build_political_context
```

Review unresolved rows in `data/processed/political_context/party_crosswalk_review.csv` before admitting them to a published party-position panel.

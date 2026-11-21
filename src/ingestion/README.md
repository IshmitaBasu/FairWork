# Source-audit utilities

Run the Eurostat evidence gate from the repository root:

```powershell
python -m src.ingestion.audit_eurostat
```

The command retrieves the two planned Eurostat datasets for Germany, Spain, France and Sweden; writes local raw snapshots; and produces a country-year availability matrix plus retrieval hashes in `data/processed/source_audit/`.

It does **not** select a final dimension configuration, transform values, or treat every returned configuration as comparable. Inspect the generated audit and the source metadata before admitting a metric to the final pilot.

Profile the political data sources separately:

```powershell
python -m src.ingestion.audit_political_sources
```

It stores local CHES and ParlGov snapshots and emits coverage and schema profiles. Subsequent runs reuse the existing snapshot; pass `--refresh` only to deliberately retrieve a new release. It does not create a party crosswalk or make a cabinet-to-year assignment.

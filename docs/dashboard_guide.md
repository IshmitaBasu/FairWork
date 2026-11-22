# FairWork local dashboard

## Run it

From the repository root, regenerate the local curated data if necessary, then start Streamlit:

```powershell
python -m src.transforms.build_policy_context
python -m src.transforms.build_party_positions
python -m src.analytics.build_warehouse
python -m src.analytics.export_curated_data
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

Close any interactive Python or DuckDB session before rebuilding `data/processed/fairwork.duckdb`; DuckDB permits only one writer at a time.

## What it shows

- **Country explorer:** an outcome trend for one country, an optional overlay of that country's dated cabinet starts, data-quality notice, cabinet periods, CSV download and on-demand PNG chart export.
- **Cabinets & events:** a selected cabinet's recorded parties, a descriptive before/after timing window, a left/centre/right composition count and separate CHES party-wave context.
- **Political landscape:** an interactive CHES left–right spectrum for parties with accepted ParlGov-to-CHES mappings, selectable by original 2010, 2014 or 2019 survey wave.
- **Compare countries:** the same approved metric configuration across Germany, France, Spain and Sweden.
- **Methods & sources:** coverage, definitions, flags and the descriptive-only interpretation boundary.

The app reads only the curated Parquet files in `data/published/`. It never reads raw CHES, ParlGov, OECD or Eurostat snapshots directly.

The sidebar now states the active **selected country** directly below the single-country context control. That country controls the overview, explorer, cabinet and political-landscape pages. The Compare Countries page starts with it and separately states every country selected in its multi-country comparison control, so the two scopes cannot be confused.

Use **Hide observations with Eurostat flags** to inspect only unflagged outcome records across the outcome, explorer, event-window and comparison charts. It never alters the source data; turn it off to see all retained values and flags again.

## Interpretation boundary

Cabinet starts are factual date markers. They do not show that a cabinet, party position or policy caused a change in an annual outcome. Eurostat flags remain visible, missing values are not filled, and CHES party positions remain original survey-wave measures rather than annual scores. The blue-to-red spectrum visualizes CHES `lrgen` from 0 (left) to 10 (right); it is not a party ranking or endorsement.

## Local-only status

The dashboard is currently local. A later hosted version must have a reproducible source-data strategy and a fresh licence/redistribution review before publication. See `deployment_readiness.md` for the release gate.

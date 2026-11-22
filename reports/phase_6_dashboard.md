# Phase 6 local dashboard

**Status:** Complete locally on 22 November 2026. Not deployed.

## Delivered

- `app.py`: Streamlit entry point with Overview, Country explorer, Political landscape, Compare countries and Methods & sources views.
- `src/dashboard/data.py`: curated-Parquet loading and safe metric/year filters.
- `.streamlit/config.toml`: local visual configuration.
- `requirements.txt` and the `dashboard` extra in `pyproject.toml`: declared runtime dependencies.

## User-facing safeguards

- Country/year/metric filters operate on curated data only.
- The sidebar explicitly displays the selected single-country context; Compare Countries separately displays its multi-country selection.
- Country charts show only the selected country's cabinet starts.
- The selected country is the default across every page, including Compare Countries; extra countries are opt-in.
- Cabinet event windows display timing and available observations without estimating a cabinet effect.
- Cabinet-party membership is shown separately from selectable CHES survey waves, preventing invented annual ideology scores.
- The political landscape shows only parties with accepted ParlGov-to-CHES links, selectable at their original 2010, 2014 or 2019 CHES wave.
- Its blue-to-red 0–10 spectrum represents CHES `lrgen` (left to right); it is not an annual ideology score, government score or political endorsement.
- Eurostat status flags appear in the explorer and flagged observations can be inspected.
- An optional quality filter hides retained flagged observations consistently for outcome, event-window and comparison inspection without modifying source data.
- Cabinet context now includes a clearly labelled left/centre/right count at a chosen CHES wave; it is not a coalition ideology score.
- Cabinet timelines are dated periods, not annual government assignments.
- Downloaded CSVs contain only the currently displayed outcome data.
- The methods page states the source definitions, coverage and non-causal interpretation boundary.
- Keyboard focus is visibly styled and text labels explain colour bands, improving non-colour and keyboard use.

## Validation

The app passed Streamlit's headless render test using the local curated Parquet outputs, including 54 reviewed CHES party-wave records and 83 cabinet-party memberships. The test suite has eight passing tests. PNG export is prepared on demand with Kaleido; the renderer is safely optional because some restricted local environments do not permit its Chrome process. The dashboard remains local because raw source snapshots and derived local data are excluded from Git pending source-term review.

## Run

```powershell
python -m streamlit run app.py
```

See `docs/dashboard_guide.md` for the full rebuild and run instructions.

# Dashboard deployment readiness

FairWork is intentionally local until this checklist is complete. The checked-in application contains no hosted credentials and the raw source snapshots and curated Parquet outputs are ignored by Git.

## Before deploying

- Confirm that the Eurostat, OECD, ParlGov and CHES terms permit the intended public display and any required redistribution of derived data.
- Choose a reproducible hosted data strategy: approved committed fixtures, a permitted build-time retrieval process, or a licensed data store. Do not upload the present ignored local snapshots by default.
- Rebuild the warehouse and dashboard inputs in a clean environment; record source retrieval dates and validation counts.
- Run the GitHub Actions checks and add a deployment-specific smoke test against the intended host.
- Set any host secrets only in the host's secret manager; never put them in `.env`, source files or commits.
- Verify the public app has an accessible source/methodology notice, a privacy statement if analytics are enabled, and a clear non-causal interpretation boundary.

## Current state

The application is deployment-ready in code structure, but it is **not authorised for public deployment** because the source-term review and hosted-data strategy are outstanding. This is a deliberate release gate, not a technical failure.

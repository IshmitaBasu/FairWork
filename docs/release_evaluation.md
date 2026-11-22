# Release evaluation

**Status:** Portfolio documentation prepared; public release blocked by the documented data-terms gate.

| Dimension | Current evidence | Status |
|---|---|---|
| Pipeline validity | DuckDB validation plus 10 local automated tests | Passing locally |
| CI reliability | GitHub Actions syntax, unit and synthetic-fixture warehouse checks | Passing on `main` |
| Data coverage | 4 countries; outcomes/cabinets 2010–2022; OECD policy context 2015–2022 | Documented pilot scope |
| Political mapping | 19 accepted links; 7 unsupported links quarantined | Review boundary retained |
| Dashboard safeguards | Flags, selected-country state, dated cabinet context, source/method notices | Implemented locally |
| Responsive/manual UI check | Desktop and narrow-width review | Manual validation pending |
| Source reconciliation | Selected displayed values checked against approved snapshots | Manual validation pending |
| Public deployment | Licence review and reproducible hosted-data strategy | Blocked deliberately |

The passing CI workflow proves code and synthetic structural inputs work together. It does not verify a public source refresh, redistribute source data, or authorise deployment.

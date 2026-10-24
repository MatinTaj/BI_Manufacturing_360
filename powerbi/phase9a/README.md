# Manufacturing 360 â€” Power BI model and DAX preparation

Phase 9A prepares a complete Import-model handoff for the existing PostgreSQL database manufacturing_360, schema manufacturing_v2. It does not create a PBIX, change PostgreSQL or proceed to Phase 9B.

## Build inputs

- [Implementation guide](IMPLEMENTATION_GUIDE.md): exact connection, query import order, relationship/measure setup, formats, pages and slicers.
- [Star schema](STAR_SCHEMA.md), [table mapping](TABLE_MAPPING.csv), [relationships](RELATIONSHIPS.csv), [machine-readable model](model_spec.json).
- power_query/: 22 ready-to-paste M files, including nineteen model queries and three connection helpers. No credentials.
- [DAX library](DAX_LIBRARY.md): 120 core measures plus fourteen optional sensitivity measures; every formula has source lineage, definition, filters and validation method.
- dax/: structured measures.json, query-scoped core/optional DEFINE libraries, six optional parameter-table formulas and an optional non-overwriting Tabular Editor batch script.
- [All 49 approved KPIs mapped to DAX](KPI_TO_DAX.csv).
- [Financial and filter acceptance tests](FINANCIAL_VALIDATION.md) plus six ready-to-run Desktop/DAX Studio test files in validation/.
- [What-if readiness and limits](WHAT_IF_READINESS.md): six independent static sensitivities with default zero; not a prospective inventory forecast.
- [Official references](REFERENCES.md).

## Current verification status

Read-only PostgreSQL source projections, keys and all 34 relationship mappings have been checked against actual data. The 731-day calendar design covers the verified full years. All 36 existing SQL checks and 33 financial comparisons pass. Static DAX column/dependency/delimiter and M delimiter checks pass. Those checks do **not** execute DAX, M or the optional C# script. Actual model behavior has not been verified in Power BI Desktop.

All required inputs for the defined dashboard and static six-parameter sensitivity scope are ready as preparation artifacts. No new database views or data generation are required. Desktop must still validate connector authentication/refresh, M evaluation/types, relationships, DAX compilation/filter/time behavior, totals, snapshots, optional script/parameters and visual interactions. A full prospective scenario forecast would require a separate scope and assumptions.

The detailed completion report location is in report_path.txt. Existing datasets, SQL analyses and powerbi/dash1.pbix remain unchanged. Do not automatically proceed to Phase 9B.

[Detailed Phase 9A completion report](COMPLETION_REPORT.md)

# Phase 9A completion report

**Preparation status: complete. All required inputs are ready for the defined Power BI Import dashboard and optional static sensitivity scope.** This is not a deployed or runtime-validated semantic model. Phase 9B was not started.

## Delivered architecture and code

- Nineteen core model tables: six dimensions (including the daily Date calendar), eleven facts and two disconnected reconciliation references.
- Exact table sources, columns, business grains and keys in model_spec.json / TABLE_MAPPING.csv; 30 active and four inactive Single-direction 1:* relationships in RELATIONSHIPS.csv.
- Twenty-two Power Query M files: nineteen model queries and three parameter/function helpers. Queries reference existing manufacturing_360.manufacturing_v2 objects only. Receipt/order month fields and the Date calendar are explicitly model-derived, not invented database columns.
- DAX library: 120 core measures, fourteen optional sensitivity measures and six optional disconnected parameter-table definitions. Every measure documents exact formula, required direct/transitive sources, definition, filter behavior, format and validation method. Numbered creation order is dependency-safe.
- One-to-many mapping of every one of the 49 approved business KPIs to named measures.
- Six ready-to-run DAX acceptance-query files for annual, combined, monthly, operational, edge-filter and optional zero-scenario checks. Read-only source SQL projections are supplied separately.
- Step-by-step Desktop guide covering connectivity, import sequence, relationships, Date marking, formats, measure creation, report-page design, slicers, interactions, refresh and acceptance.
- Reproducible read-only SQL/static checker and complete preservation evidence.

## Verified source facts and checks

Live database: manufacturing_360; schema manufacturing_v2; PostgreSQL 18.6 on localhost:5432. Existing secure authentication was used, without logging credentials. All eighteen database projections executed successfully. Each model source has its expected row count and unique business key. All 34 proposed relationship endpoints have zero orphan keys and valid unique dimension sides. No new SQL view or other database object is required.

Date coverage was checked against actual accounting, order, expected receipt, receipt and shipment dates. It is 2024-01-01 through 2025-12-31, with 731 unique calendar dates and full years. Monthly facts connect to Date via first-of-month values. Accounting pages require whole months; inactive date-role measures support explicitly daily operational measures.

All 36 existing live SQL integrity checks and 33 approved financial comparisons passed. Approved annual and combined financial totals remain unchanged. Examples: 2024 revenue EUR 10,559,374.25 / OP EUR 1,191,810.42; 2025 revenue EUR 10,973,277.52 / OP EUR 1,258,943.35; combined revenue EUR 21,532,651.77 / OP EUR 2,450,753.77. These are PostgreSQL references, **not executed DAX results**.

Static checks verified 130 direct DAX column references, ordered measure dependencies, delimiter balance, model relationship configuration, all 49 KPI mappings and M delimiter balance. There is no DAX/M/C# compiler or Power BI Desktop execution behind that PASS. Static checks cannot prove expression binding, relationship overrides, visual filter semantics or connector evaluation.

Before/after data fingerprints for all 23 public/v2 tables and normalized definition hashes match. All 252 pre-existing project file hashes match, including staged/processed data, financial code, SQL analyses, documentation and the existing PBIX. Only new files inside powerbi/phase9a and this phase's report directory were written. No database object, dataset, assumption, existing SQL analysis or Power BI file was modified.

## Modeling safeguards

No fact-to-fact, bidirectional, many-to-many or dimension-to-dimension links are needed. The line dimension filters facts directly rather than connecting through Product. Summary views are not added as extra business facts. Financial references are disconnected and read by deliberate TREATAS only.

Company OP is Date-only and BLANK under unsupported entity filters; product/customer contribution remains distinct from company profit. Capacity and pool measures are line-level, not arbitrarily product allocated. Snapshot closing values use the selected latest month; midpoint averages and full-year turnover avoid summing snapshots. COGS and inbound freight components are recognized once.

Optional sensitivity independently covers material, inbound, outbound, labor, energy and net selling prices with default zero. Fixed selling/admin remain fixed; revenue-variable selling follows revised revenue. This is historical static-volume sensitivity, not a prospective inventory/capacity forecast. Base measures never reference scenario parameters. Full prospective forecasting requires separately approved lineage/timing/volume assumptions outside this handoff.

## What still must be tested in Power BI Desktop

1. Installed PostgreSQL connector, credential handling/native SELECT prompts, M evaluation, complete refresh and all imported data types/row counts.
2. Exact relationship setup, Date marking/sorts, inactive date roles and absence of unintended auto-detected reference relationships.
3. Compilation and execution of every core DAX measure; source/dependency checks alone are not syntax/type certification.
4. Financial reconciliation at month/year/combined levels, with percentages converted from DAX fractions to SQL percentage units.
5. Entity/cohort slicers, company-scope BLANK guards, zero denominators, first-year comparisons, partial-month guards, full-year turnover and non-additive inventory totals.
6. Daily operational role behavior, ensuring daily revenue is never combined with unallocated daily company costs.
7. Optional Tabular Editor script compilation/deployment, if that tool is used; manual complete formulas remain available without it.
8. Optional parameter tables, single-select zero defaults, zero-scenario reconciliation and isolated/combined linear sensitivity behavior.
9. Visual totals, interactions, drill-through, repeat refresh and eventual gateway/deployment performance. No PBIX, visual or semantic model has been built in this phase.

There is no missing SQL/data-model prerequisite for the requested core dashboard. Desktop acceptance and operational reporting credentials remain deployment gates. Supplier reliability variation, WIP/daily inventory and supplier/material-specific sales COGS lineage are unavailable data, not features silently promised by this design. No Phase 9B action was taken.

## File inventory and evidence

The package README links all deliverables. artifact_manifest.json in the report lists every new artifact and SHA-256 hash. The report contains live_schema_columns.json, source_checks.json, relationship_checks.json, calendar_check.json, sql_model_checks.json, sql_baseline_checks.json, approved_financial_reference.json, static_validation_results.json, before/after database fingerprints and the protected original-file manifest.

All findings above distinguish live PostgreSQL checks, static preparation checks and unexecuted Desktop tests. No DAX result has been invented.

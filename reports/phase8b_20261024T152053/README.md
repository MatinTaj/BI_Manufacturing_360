# Phase 8B live migration execution report

Status: **PASS — committed and operational; ready for Power BI integration.**

## Connection and safety

Existing PostgreSQL 18.6, localhost:5432, database manufacturing_360, verified role postgres. Initial schemas were information_schema, pg_catalog, pg_toast and public; manufacturing_v2 was absent. CREATE privilege was confirmed. Secure existing authentication was used without printing or embedding credentials. No database or server was created.

A schema-absence guard under an advisory transaction lock protects against races. All new objects are confined to manufacturing_v2. No public objects were modified, dropped or truncated. Migration, imports, views, baselines and validation executed once in one transaction and committed. There were no failures or retries. The first sandboxed connectivity attempt was denied local socket access; an approved execution context enabled the read-only preflight before any migration.

## Created objects

19 source tables plus two audit tables, 15 analytical bi_ views plus two audit_ views, 41 total indexes (16 explicit and 25 primary/unique indexes). Catalog verification found 21 primary keys, 26 foreign keys, 4 additional unique constraints, 294 CHECK constraints and 225 NOT NULL constraints. All catalog constraints were validated. All 17 views passed live smoke queries.

Source table names and column layouts are preserved. Analytical names are manufacturing_v2.bi_NAME; audit names are manufacturing_v2.audit_NAME. All constraint targets and view sources are schema-qualified; indexes reside with their owning tables. No public search-path dependency is needed.

## Imported source rows

| Dataset | Expected | Imported |
|---|---:|---:|
| months | 24 | 24 |
| production_lines | 3 | 3 |
| materials | 10 | 10 |
| suppliers | 15 | 15 |
| customers | 25 | 25 |
| products | 20 | 20 |
| material_suppliers | 30 | 30 |
| bom | 64 | 64 |
| line_month_capacity | 72 | 72 |
| production | 480 | 480 |
| purchase_order_lines | 144 | 144 |
| material_receipts | 144 | 144 |
| material_consumption | 1536 | 1536 |
| raw_material_inventory | 240 | 240 |
| manufacturing_costs | 72 | 72 |
| production_cost_allocation | 480 | 480 |
| finished_goods_inventory | 480 | 480 |
| sales | 2596 | 2596 |
| operating_expenses | 48 | 48 |

Total source rows: **6,483**. Audit expectation tables add 19 file records and three period records.

## Validation

All **36 live SQL checks returned zero failures**; all **33 Phase 7 metric comparisons passed**. Monetary totals match exactly. Margin comparisons use the approved tolerance of 0.00000001 percentage points. Checks cover PK/FK constraints, row counts, BOM consumption, capacity, activity allocations, line cost pools, material receipt terms, two-component raw inventory, carry-forward, five-component finished goods, capitalization, sales cent allocation, discounts, outbound freight, opex behavior and no-fanout P&L.

Evidence: validation_results.csv, pnl_reconciliation.csv, constraints.csv, indexes.csv, view_smoke_tests.csv and migration_execution.log. No validation was suppressed.

## Financial totals

| EUR unless % | 2024 | 2025 | Combined |
|---|---:|---:|---:|
| Net revenue | 10,559,374.25 | 10,973,277.52 | 21,532,651.77 |
| Manufacturing COGS | 8,095,663.36 | 8,411,512.20 | 16,507,175.56 |
| Gross profit | 2,463,710.89 | 2,561,765.32 | 5,025,476.21 |
| Gross margin % | 23.33197812 | 23.34548922 | 23.33886353 |
| Outbound freight | 286,376.98 | 295,196.43 | 581,573.41 |
| Selling | 525,761.49 | 539,655.54 | 1,065,417.03 |
| Administration | 459,762.00 | 467,970.00 | 927,732.00 |
| Idle costs | 0.00 | 0.00 | 0.00 |
| Abnormal production losses | 0.00 | 0.00 | 0.00 |
| Operating profit | 1,191,810.42 | 1,258,943.35 | 2,450,753.77 |
| Operating margin % | 11.28675234 | 11.47281063 | 11.38156970 |

## Execution plans

ANALYZE was restricted to the 21 new tables. EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) completed for six representative read-only analytical queries:

| Query | Execution ms | Result rows | Temp blocks written |
|---|---:|---:|---:|
| monthly_pnl | 1.302 | 24.0 | 0 |
| product_profitability | 4.611 | 20.0 | 0 |
| customer_month | 0.962 | 25.0 | 0 |
| procurement | 0.613 | 144.0 | 0 |
| raw_inventory | 0.084 | 10.0 | 0 |
| production | 0.277 | 3.0 | 0 |

No sort spills or temporary-file writes occurred. Sequential scans on these small tables are reasonable; no obvious performance issue was found. These single local runs are not concurrency/load benchmarks. Full plans and actual queries are saved in query_plans.json.

## Preservation checks

Before/after normalized pg_dump schema definitions are identical for public (only the per-run random restrict token was normalized). Both public tables have unchanged row counts and order-independent full-row MD5 fingerprints. These are before/after checks; a live application writing concurrently could invalidate the comparison, but no differences occurred. All 61 protected files under data and powerbi have unchanged SHA-256 hashes. No generator or PBIX modification occurred.

## File changes

Created SQL package files in sql/v2/existing_schema/: 01_schema.sql, 02_import.psql, 03_views.sql, 04_reference_baseline.sql, 05_validate.sql, apply.psql, run_schema_import.ps1, README.md, report_path.txt.

Modified sql/v2/README.md to point to the active deployment and retired sql/v2/run_import.ps1 with an immediate error, preventing accidental invocation of the superseded CREATE DATABASE workflow. Original root-level DDL/import SQL remains historical and was not executed.

Created docs/power_bi_v2_connection.md. Updated docs/postgresql_v2_architecture.md and docs/power_bi_v2_model.md with the active schema mapping. No source economic logic, staging datasets, legacy SQL portfolio or Power BI files changed.

This report directory contains the execution log, connection preflight, static safety checks, protected-file hashes, before/after public definitions and fingerprints, imported row counts, constraints, indexes, view inventory/smoke tests, financial totals, reconciliation results, six plans and execution_summary.json. artifact_manifest.json inventories every report/package artifact and hash.

## Remaining issues and next steps

No migration or financial reconciliation issue remains. The preserved exact-half-cent labor compatibility rule from Phase 8A remains in effect; all component conservation and EUR baseline checks remain exact. Provisioning a dedicated read-only Power BI role is recommended rather than ongoing postgres superuser use. No role/grants were created without a defined user requirement. Power BI connector/model/report acceptance remains pending and no existing model was switched. See docs/power_bi_v2_connection.md.

The schema now exists; do not rerun migration or attempt reset. Read-only health queries are documented in the package README.

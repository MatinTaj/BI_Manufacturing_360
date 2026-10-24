# Phase 8A implementation and migration-readiness report

## Outcome

Prepared PostgreSQL 18 architecture for manufacturing_360_v2 using all 19 approved Phase 7 staging datasets. No database was connected to, created or modified. No CSV, existing SQL portfolio file, Power BI file or prior project file was changed. SHA-256 comparison confirmed all 101 pre-existing project files unchanged after implementation and tests.

## Created files

Under sql/v2/: 00_create_database.sql, 01_schema.sql, 02_import.psql, 03_views.sql, 04_reference_baseline.sql, 05_validate.sql, apply.psql, run_import.ps1, database_contract.json, input_manifest.json, static_check.py, static_check_results.json, data_dictionary.md, README.md and this IMPLEMENTATION_REPORT.md.

Under docs/: postgresql_v2_architecture.md and power_bi_v2_model.md.

Total: 17 new project files; no existing files modified. The isolated pglast parser was installed outside the project for offline checks, not added to generator dependencies.

## Database design

19 erp source tables preserve source columns, keys and grains; two audit expectation tables pin approved row counts/hashes and financial totals. Primary/unique keys, immediate composite foreign keys, finite/nonnegative values and accounting identities protect imports. Sixteen explicit indexes supplement key indexes. Fifteen analytical bi views cover production, conversion components, sales, customer/product performance, procurement, inventory and P&L. Two audit views support reconciliation.

Analytical views derive results from facts and contain no frozen financial results. Cross-grain facts are aggregated before joins. Monthly inventory snapshots, cost pools versus allocations, and annual versus combined financial rows are documented as non-additive combinations.

Import defaults to plan-only. Future explicit execution uses fixed database guards, a PostgreSQL 18 guard, approved input hashes, parent-first client COPY with HEADER MATCH and one schema/data/view/validation transaction. Failures are raised and never suppressed. No DROP/TRUNCATE or automatic promotion is included.

## Safe checks completed

- PostgreSQL 18 grammar via pglast v8.7, parser version 18.6: 85 SQL statements and three PL/pgSQL blocks parsed.
- Offline relation/column binding: 212 SELECT scopes and 17 views checked.
- All 19 CSV schemas, exact numeric precision/scale, primary/unique keys and foreign keys checked.
- All 19 explicit COPY column lists and parent-first dependencies checked.
- 160,078 evaluations of planned row CHECK expressions passed against actual staged rows.
- 33 independent financial metric comparisons passed against the approved Phase 7 candidate (exact EUR, percentage tolerance 0.00000001 points).
- PowerShell AST syntax check passed. Plan-only wrapper passed with a deliberately nonexistent psql executable path, confirming it invokes no psql in default mode.
- Existing non-destructive regression suite: 61 tests passed. No full generation pipeline ran.
- Original 101 project file hashes unchanged after checks, including every existing dataset, SQL portfolio and Power BI file.

The 36 SQL audit checks are prepared but have NOT executed in PostgreSQL. Offline parsing/name checks cannot prove server operator/type resolution, COPY behavior, transactions, privileges or query plans. See static_check_results.json for machine-readable results.

## Financial reference verified offline

| Metric EUR | 2024 | 2025 | Combined |
|---|---:|---:|---:|
| Net revenue | 10,559,374.25 | 10,973,277.52 | 21,532,651.77 |
| Manufacturing COGS | 8,095,663.36 | 8,411,512.20 | 16,507,175.56 |
| Gross profit | 2,463,710.89 | 2,561,765.32 | 5,025,476.21 |
| Outbound freight | 286,376.98 | 295,196.43 | 581,573.41 |
| Selling | 525,761.49 | 539,655.54 | 1,065,417.03 |
| Administration | 459,762.00 | 467,970.00 | 927,732.00 |
| Operating profit | 1,191,810.42 | 1,258,943.35 | 2,450,753.77 |

Idle and abnormal losses are zero in this candidate, but remain explicit dynamic deductions in P&L views and validations. Financial expectations are isolated in audit tables, never analytical view formulas.

## Remaining risks and approval readiness

Prepared for a separately authorized PostgreSQL 18 integration run; not yet certified as successfully imported. Required next steps are selecting a server/owner, confirming permissions and client encoding, running the transactional migration, inspecting all audits, and checking plans/refresh performance before Power BI connection changes.

One preserved compatibility case: February 2024 L01 stored labor rounds down at an exact half-cent (96,531.705 to 96,531.70), whereas NUMERIC gives 96,531.71. A narrowly defined half-cent exception preserves the approved candidate; component totals and P&L remain exact. A future versioned generator should consistently use Decimal. This is not a general tolerance or a silent adjustment.

CREATE DATABASE is outside the import transaction and may leave an empty target after import failure. The scripts deliberately provide no destructive retry cleanup. Existing one-full-receipt-per-order, single-line product assignment and nonnegative transaction assumptions require schema review before future partial receipts/returns. Credentials, reporting grants, backup policy and live performance remain deployment decisions.

Power BI recommendations preserve separate fact grains, single-direction dimension relationships, semi-additive inventory and explicit unallocated operating expenses. No report is automatically switched.

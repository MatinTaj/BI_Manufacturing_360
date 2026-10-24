# Active Phase 8B schema-only migration

Successfully executed on PostgreSQL 18.6 at localhost:5432, existing database `manufacturing_360`, schema `manufacturing_v2`, using authenticated role `postgres`. No server or database was created. See the report path in report_path.txt.

## Object naming

All source tables keep their CSV names inside manufacturing_v2. Analytical views have `bi_` prefixes; audit tables/views have `audit_` prefixes. This avoids collisions such as a raw_material_inventory source table and its analytical view. There are no erp/bi/audit schemas in this architecture. Constraints and indexes belong to the new schema's tables; all foreign-key targets and view references are schema-qualified. Index names inherit the owning table schema.

All original source columns, monetary rules, component reconciliation and 36 audit checks are unchanged. The Phase 8A contract and dictionary still describe source columns/keys; translate erp.NAME to manufacturing_v2.NAME, bi.NAME to manufacturing_v2.bi_NAME and audit.NAME to manufacturing_v2.audit_NAME. The original Phase 8A CREATE DATABASE scripts are historical, not part of this workflow.

## Execution safety

`run_schema_import.ps1` defaults to plan-only. Its `-Execute` option verifies all 19 approved CSV hashes/headers and the financial reference before invoking psql. psql uses noninteractive secure authentication (`-w`), no credential arguments, `-X`, ON_ERROR_STOP and the fixed existing database. It never creates a database or touches public.

apply.psql runs BEGIN, sets a local pg_catalog search_path and time zone, and includes 01_schema, 02_import, 03_views, 04_reference_baseline and 05_validate before COMMIT. The first SQL guard verifies PostgreSQL 18, the database name, CREATE privilege and schema absence under a transaction advisory lock. CREATE SCHEMA does not use IF NOT EXISTS. If the target exists, execution stops before changing it. No reset, overwrite, drop, truncate or destructive retry is implemented.

This schema now exists: do not rerun migration. Use read-only validation queries for later health checks:

```sql
SELECT * FROM manufacturing_v2.audit_validation_results ORDER BY check_name;
SELECT * FROM manufacturing_v2.audit_pnl_reconciliation ORDER BY period,metric;
SELECT * FROM manufacturing_v2.bi_period_pnl ORDER BY period;
```

Every validation failure raises an exception before import COMMIT. The schema/data/view transaction rolls back on failure. No failed validations occurred in this execution. ANALYZE was run only on newly created schema tables after success.

## Power BI

Connect to PostgreSQL server `localhost:5432`, database `manufacturing_360`. Select objects under manufacturing_v2; prefer `bi_sales_detail`, `bi_monthly_pnl` and other views appropriate to the intended grain. See docs/power_bi_v2_connection.md. Do not mix legacy public tables into v2 measures accidentally. A dedicated read-only reporting role is recommended; role creation/grants and existing report updates were not performed.

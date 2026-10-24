# Manufacturing 360 v2 SQL package — active deployment

Phase 8B is deployed inside the EXISTING database `manufacturing_360`, schema `manufacturing_v2`, on PostgreSQL 18.6. No new server or database was created.

Use [the active schema-only guide](existing_schema/README.md) and [Power BI connection instructions](../../docs/power_bi_v2_connection.md). The original root-level 00–05 scripts, apply.psql, contract/dictionary, static results and implementation report are preserved Phase 8A history for a superseded separate-database design; do not execute them. The old run_import.ps1 now fails immediately to prevent accidentally using that retired workflow.

The active schema already exists. Do not rerun the importer: its guard will stop rather than overwrite. All 19 CSVs are loaded, 36 SQL checks passed, and 33 financial baseline comparisons passed. Existing public schema/data and protected files were verified unchanged.

Latest execution evidence: [Phase 8B report](../../reports/phase8b_20261024T152053/README.md). [Source column dictionary](data_dictionary.md) remains valid for column types and business keys, with schema names translated as described in the active guide.

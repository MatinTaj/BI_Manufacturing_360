# Phase 8C completion report

Status: **PASS — complete. Phase 9 not started.**

## Deliverables

Created sql/analytics/: eight business SQL modules (01–08), 09_validation.sql, run_analytics.py, analysis_catalog.json, README.md, BUSINESS_FINDINGS.md, KPI_DICTIONARY.md and KPI_DICTIONARY.csv. Created sql/README.md as the portfolio entry point. No pre-existing SQL or project documentation was edited. Reports from execution attempts are retained under reports/phase8c_*; the final accepted run is this directory.

Each business module has two executed queries with question, source/grain, KPIs, logic, verified output links, interpretation and limitations. Output CSVs and query_results.json preserve the full verified results. CSV NULL fields are blank; JSON decimals are stored as strings to retain monetary precision.

## Live execution and validation

PostgreSQL 18.6, localhost:5432, existing manufacturing_360 database, manufacturing_v2 schema, verified postgres account. Authentication was noninteractive through the existing secure configuration; no credentials were printed or written. PostgreSQL enforced REPEATABLE READ READ ONLY. SQL was AST checked with PostgreSQL 18 grammar. No database object, dataset, assumption or Power BI file was modified.

| Verification | Passed |
|---|---:|
| Business modules / SELECT queries | 8 / 16 |
| Validation/diagnostic SELECT queries | 3 |
| Explicit source, join, ratio and negative-control gates | 83 |
| Existing Phase 8B model gates re-evaluated | 36 |
| Approved annual/combined financial metric comparisons | 33 |
| Annual cross-analysis reconciliations | 22 |
| Annual inbound freight recognition bridges | 2 |
| Database tables fingerprinted, public plus v2 | 23 |
| Protected data/Power BI/source/test/existing SQL file hashes unchanged | 91 |

Primary keys, every source foreign-key relationship and required source field were checked for duplicates/orphans/NULLs. Source/view row coverage and product/month uniqueness protect joins. Independent analysis totals reconcile revenue, COGS, GP, customer contribution, outbound, manufacturing components, inventory COGS and year-end YTD values. Negative controls deliberately detect duplicate, orphan, double-counting and fanout fixtures without modifying stored data. Zero-denominator, noninteger division, NULL fallback and ratio-of-sums behavior were exercised.

Financial EUR comparisons are exact; approved percentage tolerance is 0.00000001 percentage points. The runner checks both live audit tables and the hash-pinned Phase 7 financial_comparison.csv independently. All 36 original SQL gates returned zero failures, and all 83 portfolio gates returned zero failures. Source data/definition fingerprints before and after are identical, including existing public objects.

## Verified financial and business findings

2025 revenue EUR 10,973,277.52, manufacturing COGS EUR 8,411,512.20, operating profit EUR 1,258,943.35. Revenue grew 3.92%; operating profit grew 5.63%. Combined revenue remains EUR 21,532,651.77 and operating profit EUR 2,450,753.77.

Product gross margin ranges 12.80%–34.09%. Top-five customer share is 23.23% in 2025. Labor accounts for 43.87% of 2025 allocated manufacturing cost. Combined inventory days are an estimated 14.50 in 2025 versus 9.63 in 2024, subject to startup and midpoint limitations.

The deliberately unsafe join diagnostic expands 2,596 sales rows to 8,327 (3.2076×). These diagnostic rows are not used for financial results. Supplier OTD is 100% for 144 receipts; 4 suppliers have no observations. No comparative reliability claim is made.

Full per-analysis evidence and business interpretation: [BUSINESS_FINDINGS.md](../../sql/analytics/BUSINESS_FINDINGS.md).

## Execution history and remaining issues

The initial run stopped during client-side JSON parsing of the catalog response because PostgreSQL JSON aggregate formatting spanned multiple lines. No business analyses or writes ran in that attempt. The runner was corrected to compact JSONB framing. Subsequent successful runs validated the analyses before and after AST formatting; the final run adds the complete 22 cross-analysis gates. No SQL integrity or financial validation failure occurred. Attempt directories are retained rather than silently deleted.

No unresolved financial or integrity issue remains. Limits: synthetic assumptions, uniformly on-time receipts, approximate midpoint inventory, zero opening FG in 2024, no WIP/OEE/causal root causes/credit risk and unallocated company opex. A dedicated least-privilege reporting role remains an operational recommendation; no roles/grants or Power BI changes were made. Query runtime is a local observation, not a load benchmark. No Phase 9 action was taken.

## Evidence inventory

- execution_summary.json: final machine-readable PASS and preservation results.
- query_results.json plus 20 query/environment CSVs: 16 business outputs, three validation/diagnostic outputs and environment.
- database_fingerprints_before/after.json: table data multiset hashes and counts.
- database_definitions_before/after.sql: public/v2 definition snapshots, normalized only for pg_dump random restrict tokens.
- protected_files_before.json: 91 original protected-file SHA-256 values.
- artifact_manifest.json: complete new portfolio/report file hashes and source SQL provenance.

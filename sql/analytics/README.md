# Manufacturing 360 — SQL Business Analytics

A PostgreSQL portfolio that follows manufacturing economics from purchasing and production through inventory, customer sales and company profit. It uses a fictional automotive-parts manufacturer with 19 validated datasets covering 2024–2025. Results are synthetic and do not describe a real company.

## Business coverage

| Module | Decision supported | SQL techniques |
|---|---|---|
| [01 Executive financial](01_executive_financial.sql) | Revenue/profit trends and YTD tracking | CTE, LAG, ordered running totals |
| [02 Product profitability](02_product_profitability.sql) | Margin ranking and realized unit economics | Ranking, contribution windows, annual comparisons |
| [03 Manufacturing costs](03_manufacturing_costs.sql) | Component exposure and labor/energy intensity | LATERAL unpivot, weighted ratios, independent facts |
| [04 Production efficiency](04_production_efficiency.sql) | Capacity and quality monitoring | Multi-level aggregation, LAG, ranking |
| [05 Supplier/procurement](05_supplier_procurement.sql) | Spend concentration and observed reliability | LEFT JOIN, FILTER, receipt-weighted rates |
| [06 Inventory turnover](06_inventory_turnover.sql) | Inventory investment and flow/stock ratios | Preaggregation, month spine, midpoint averages |
| [07 Customer concentration](07_customer_concentration.sql) | Top-customer exposure and contribution | ROW_NUMBER, Pareto windows, top-N, HHI |
| [08 Logistics](08_logistics_distribution.sql) | Segment distribution cost and freight recognition | Separate fact aggregates, inventory bridge |
| [09 Validation](09_validation.sql) | Trustworthy analytics | 83 gates, negative fixtures, baseline checks, fanout diagnostic |

Each module documents its business question, source grain, KPI definitions, SQL logic and limitations. [Business findings](BUSINESS_FINDINGS.md) add the verified results and interpretation for all eight analyses. The [49-KPI dictionary](KPI_DICTIONARY.md) and [machine-readable CSV](KPI_DICTIONARY.csv) define reusable semantics for future Power BI measures.

## Verified highlights

- Revenue increased 3.92% in 2025; operating profit increased 5.63%.
- Product gross margins range from 12.80% to 34.09% over the combined period.
- Top-five customer revenue concentration was 23.23% in 2025.
- Supplier receipt OTD is uniformly 100% in this synthetic sample; reliability differentiation is therefore limited.
- All financial totals reconcile to the approved Phase 7/8B baseline without changing assumptions.

## Reproduce safely

Prerequisites: existing PostgreSQL 18 database manufacturing_360 and completed manufacturing_v2 deployment, psql/pg_dump clients, Python 3 and pglast 8.x with PostgreSQL 18 grammar. The reference Phase 7 report and input manifest must remain available. Use existing secure pgpass authentication; no passwords are accepted or embedded. The provided runner targets localhost:5432 as postgres to match the verified environment. A separately provisioned reader is recommended for ongoing use.

From the project root:

```powershell
python -B sql/analytics/run_analytics.py
```

Use `--parser-path` for an isolated parser installation and `--psql` for another PostgreSQL 18 client path. The runner creates a new timestamped reports/phase8c_* directory, parses every module, rejects non-SELECT statements and locks, and executes in REPEATABLE READ READ ONLY. Validation gates run before analyses. No CREATE, ALTER, COPY FROM, INSERT, UPDATE, DELETE, ANALYZE or other database modification is executed. pg_dump is definition-only read access.

For an individual file in an already authenticated psql session:

```sql
BEGIN READ ONLY;
SET LOCAL search_path = pg_catalog;
\i sql/analytics/01_executive_financial.sql
ROLLBACK;
```

The full runner is preferred because it preserves a consistent snapshot, stops on errors, reconciles the baseline and checks before/after data and definitions. Running a single file does not replace those controls.

## Accounting and modeling safeguards

- Revenue is net of discounts; manufacturing COGS retains purchase materials, inbound freight, labor, energy and overhead exactly once.
- Outbound freight is a selling/distribution expense below gross profit; selling and administration remain separate.
- Product/customer contribution excludes unallocated company operating costs.
- Closing inventory is semi-additive; annual flow/stock ratios use monthly midpoint averages, not summed closing snapshots.
- Ratios use numeric division and NULLIF denominators; initial comparisons and unobserved supplier performance remain NULL.
- Facts are aggregated to compatible grains before joins. Pool costs and their allocations are alternative perspectives.

## Evidence and limitations

[Final execution report](../../reports/phase8c_20261024T232331/README.md): 16 business SELECT queries plus three validation/diagnostic queries executed; 83 quality gates, existing 36 model gates and 33 approved financial comparisons passed. Twenty-two annual cross-analysis checks and two freight bridges passed. Data/definitions for 23 tables and hashes for 91 protected files were unchanged. No Phase 9 work was started.

Time-based inventory is approximate; there is no WIP, daily inventory, machine-level OEE, supplier disruption history, customer credit risk or demand elasticity. Analysis supports questions and diagnosis within those limits. It does not demonstrate causal operational improvements. [Power BI connection guide](../../docs/power_bi_v2_connection.md) covers the already deployed schema; no PBIX was changed.

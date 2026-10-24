# Power BI connection to the live v2 schema

## Connection

In Power BI Desktop choose Get Data → PostgreSQL database. Server: `localhost:5432`. Database: `manufacturing_360`. Import mode is suitable for this small synthetic dataset; DirectQuery is an optional separate performance decision. Authenticate through the connector's credential dialog. Do not put passwords in SQL, Power Query text or repository files.

For an initial owner-operated connection the verified account is postgres. For ongoing use, have an administrator provision a dedicated reader with CONNECT on manufacturing_360, USAGE on manufacturing_v2 and SELECT only on the required views/tables. No reporting role/grants were created in Phase 8B. A remote desktop or gateway interprets localhost as its own machine, so it needs the actual database host and appropriate network access.

In Navigator select the manufacturing_v2 schema. Examples:

- `bi_sales_detail`: shipment-level revenue, five COGS components and outbound freight.
- `bi_monthly_pnl`: 24 company/month rows including selling, administration and separately expensed production costs.
- `bi_product_month_profitability`: product/month gross profit and contribution after outbound freight.
- `bi_line_production_performance`: line/month capacity and output.
- `bi_raw_material_inventory`, `bi_finished_goods_inventory`: monthly snapshots.
- Source dimensions: months, products, customers, materials, suppliers, production_lines.

The other bi_ views cover customer/month, procurement, consumption, cost pools and allocations. Select detail facts OR their aggregated alternatives for additive measures, not both. Keep audit_ objects for validation rather than business fact relationships.

A SQL-based connection can explicitly use:

```sql
SELECT * FROM manufacturing_v2.bi_monthly_pnl;
```

Do not rely on search_path or switch existing public-backed reports automatically. Build a separate v2 model and verify it first. All previous relationship, component-cost and semi-additive inventory recommendations in power_bi_v2_model.md still apply with manufacturing_v2.bi_ naming.

## Reconciliation acceptance

Company results must reconcile to 2024 revenue EUR 10,559,374.25 / operating profit EUR 1,191,810.42; 2025 revenue EUR 10,973,277.52 / operating profit EUR 1,258,943.35; combined revenue EUR 21,532,651.77 / operating profit EUR 2,450,753.77. Full figures and comparisons are in the Phase 8B report.

Gross profit subtracts manufacturing COGS only. Operating profit also subtracts outbound freight, selling, administration, idle costs and abnormal production losses once. Inbound freight is already included in COGS. Do not add landed material aggregate to its components. Ratio totals use summed numerators/denominators. Closing inventory is not summed across months. bi_period_pnl includes overlapping annual and combined rows and should not be an additive fact table.

The database is validated and ready for a Power BI connection. Connector authentication, semantic-model relationships and visual reconciliation remain to be tested in Power BI; no PBIX was changed.

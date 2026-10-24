# Financial and semantic-model acceptance checklist

**Status: prepared, not executed in Power BI.** PostgreSQL validation has passed; DAX/M compilation, refresh and semantic-model behavior remain pending. Run these checks before report styling or acceptance. Do not change data, assumptions or reference figures to make a test pass.

## Financial baseline

EUR amounts below are the live approved audit expectations, not DAX results.

| Metric | 2024 | 2025 | Combined |
|---|---:|---:|---:|
| revenue | 10559374.25 | 10973277.52 | 21532651.77 |
| cogs | 8095663.36 | 8411512.2 | 16507175.56 |
| gross_profit | 2463710.89 | 2561765.32 | 5025476.21 |
| outbound_freight | 286376.98 | 295196.43 | 581573.41 |
| selling_expenses | 525761.49 | 539655.54 | 1065417.03 |
| administrative_expenses | 459762.0 | 467970.0 | 927732.0 |
| idle_cost | 0.0 | 0.0 | 0.0 |
| production_loss | 0.0 | 0.0 | 0.0 |
| operating_profit | 1191810.42 | 1258943.35 | 2450753.77 |
| gross_margin_pct | 23.33197812 | 23.34548922 | 23.33886353 |
| operating_margin_pct | 11.28675234 | 11.47281063 | 11.3815697 |

Monetary fields must match to EUR 0.00 after two-decimal rounding; the source/reference monetary model is exact cents. Unexpected raw floating differences should prompt a source type check (money should be Currency), not broad tolerance. Percent references are in 0–100 units; DAX ratios are 0–1. Use annual DAX query percent difference columns (multiply DAX by 100), tolerance 0.00000001 percentage points. Ratios such as midpoint inventory turnover may differ in final binary decimals; compare to Phase 8C at six decimal places.

## Step-by-step gates

1. [ ] Refresh all nineteen model tables; compare TABLE_MAPPING.csv counts. There must be 731 unique/nonblank DimDate dates, 20 products, 25 customers, 10 materials, 15 suppliers and three lines.
2. [ ] Verify exactly 30 active and four inactive relationships from RELATIONSHIPS.csv. All are Single dimension-to-fact 1:*. No blank/orphan dimension member, extra auto-detected reference relationship or ambiguous route is acceptable.
3. [ ] Verify DimDate is marked on Date; full-year calendar and correct sort columns. Disable Auto date/time. Monthly pages expose full Year/YearMonth selection only.
4. [ ] Create all 120 core measures in supplied order; check Desktop compilation, data types and display formats. No actual DAX runtime result has been claimed by Phase 9A.
5. [ ] Run 01_annual_financial.dax with no unrelated filters: two rows (2024/2025), all monetary differences round to zero; percent differences within tolerance. The query includes GP, outbound, selling/admin, idle/loss and OP so missing deductions cannot be hidden.
6. [ ] Run 02_combined_financial.dax with no filters: baseline revenue, COGS, GP and OP as above; freight bridge zero. Never sum annual and combined RefPnL rows.
7. [ ] Run 03_monthly_financial.dax: 24 monthly rows; SQL revenue/OP differences and COGS component differences zero; each inbound bridge zero. The two reference tables remain disconnected; TREATAS supplies only the deliberate reference month scope.
8. [ ] Run 04_operational.dax: line/year attempts, good, defects, utilization and defect ratios match Phase 8C 04_production_efficiency_q01.csv. Supplier rows match 05_supplier_procurement_q01.csv; four suppliers without receipts show BLANK OTD/target gap, not 0% failures. Inventory and customer metrics match 06_inventory_turnover_q01.csv and 07_customer_concentration_q02.csv after percentage unit conversion.
9. [ ] Verify 2024 FG turnover startup limitation and 2025 combined inventory days around 14.499049. Selecting one month or multiple years makes annual turnover BLANK. Closing stock on a year total must be December stock, not the sum of twelve closes.
10. [ ] Add a Product/Year matrix of Net Revenue, COGS, GP and realized price; reconcile to Phase 8C product-year output. Adding Customer should partition sales rather than duplicate them; sums must return original company/year revenue/COGS. Never join fact tables physically to obtain that matrix.
11. [ ] Test Line filtering on sales/production/manufacturing/FG and pool/capacity. No line-to-product relationship is needed. Product filtering should not invent a product share of line capacity or idle expense.
12. [ ] Run 05_filter_edge_cases.dax: all Boolean tests true. Partial-day monthly revenue is BLANK, product-filtered company OP is BLANK, unobserved supplier OTD is BLANK, first-year YoY is BLANK, partial-year turns are BLANK and the verified daily shipment role returns a value on 2025-12-31.
13. [ ] Compare daily shipment revenue summed over full months to monthly revenue; receipt/order date roles must change only the intended operational measure. Daily values cannot create a daily company P&L.
14. [ ] Test Customer share/Top-N/HHI with and without external Customer/segment slicers. Measures explicitly describe the externally selected cohort; remove customer slicers to reconcile full-company SQL. Do not label a selected-cohort share as all-customer share.
15. [ ] Test company OP under Product, Customer, Line, Material and Supplier selections; it must be BLANK. The product/customer alternative is Contribution after Outbound, not OP with silently unallocated expenses repeated.
16. [ ] If optional sensitivity is enabled, run 06_optional_zero_scenario.dax with six zero/default selections: differences round to zero. Change one parameter at a time and verify the component-specific linear effect. Outbound affects OP but not GP; price affects revenue and variable selling; fixed admin remains fixed.
17. [ ] Verify report-page slicer interactions, totals, drill-through grain and reset filters. No raw aggregate columns, summed unit prices or summed month-end snapshots appear as implicit measures.
18. [ ] Refresh again, rerun financial gates and save the new report only after acceptance. Existing dash1.pbix must remain untouched unless separately authorized.

## SQL verification available without modifying objects

validation/source_queries.sql contains all eighteen server projections for inspection. Source keys/relationship coverage and approved financial metrics were checked live read-only; see the Phase 9A report. Reuse existing manufacturing_v2.audit_validation_results and audit_pnl_reconciliation for health checks. No additional view, materialized view, function, table, grant or index is required by this handoff.

## Test log template

| Gate | Expected | Observed in Desktop | Pass/fail | Tester/date |
|---|---|---|---|
| Annual monetary reconciliation | All differences EUR 0.00 | Pending | Pending | |
| Annual % reconciliation | Within 0.00000001 pp | Pending | Pending | |
| Relationships / no fanout | 30 active + 4 inactive | Pending | Pending | |
| Snapshot / turnover semantics | Non-additive, full-year guards | Pending | Pending | |
| Filter / daily role behavior | All edge checks true | Pending | Pending | |
| Optional zero scenario | No change from baseline | Pending | Pending | |

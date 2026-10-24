# Verified business findings

All results were executed on PostgreSQL 18.6, database manufacturing_360, schema manufacturing_v2, against the unchanged approved synthetic dataset. Full precision results are exported; numbers below are rounded only for presentation. Interpretations are labeled as implications or limitations, not proven causes.

[Final execution evidence](../../reports/phase8c_20261024T232331/README.md) · [KPI dictionary](KPI_DICTIONARY.md)

## Executive financial performance

**Business question:** How did revenue and operating profit change, and which months drove the result?

**Sources and grain:** bi_monthly_pnl; bi_period_pnl; Q1 year; Q2 month.

**KPI definitions:** Gross margin=GP/revenue; operating margin=OP/revenue; YoY=(current/prior−1); percentage changes use percentage points.

**SQL logic:** LAG over annual results and same calendar month; cumulative SUM resets each year.

**Verified result and interpretation:** 2025 revenue was EUR 10,973,277.52, up 3.92%; operating profit was EUR 1,258,943.35, up 5.63%. Operating margin rose 0.1861 percentage points to 11.4728%. Profit grew faster than revenue under the approved cost structure; this does not prove a specific causal efficiency improvement.

**Limits:** Initial-year YoY is NULL. OP follows approved policy; net income and cash flow are outside scope.

**Executable SQL:** [01_executive_financial.sql](01_executive_financial.sql). Verified outputs: [Q1](../../reports/phase8c_20261024T232331/01_executive_financial_q01.csv), [Q2](../../reports/phase8c_20261024T232331/01_executive_financial_q02.csv).

## Product profitability

**Business question:** Which products create profit and how do realized prices compare with COGS per unit?

**Sources and grain:** bi_product_profitability; bi_product_month_profitability; Q1 product/full period; Q2 product/year.

**KPI definitions:** GP=revenue−five-component COGS; contribution=GP−outbound; realized price=revenue/shipped units.

**SQL logic:** DENSE_RANK and cumulative contribution ordered by gross profit; annual ratio-of-sums with same-product LAG.

**Verified result and interpretation:** Combined-period gross margins span 12.80% (P020, Transmission Housing 4) to 34.09% (P013, Suspension Link 1). The low-margin product realizes EUR 94.60/unit with EUR 82.49 manufacturing COGS/unit; its margin is positive, so low ranking does not mean loss-making. Examine engineering scope, mix, discounts and cost intensity before proposing price changes. Shared opex is deliberately unallocated.

**Limits:** Product contribution excludes unallocated company opex and idle losses. Price/cost changes are descriptive, not causal price-volume-mix attribution.

**Executable SQL:** [02_product_profitability.sql](02_product_profitability.sql). Verified outputs: [Q1](../../reports/phase8c_20261024T232331/02_product_profitability_q01.csv), [Q2](../../reports/phase8c_20261024T232331/02_product_profitability_q02.csv).

## Manufacturing costs and activity drivers

**Business question:** Which cost components dominate, and what drives line conversion economics?

**Sources and grain:** production_cost_allocation; bi_line_manufacturing_costs; Q1 year/component; Q2 line/year.

**KPI definitions:** Manufacturing total=five components; labor rate=cost/hours; energy tariff=cost/kWh; activity intensity=activity/attempted units.

**SQL logic:** LATERAL VALUES unpivots only five authoritative components; line pools analyzed independently from allocations.

**Verified result and interpretation:** In 2025 labor accounts for 43.87% of allocated manufacturing cost, purchase materials 40.54%, overhead 10.72%, energy 3.52% and inbound freight 1.34% (display rounding may prevent an exact 100%). Labor is the largest modeled component, making activity/support separation more useful than a blanket cost-cut assumption. The results reflect synthetic standard activities, not observed time-study productivity.

**Limits:** Never add cost pools to product allocations, or landed material subtotal to purchase/freight. Manufacturing additions differ from sales COGS because inventory defers costs.

**Executable SQL:** [03_manufacturing_costs.sql](03_manufacturing_costs.sql). Verified outputs: [Q1](../../reports/phase8c_20261024T232331/03_manufacturing_costs_q01.csv), [Q2](../../reports/phase8c_20261024T232331/03_manufacturing_costs_q02.csv).

## Production efficiency and defects

**Business question:** Which lines have capacity pressure and where are defects concentrated?

**Sources and grain:** bi_line_production_performance; bi_production_performance; Q1 line/year; Q2 product/full period.

**KPI definitions:** Utilization=attempted/effective capacity; defect rate=defective/attempted; yield=good/attempted.

**SQL logic:** Ratios of annual sums, annual LAG changes and defect-count ranking; no sales joins.

**Verified result and interpretation:** L03 defect rate rose 0.1090 percentage points to 2.2249% in 2025, while L01 and L02 defect rates declined. Annual utilization remains approximately 83–85% across the lines. L03 merits a quality review, but the dataset has no root-cause codes or machine-level evidence. Utilization alone is not OEE.

**Limits:** Capacity utilization is not OEE. No machine-speed or quality inspection detail; defect volume depends on production mix. No scrap-sale recovery assumption.

**Executable SQL:** [04_production_efficiency.sql](04_production_efficiency.sql). Verified outputs: [Q1](../../reports/phase8c_20261024T232331/04_production_efficiency_q01.csv), [Q2](../../reports/phase8c_20261024T232331/04_production_efficiency_q02.csv).

## Supplier performance and procurement

**Business question:** How concentrated is purchasing, and do observed receipts support supplier comparisons?

**Sources and grain:** suppliers LEFT JOIN bi_procurement_receipts; material receipt details; Q1 supplier/full period; Q2 material/receipt year.

**KPI definitions:** OTD=on-time receipt count/all observed receipts; lead days=receipt−order; purchase price=purchase EUR/kg.

**SQL logic:** Retains suppliers without receipts; COUNT(receipt_id) avoids counting null extended rows; weighted spend/quantity rates.

**Verified result and interpretation:** All 144 observed receipts were on time across 11 suppliers; 4 suppliers have no receipts and correctly show NULL reliability metrics. Supplier 10 represents 21.90% of purchase-only receipt spend. Purchasing concentration is measurable, but perfect synthetic OTD does not establish comparative supplier reliability or resilience.

**Limits:** Suppliers with zero receipts have NULL performance, not zero OTD. Synthetic scheduled/full receipts limit real supplier reliability conclusions. Receipt-based OTD is not order-line fill rate.

**Executable SQL:** [05_supplier_procurement.sql](05_supplier_procurement.sql). Verified outputs: [Q1](../../reports/phase8c_20261024T232331/05_supplier_procurement_q01.csv), [Q2](../../reports/phase8c_20261024T232331/05_supplier_procurement_q02.csv).

## Inventory valuation and turnover

**Business question:** How much cost is tied up in inventory and how quickly does it turn?

**Sources and grain:** raw_material_inventory; finished_goods_inventory; months; bi_monthly_pnl; Q1 year; Q2 month.

**KPI definitions:** FG turns=annual COGS/mean monthly midpoint FG; raw turns=annual landed issues/mean raw midpoint; combined days=calendar days*mean combined inventory/COGS.

**SQL logic:** Aggregate each inventory fact to month before joining; average (opening+closing)/2 across months; calendar carries actual 365/366 days.

**Verified result and interpretation:** Average FG inventory increased from EUR 135,645.95 in 2024 to EUR 253,401.04 in 2025. Combined inventory-days proxy rose from 9.63 to 14.50 days. This warrants monitoring stock investment, but the 2024 zero FG opening balance creates startup bias and monthly midpoints are an approximation. These are not cash conversion cycle days.

**Limits:** Midpoints approximate time-average balances; zero opening FG in 2024 creates startup bias. No WIP, daily balances or receivables/payables: this is not a cash conversion cycle. Closing balances are not summed across months.

**Executable SQL:** [06_inventory_turnover.sql](06_inventory_turnover.sql). Verified outputs: [Q1](../../reports/phase8c_20261024T232331/06_inventory_turnover_q01.csv), [Q2](../../reports/phase8c_20261024T232331/06_inventory_turnover_q02.csv).

## Customer concentration

**Business question:** How dependent is revenue on the largest customers, and does their contribution justify concentration?

**Sources and grain:** bi_customer_month_performance; Q1 customer/year; Q2 year.

**KPI definitions:** Revenue share=customer/year revenue divided by company/year; HHI=sum of squared percentage shares; contribution=GP−outbound.

**SQL logic:** Annual customer aggregation, deterministic ROW_NUMBER ties by customer_id, cumulative revenue windows and conditional top-N sums.

**Verified result and interpretation:** The largest five customers represented 24.42% of 2024 revenue and 23.23% in 2025. All 25 customers were active each year; the largest customer's 2025 share was 4.91%. The synthetic book is spread across customers, but no contracts, ownership grouping or credit risk data supports a claim of low commercial risk.

**Limits:** HHI describes this fictional customer book, not an antitrust market measure. No contract renewal, credit risk or group ownership data; customer contribution excludes shared opex.

**Executable SQL:** [07_customer_concentration.sql](07_customer_concentration.sql). Verified outputs: [Q1](../../reports/phase8c_20261024T232331/07_customer_concentration_q01.csv), [Q2](../../reports/phase8c_20261024T232331/07_customer_concentration_q02.csv).

## Logistics and distribution

**Business question:** How do outbound distribution costs differ by segment and how is inbound freight recognized?

**Sources and grain:** bi_sales_detail; bi_procurement_receipts; sales; Q1 year/customer segment; Q2 year freight recognition bridge.

**KPI definitions:** Outbound EUR/unit=freight/shipped; distribution burden=outbound/revenue; inbound receipt amounts are capitalized, not immediately expensed.

**SQL logic:** Segment ratios of sums; independent annual receipt and sales aggregates joined to calendar-year spine.

**Verified result and interpretation:** 2025 outbound freight averaged EUR 2.2000/unit for Aftermarket, EUR 1.1820/unit for OEM and EUR 1.4992/unit for Tier 1. Aftermarket's outbound burden was 3.53% of net revenue versus 2.02% for OEM. These modeled segment rates explain the descriptive gap; they are not evidence of carrier inefficiency. Both annual inbound freight bridges reconcile to EUR 0.00 after raw/FG inventory changes and abnormal losses, proving that receipt freight is not all expensed immediately.

**Limits:** Inbound purchases and recognized inbound COGS differ through inventory. Outbound is below GP, never inventory. Rates are synthetic blended per-unit costs; geography and minimum shipment charges are absent.

**Executable SQL:** [08_logistics_distribution.sql](08_logistics_distribution.sql). Verified outputs: [Q1](../../reports/phase8c_20261024T232331/08_logistics_distribution_q01.csv), [Q2](../../reports/phase8c_20261024T232331/08_logistics_distribution_q02.csv).

## Why join grain matters

The diagnostic in 09_validation.sql expands 2,596 sales rows to 8,327 rows when joined directly to production/material issues: a 3.2076× multiplication. This is a demonstration of an unsafe join, not an approved financial result. The business analyses independently aggregate facts or join unique dimensions; all cross-analysis totals reconcile.

## Verified financial baseline

| EUR | 2024 | 2025 |
|---|---:|---:|
| Net revenue | 10,559,374.25 | 10,973,277.52 |
| Manufacturing COGS | 8,095,663.36 | 8,411,512.20 |
| Gross profit | 2,463,710.89 | 2,561,765.32 |
| Outbound freight | 286,376.98 | 295,196.43 |
| Selling | 525,761.49 | 539,655.54 |
| Administration | 459,762.00 | 467,970.00 |
| Operating profit | 1,191,810.42 | 1,258,943.35 |

Combined net revenue remains EUR 21,532,651.77; COGS EUR 16,507,175.56; gross profit EUR 5,025,476.21; operating profit EUR 2,450,753.77. All 33 approved annual/combined monetary and percentage checks passed.

# Business KPI dictionary

Reusable SQL/Power BI semantic contract. Full machine-readable version: [KPI_DICTIONARY.csv](KPI_DICTIONARY.csv). All monetary fields are EUR. Ratios return NULL for undefined denominators rather than a fabricated zero. Do not round inputs; round only displayed outputs. SQL NUMERIC results retain precision. CSV output represents NULL as an empty field.

| KPI | Definition | Unit | Aggregation / caution |
|---|---|---|---|
| Net revenue | SUM(net_revenue_eur) | EUR | Additive. Gross revenue less discounts; not cash receipts |
| Manufacturing COGS | SUM(material_cogs_eur+inbound_freight_cogs_eur+labor_cogs_eur+energy_cogs_eur+overhead_cogs_eur) | EUR | Additive. Monthly weighted-average inventory costing |
| Purchase-material COGS | SUM(material_cogs_eur) | EUR | Additive. Authoritative component; inbound freight is already in total COGS |
| Inbound-freight COGS | SUM(inbound_freight_cogs_eur) | EUR | Additive. Authoritative component; inbound freight is already in total COGS |
| Labor COGS | SUM(labor_cogs_eur) | EUR | Additive. Authoritative component; inbound freight is already in total COGS |
| Energy COGS | SUM(energy_cogs_eur) | EUR | Additive. Authoritative component; inbound freight is already in total COGS |
| Overhead COGS | SUM(overhead_cogs_eur) | EUR | Additive. Authoritative component; inbound freight is already in total COGS |
| Gross profit | Net revenue - Manufacturing COGS | EUR | Additive. Excludes outbound and company operating expenses |
| Gross margin | 100 * SUM(gross profit) / NULLIF(SUM(net revenue),0) | % | Ratio of sums. Never average row margins |
| Outbound freight | SUM(outbound_freight_eur) | EUR | Additive. Distribution expense below gross profit; not operating_expenses CSV |
| Contribution after outbound | Gross profit - outbound freight | EUR | Additive. Not operating profit; shared opex and production losses are not product allocated |
| Contribution margin | 100 * SUM(contribution after outbound) / NULLIF(SUM(revenue),0) | % | Ratio of sums.  |
| Selling expenses | SUM(amount_eur) FILTER expense_category=selling | EUR | Additive. Fixed resource costs plus revenue-variable selling |
| Administration | SUM(amount_eur) FILTER expense_category=administration | EUR | Additive. Fixed administration; no outbound double-counting |
| Separately expensed production costs | SUM(idle_cost_eur) + SUM(production_loss_expense_eur), independently aggregated | EUR | Additive across distinct sources. Not COGS; ordinary partial defects remain in good-unit cost |
| Operating profit | Revenue - COGS - outbound - selling - administration - idle - abnormal losses | EUR | Additive. Not EBITDA, net income or cash flow |
| Operating margin | 100 * SUM(operating profit)/NULLIF(SUM(revenue),0) | % | Ratio of sums.  |
| Revenue YoY | 100*(current revenue-prior comparable revenue)/NULLIF(prior revenue,0) | % | Recompute at selected period. LAG must preserve comparable calendar coverage |
| Operating profit YoY | 100*(current OP-prior OP)/NULLIF(prior OP,0) | % | Recompute. Negative prior OP complicates interpretation |
| Margin change | Current margin - comparable prior margin | percentage points | Difference of ratio-of-sums. Not relative percentage growth |
| YTD revenue / OP | SUM(monthly value) OVER(PARTITION BY year ORDER BY month ROWS UNBOUNDED PRECEDING) | EUR | Cumulative; not additive across months. Do not sum YTD values |
| Net realized selling price | SUM(net revenue)/NULLIF(SUM(units shipped),0) | EUR/unit | Weighted ratio. After discounts; not list price |
| COGS per shipped unit | SUM(COGS)/NULLIF(SUM(shipped units),0) | EUR/unit | Weighted ratio. Reflects inventory cost and sales mix, not current production unit cost |
| Manufacturing cost | SUM(purchase material + inbound + labor + energy + overhead) | EUR | Additive. Not sales COGS; do not add landed subtotal or line pools again |
| Manufacturing component share | 100 * component cost / SUM(five components) | % | Recompute within year. All five shares sum to 100 within numerical precision |
| Realized labor rate | SUM(labor_cost_eur)/NULLIF(SUM(labor_hours),0) | EUR/hour | Weighted ratio. Includes activity and support hours; rounding may affect final decimals |
| Realized energy tariff | SUM(energy_cost_eur)/NULLIF(SUM(energy_kwh),0) | EUR/kWh | Weighted ratio. Includes activity plus standby consumption |
| Activity labor intensity | SUM(production_labor_hours)/NULLIF(SUM(attempted_units),0) | hours/attempt | Weighted ratio. Mix-weighted standard activity, not measured worker productivity |
| Activity energy intensity | SUM(activity_energy_kwh)/NULLIF(SUM(attempted_units),0) | kWh/attempt | Weighted ratio. Exclude standby from activity intensity |
| Capacity utilization | 100.0*SUM(attempted units)/NULLIF(SUM(effective capacity),0) | % | Ratio of sums. Not OEE; effective capacity already adjusts nominal capacity |
| Defect rate | 100.0*SUM(defective units)/NULLIF(SUM(attempted units),0) | % | Ratio of sums. Volume and mix affect counts; avoid integer division |
| Good yield | 100.0*SUM(good units)/NULLIF(SUM(attempted units),0) | % | Ratio of sums. Complements defect rate under current units policy |
| Purchase spend | SUM(purchase_value_eur) | EUR | Additive. Receipt purchase-only value; excludes capitalized freight |
| Receipt OTD | 100*COUNT(on-time receipts)/NULLIF(COUNT(receipt_id),0) | % | Ratio of receipt counts. Receipt-based; expected dates, not customer delivery promises |
| Supplier target gap | Observed OTD percent - 100*on_time_delivery_target | percentage points | Recompute. Target stored as fraction 0..1 |
| Lead time | AVG(receipt_date-order_date) | days | Receipt-count weighted average. Calendar days, not business days or lead-time variance |
| Weighted purchase price | SUM(purchase value)/NULLIF(SUM(received kg),0) | EUR/kg | Weighted ratio. Year uses receipt_date; supplier/mix changes can influence price |
| Closing inventory value | SUM(closing_value_eur) at one selected month | EUR | Semi-additive across entities; not time. No WIP; avoid SUM across month-end snapshots |
| Average inventory midpoint | AVG((monthly opening EUR+monthly closing EUR)/2) after entity aggregation | EUR | Time-average approximation. Not exact daily average; 2024 zero FG opening creates startup bias |
| FG turnover | Annual COGS / NULLIF(average FG midpoint,0) | turns/year | Ratio of annual flow to average stock. Not annualized for partial periods |
| Raw turnover | Annual landed issues / NULLIF(average raw midpoint,0) | turns/year | Ratio of flow to average stock. Landed issues numerator, not company COGS |
| Combined inventory turns | Annual COGS / NULLIF(avg raw+avg FG,0) | turns/year | Ratio of annual flow to average stock. Current scope excludes WIP |
| Inventory days proxy | Calendar days*(avg raw+avg FG)/NULLIF(annual COGS,0) | days | Ratio. 366 days in 2024, 365 in 2025; not cash conversion cycle |
| Customer revenue share | 100*customer revenue/NULLIF(company revenue,0) | % | Recompute within year. Revenue from the same population and time context |
| Top-N concentration | 100*SUM(customer revenue ranked 1..N)/NULLIF(company revenue,0) | % | Recompute. ROW_NUMBER ties resolved by customer_id; N=1,5,10 |
| Customer HHI | SUM(customer percentage share squared) | 0..10000 | Recompute. Describes synthetic customer book; no antitrust thresholds inferred |
| Outbound cost per shipped unit | SUM(outbound freight)/NULLIF(SUM(shipped units),0) | EUR/unit | Weighted ratio. Shipment activity, not requested units |
| Outbound revenue burden | 100*SUM(outbound freight)/NULLIF(SUM(net revenue),0) | % | Ratio of sums. Distribution expense outside manufacturing gross profit |
| Inbound freight recognition bridge | Receipts freight - recognized inbound COGS - raw freight stock change - FG freight stock change - inbound abnormal losses | EUR | Independent annual source aggregates. Opening balances explain receipts versus COGS differences; outbound excluded |

## Future Power BI use

Dimensions should filter facts in a single direction. Define margins with DIVIDE(SUM(profit), SUM(revenue)); preserve BLANK when undefined. Use an explicit selected month-end for snapshot measures. Keep company opex unallocated unless a policy is approved. Do not sum annual and combined period rows or YTD values. Material COGS is purchase-only; legacy landed material_cost_eur already contains inbound freight. Use five components exactly once. No new DAX, What-if scenario or PBIX change is included.

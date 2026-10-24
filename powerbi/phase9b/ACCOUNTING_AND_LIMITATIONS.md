# Accounting treatment and scope of scenario results

## Baseline ownership

Historical material receipts separate purchase-only value from inbound freight. Both are capitalized in landed raw-material inventory, issued at monthly weighted average, and passed into five-component finished-goods inventory. Sales recognize the purchase-material, inbound, labor, energy and overhead COGS components. Outbound freight is expensed from shipped units below gross profit. Selling/admin belong to operating_expenses; variable selling follows net revenue. Idle line costs and fully defective production losses are expensed separately below GP under the existing approved policy.

The source valuation, all cost components, prices, quantities and accounting assumptions remain unchanged. Scenario totals are analytical sensitivities layered over recognized historical costs. Source inventory is neither written nor revalued. We do not claim that scenario income statements plus unchanged stock values form a rebuilt counterfactual ledger or balance sheet.

## Six independent effects

1. **Selling price:** scales historical net revenue at fixed shipped volume and unchanged discount percentages. Fixed selling/admin stay fixed; historical revenue-variable selling is scaled by the same factor. It is not a demand/elasticity model and does not regenerate price/discount rows or rounded monthly commissions.
2. **Purchase materials:** scales only purchase-material sales COGS. Freight is separate. This models the exposure of costs already recognized, including costs originally carried through inventory; it is not the immediate expense of a new purchase-price increase.
3. **Inbound freight:** scales only the inbound component recognized in sales COGS. Receipt freight, inventory additions/closures and operating expenses are not charged again. Actual inventories retain approved values.
4. **Outbound freight:** scales the historical shipment distribution expense, holding units fixed. It affects OP, not manufacturing COGS or GP.
5. **Direct labor:** scales direct production-labor COGS exposure only, using the decomposition below. Support labor is unchanged. Idle/abnormal expenses are held at the approved baseline; these are zero in the actual data. This is not a staffing or flexible-budget recalculation.
6. **Energy:** scales recognized energy COGS, including its historical activity/standby mixture. It does not change kWh, utilization, overhead or separately expensed pools. It is not a new production-energy ledger.

Scenario Manufacturing COGS = changed purchase materials + changed inbound + baseline labor + direct-labor incremental exposure + changed energy + unchanged overhead. Direct labor is already part of baseline labor: never add its full amount again. Support exposure is an explanatory remainder, not a sixth COGS component.

Scenario Operating Expenses = Scenario Selling + unchanged Administration, matching the scope of operating_expenses.csv. Outbound freight and separately expensed production costs are excluded from this subtotal and deducted separately once. Scenario OP = Scenario GP − Scenario Outbound − Scenario Operating Expenses − separately expensed production costs. This definition prevents aliases/subtotals being added to their parts.

## Why direct labor needed a model-only decomposition

Phase 9A labor_cogs_eur includes production and support labor; its original parameter scaled both. The approved policy explicitly says not to label the whole pool direct labor. Existing batch allocations distinguish production_labor_cost_eur from support_labor_cost_eur, but finished-goods and sales exports preserve only their combined labor component. We therefore derive an **analytical** direct/support split without changing any booked labor COGS.

For each product/month:

- Require zero opening FG labor at the start of available history (verified in this dataset); reject unknown initial lineage instead of inventing a split.
- Carry prior direct/support closing values into opening. Add direct production labor from capitalized batches; fully defective batches add zero to inventory. Support additions are the capitalized labor remainder.
- Split authoritative monthly labor COGS between available direct/support values proportionally. Integer-cent largest-remainder allocation preserves the existing monthly amount; direct wins an exact remainder tie. This is consistent with shared monthly weighted-average valuation, not FIFO or a latest-production-only ratio.
- Carry the two closing remainders forward. Require nonnegative values, consecutive months, exact opening/addition/COGS/closing conservation and agreement with total labor values.
- Split the monthly direct COGS total among sales rows using their already-booked labor COGS as weights; largest remainders tie by sales_line_id. Support on each sale is its booked labor less assigned direct exposure. Thus every row/month/company and customer slice preserves booked total labor.

The SQL recursive CTE and independent Python integer algorithm agree for all 480 product/month ledgers and 2,596 sales rows. They return two derived FactSales columns, not new PostgreSQL/CSV fields. The replacement M query checks source validity and stops refresh if reconstruction fails. Full history is required: filtering to only a later year before reconstruction would lose opening lineage. This allocation is a reproducible analytical attribution, not a claim to uniquely observed direct-labor tracing inside historical finished goods.

## Interpretation and numerical precision

The reference calculator uses exact integer cents for attribution and Decimal precision 48 for sensitivities. Scenario effects can have fractional cents; retain unrounded calculations and round only final presentation. Independently rounded scenario totals and independently rounded deltas can differ by one cent at a half-cent tie; the full-precision JSON/CSV is the reference. Do not force extra cent adjustments into the accounting baseline.

Power BI percentages are fractions; the reference report percentages use 0–100 units. Convert consistently. Percentage profit change is (scenario−base)/base and is BLANK/undefined at zero base profit. With a negative base profit its sign can be counterintuitive; display absolute change alongside it and do not infer improvement solely from the percentage sign.

These scenarios do not model purchasing timing, replenishment, cost lag, demand response, capacity, overtime, working capital, cash flow, tax, WIP or supplier/material-specific sales lineage. They are historical, static-volume sensitivity, not a forward-looking forecast. A future prospective model needs approved new assumptions and development; no such claim is made here.

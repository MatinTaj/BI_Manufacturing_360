# Exact DAX measure library

Create in numbered order. All measures use FactSales as home table and the supplied display folders. This is metadata organization, not an indication that every measure aggregates sales. Percent measures return 0–1 fractions, unlike SQL 0–100 percentages. Optional measures require six disconnected parameter tables. **No DAX engine has executed this library.**

## 1. Complete Month Context

```dax
Complete Month Context =
VAR VisibleDays = COUNTROWS(VALUES('DimDate'[Date]))
VAR ExpectedDays = SUMX(VALUES('DimDate'[MonthStart]), DAY(EOMONTH('DimDate'[MonthStart], 0)))
RETURN VisibleDays > 0 && VisibleDays = ExpectedDays
```

**Definition:** True only when the selected calendar context contains every day in each visible month.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`.

**Dependencies / creation order:** none.

**Filter behavior:** Calendar only.

**Validation method:** True for year/month slicers; false for a single day in a multi-day month.

**Format / folder:** `General` / 00 Controls.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 2. Company Context Valid

```dax
Company Context Valid =
[Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimLine') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier'))
```

**Definition:** Company-only financial scope; prevents presenting shared costs as allocated segment profit.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Only Date filters are valid; every entity dimension filter returns false. Hide fact attributes to prevent unsupported direct-fact filtering.

**Validation method:** False after selecting any product, customer, line, material or supplier.

**Format / folder:** `General` / 00 Controls.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 3. Net Revenue

```dax
Net Revenue =
IF([Complete Month Context], SUM('FactSales'[net_revenue_eur]))
```

**Definition:** Net sales revenue after discounts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 01 Sales.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 4. Gross Sales

```dax
Gross Sales =
IF([Complete Month Context], SUM('FactSales'[gross_revenue_eur]))
```

**Definition:** Sales before discounts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[gross_revenue_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 01 Sales.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 5. Sales Discounts

```dax
Sales Discounts =
IF([Complete Month Context], SUM('FactSales'[discount_amount_eur]))
```

**Definition:** Discount deductions; positive values.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[discount_amount_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 01 Sales.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 6. Shipped Units

```dax
Shipped Units =
IF([Complete Month Context], SUM('FactSales'[units_shipped]))
```

**Definition:** Actual shipped volume.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[units_shipped]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 01 Sales.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 7. Requested Units

```dax
Requested Units =
IF([Complete Month Context], SUM('FactSales'[requested_units]))
```

**Definition:** Requested demand.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[requested_units]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 01 Sales.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 8. Unfulfilled Units

```dax
Unfulfilled Units =
IF([Complete Month Context], SUM('FactSales'[unfulfilled_units]))
```

**Definition:** Requested units not shipped.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[unfulfilled_units]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 01 Sales.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 9. Net Realized Price

```dax
Net Realized Price =
DIVIDE([Net Revenue], [Shipped Units])
```

**Definition:** Weighted realized selling price after discounts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`, `FactSales[units_shipped]`.

**Dependencies / creation order:** Net Revenue, Shipped Units.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 01 Sales.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 10. Revenue Prior Year

```dax
Revenue Prior Year =
CALCULATE([Net Revenue], DATEADD('DimDate'[Date], -1, YEAR))
```

**Definition:** Revenue in the corresponding prior calendar period.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`.

**Dependencies / creation order:** Net Revenue.

**Filter behavior:** Shifts Date by one year; retains entity filters. Initial-year result is BLANK.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 01 Sales.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 11. Revenue YoY %

```dax
Revenue YoY % =
DIVIDE([Net Revenue] - [Revenue Prior Year], [Revenue Prior Year])
```

**Definition:** Relative revenue growth; fraction formatted as percent.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`.

**Dependencies / creation order:** Net Revenue, Revenue Prior Year.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 01 Sales.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 12. Revenue YTD

```dax
Revenue YTD =
TOTALYTD([Net Revenue], 'DimDate'[Date])
```

**Definition:** Calendar-year running revenue.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`.

**Dependencies / creation order:** Net Revenue.

**Filter behavior:** Runs January through current month; keep one year per chart series.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 01 Sales.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 13. Material COGS

```dax
Material COGS =
IF([Complete Month Context], SUM('FactSales'[material_cogs_eur]))
```

**Definition:** Recognized sales COGS component; purchase-material COGS excludes inbound freight.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[material_cogs_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 14. Inbound Freight COGS

```dax
Inbound Freight COGS =
IF([Complete Month Context], SUM('FactSales'[inbound_freight_cogs_eur]))
```

**Definition:** Recognized sales COGS component; purchase-material COGS excludes inbound freight.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[inbound_freight_cogs_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 15. Labor COGS

```dax
Labor COGS =
IF([Complete Month Context], SUM('FactSales'[labor_cogs_eur]))
```

**Definition:** Recognized sales COGS component; purchase-material COGS excludes inbound freight.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[labor_cogs_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 16. Energy COGS

```dax
Energy COGS =
IF([Complete Month Context], SUM('FactSales'[energy_cogs_eur]))
```

**Definition:** Recognized sales COGS component; purchase-material COGS excludes inbound freight.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[energy_cogs_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 17. Overhead COGS

```dax
Overhead COGS =
IF([Complete Month Context], SUM('FactSales'[overhead_cogs_eur]))
```

**Definition:** Recognized sales COGS component; purchase-material COGS excludes inbound freight.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 18. Manufacturing COGS

```dax
Manufacturing COGS =
IF([Complete Month Context] && COUNTROWS('FactSales') > 0, [Material COGS] + [Inbound Freight COGS] + [Labor COGS] + [Energy COGS] + [Overhead COGS])
```

**Definition:** Sum of five authoritative COGS components.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Complete Month Context, Energy COGS, Inbound Freight COGS, Labor COGS, Material COGS, Overhead COGS.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 19. COGS per Shipped Unit

```dax
COGS per Shipped Unit =
DIVIDE([Manufacturing COGS], [Shipped Units])
```

**Definition:** Weighted recognized inventory cost per shipped unit.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[overhead_cogs_eur]`, `FactSales[units_shipped]`.

**Dependencies / creation order:** Manufacturing COGS, Shipped Units.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 20. Gross Profit

```dax
Gross Profit =
[Net Revenue] - [Manufacturing COGS]
```

**Definition:** Revenue less manufacturing COGS.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Manufacturing COGS, Net Revenue.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 21. Gross Margin %

```dax
Gross Margin % =
DIVIDE([Gross Profit], [Net Revenue])
```

**Definition:** Manufacturing gross profit divided by net revenue.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Gross Profit, Net Revenue.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 22. Outbound Freight

```dax
Outbound Freight =
IF([Complete Month Context], SUM('FactSales'[outbound_freight_eur]))
```

**Definition:** Shipment distribution expense below gross profit.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[outbound_freight_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/08_logistics_distribution.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 09 Logistics.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 23. Contribution after Outbound

```dax
Contribution after Outbound =
[Gross Profit] - [Outbound Freight]
```

**Definition:** Product/customer contribution before shared company costs.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Gross Profit, Outbound Freight.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 24. Contribution Margin %

```dax
Contribution Margin % =
DIVIDE([Contribution after Outbound], [Net Revenue])
```

**Definition:** Contribution after outbound freight divided by revenue.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Contribution after Outbound, Net Revenue.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 25. Product Gross Profit Rank

```dax
Product Gross Profit Rank =
IF(HASONEVALUE('DimProduct'[product_id]), RANKX(ALLSELECTED('DimProduct'), [Gross Profit], , DESC, DENSE))
```

**Definition:** Dense gross profit rank within externally selected product cohort.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `DimProduct[product_id]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Gross Profit.

**Filter behavior:** Date/other dimensions retained; external product selections define comparison cohort.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/02_product_profitability.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 02 Profitability.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 26. Selling Expenses

```dax
Selling Expenses =
IF([Company Context Valid], CALCULATE(SUM('FactOpex'[amount_eur]), 'FactOpex'[expense_category] = "selling"))
```

**Definition:** Approved company operating expense category.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`.

**Dependencies / creation order:** Company Context Valid.

**Filter behavior:** Company-only, Date context. BLANK for segment/entity filters.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 27. Administrative Expenses

```dax
Administrative Expenses =
IF([Company Context Valid], CALCULATE(SUM('FactOpex'[amount_eur]), 'FactOpex'[expense_category] = "administration"))
```

**Definition:** Approved company operating expense category.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`.

**Dependencies / creation order:** Company Context Valid.

**Filter behavior:** Company-only, Date context. BLANK for segment/entity filters.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 28. Fixed Selling Expenses

```dax
Fixed Selling Expenses =
IF([Company Context Valid], CALCULATE(SUM('FactOpex'[fixed_amount_eur]), 'FactOpex'[expense_category] = "selling"))
```

**Definition:** Fixed selling expense resource baseline.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`.

**Dependencies / creation order:** Company Context Valid.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 29. Variable Selling Expenses

```dax
Variable Selling Expenses =
IF([Company Context Valid], CALCULATE(SUM('FactOpex'[variable_amount_eur]), 'FactOpex'[expense_category] = "selling"))
```

**Definition:** Revenue-variable selling expense.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactOpex[expense_category]`, `FactOpex[variable_amount_eur]`.

**Dependencies / creation order:** Company Context Valid.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 30. Idle Production Costs

```dax
Idle Production Costs =
IF([Company Context Valid], SUM('FactConversion'[idle_cost_eur]))
```

**Definition:** Separately expensed idle line pools.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`.

**Dependencies / creation order:** Company Context Valid.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 31. Abnormal Production Losses

```dax
Abnormal Production Losses =
IF([Complete Month Context], SUM('FactManufacturing'[production_loss_expense_eur]))
```

**Definition:** Fully defective batch costs, separately expensed.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[production_loss_expense_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 32. Separately Expensed Production Costs

```dax
Separately Expensed Production Costs =
IF([Company Context Valid], [Idle Production Costs] + [Abnormal Production Losses])
```

**Definition:** Idle line costs plus fully defective production losses, once.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`.

**Dependencies / creation order:** Abnormal Production Losses, Company Context Valid, Idle Production Costs.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 33. Operating Profit

```dax
Operating Profit =
IF([Company Context Valid], [Gross Profit] - [Outbound Freight] - [Selling Expenses] - [Administrative Expenses] - [Separately Expensed Production Costs])
```

**Definition:** Approved company operating profit.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Administrative Expenses, Company Context Valid, Gross Profit, Outbound Freight, Selling Expenses, Separately Expensed Production Costs.

**Filter behavior:** Date only. BLANK under any entity dimension filter; use contribution for product/customer analysis.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 34. Operating Margin %

```dax
Operating Margin % =
DIVIDE([Operating Profit], IF([Company Context Valid], [Net Revenue]))
```

**Definition:** Company operating profit as a share of revenue.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Company Context Valid, Net Revenue, Operating Profit.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 35. Operating Profit Prior Year

```dax
Operating Profit Prior Year =
CALCULATE([Operating Profit], DATEADD('DimDate'[Date], -1, YEAR))
```

**Definition:** Comparable prior-year company operating profit.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Operating Profit.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 36. Operating Profit YoY %

```dax
Operating Profit YoY % =
DIVIDE([Operating Profit] - [Operating Profit Prior Year], [Operating Profit Prior Year])
```

**Definition:** Relative operating profit growth.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Operating Profit, Operating Profit Prior Year.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 37. Operating Margin Change pp

```dax
Operating Margin Change pp =
VAR Prior = CALCULATE([Operating Margin %], DATEADD('DimDate'[Date], -1, YEAR))
RETURN IF(NOT ISBLANK(Prior) && NOT ISBLANK([Operating Margin %]), 100 * ([Operating Margin %] - Prior))
```

**Definition:** Change in operating margin in percentage points.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Operating Margin %.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Initial-year result should be BLANK; prior-year BLANK guard must prevent a fabricated change. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00 "pp"` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 38. Operating Profit YTD

```dax
Operating Profit YTD =
TOTALYTD([Operating Profit], 'DimDate'[Date])
```

**Definition:** Calendar-year company operating profit running total.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Operating Profit.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/01_executive_financial.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 03 Company P&L.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 39. Attempted Units

```dax
Attempted Units =
IF([Complete Month Context], SUM('FactProduction'[attempted_units]))
```

**Definition:** Production volume; defects included in attempted units.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactProduction[attempted_units]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/04_production_efficiency.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 04 Production.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 40. Good Units

```dax
Good Units =
IF([Complete Month Context], SUM('FactProduction'[good_units]))
```

**Definition:** Production volume; defects included in attempted units.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactProduction[good_units]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/04_production_efficiency.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 04 Production.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 41. Defective Units

```dax
Defective Units =
IF([Complete Month Context], SUM('FactProduction'[defective_units]))
```

**Definition:** Production volume; defects included in attempted units.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactProduction[defective_units]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/04_production_efficiency.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 04 Production.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 42. Effective Capacity Units

```dax
Effective Capacity Units =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUM('FactCapacity'[effective_capacity_units]))
```

**Definition:** Line/month available capacity, not repeated by product.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactCapacity[effective_capacity_units]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/04_production_efficiency.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 04 Production.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 43. Capacity Utilization %

```dax
Capacity Utilization % =
DIVIDE([Attempted Units], [Effective Capacity Units])
```

**Definition:** Attempted units / effective line capacity; not OEE.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactCapacity[effective_capacity_units]`, `FactProduction[attempted_units]`.

**Dependencies / creation order:** Attempted Units, Effective Capacity Units.

**Filter behavior:** Date and Line only for meaningful utilization; denominator is BLANK for product/customer/material/supplier filters.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/04_production_efficiency.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 04 Production.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 44. Defect Rate %

```dax
Defect Rate % =
DIVIDE([Defective Units], [Attempted Units])
```

**Definition:** Ratio of total defects to attempted volume.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactProduction[attempted_units]`, `FactProduction[defective_units]`.

**Dependencies / creation order:** Attempted Units, Defective Units.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/04_production_efficiency.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 04 Production.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 45. Good Yield %

```dax
Good Yield % =
DIVIDE([Good Units], [Attempted Units])
```

**Definition:** Good output / attempted output.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactProduction[attempted_units]`, `FactProduction[good_units]`.

**Dependencies / creation order:** Attempted Units, Good Units.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/04_production_efficiency.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 04 Production.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 46. Purchase Material Manufacturing Cost

```dax
Purchase Material Manufacturing Cost =
IF([Complete Month Context], SUM('FactManufacturing'[purchase_material_cost_eur]))
```

**Definition:** Production cost allocation component or capitalized aggregate; never add pools again.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[purchase_material_cost_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 47. Inbound Manufacturing Cost

```dax
Inbound Manufacturing Cost =
IF([Complete Month Context], SUM('FactManufacturing'[inbound_freight_cost_eur]))
```

**Definition:** Production cost allocation component or capitalized aggregate; never add pools again.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[inbound_freight_cost_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 48. Manufacturing Labor Cost

```dax
Manufacturing Labor Cost =
IF([Complete Month Context], SUM('FactManufacturing'[labor_cost_eur]))
```

**Definition:** Production cost allocation component or capitalized aggregate; never add pools again.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[labor_cost_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 49. Manufacturing Energy Cost

```dax
Manufacturing Energy Cost =
IF([Complete Month Context], SUM('FactManufacturing'[energy_cost_eur]))
```

**Definition:** Production cost allocation component or capitalized aggregate; never add pools again.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[energy_cost_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 50. Manufacturing Overhead Cost

```dax
Manufacturing Overhead Cost =
IF([Complete Month Context], SUM('FactManufacturing'[manufacturing_overhead_eur]))
```

**Definition:** Production cost allocation component or capitalized aggregate; never add pools again.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[manufacturing_overhead_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 51. Capitalized Production Cost

```dax
Capitalized Production Cost =
IF([Complete Month Context], SUM('FactManufacturing'[capitalized_production_cost_eur]))
```

**Definition:** Production cost allocation component or capitalized aggregate; never add pools again.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[capitalized_production_cost_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 52. Total Manufacturing Cost

```dax
Total Manufacturing Cost =
[Purchase Material Manufacturing Cost] + [Inbound Manufacturing Cost] + [Manufacturing Labor Cost] + [Manufacturing Energy Cost] + [Manufacturing Overhead Cost]
```

**Definition:** Five-component production cost incurred.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[energy_cost_eur]`, `FactManufacturing[inbound_freight_cost_eur]`, `FactManufacturing[labor_cost_eur]`, `FactManufacturing[manufacturing_overhead_eur]`, `FactManufacturing[purchase_material_cost_eur]`.

**Dependencies / creation order:** Inbound Manufacturing Cost, Manufacturing Energy Cost, Manufacturing Labor Cost, Manufacturing Overhead Cost, Purchase Material Manufacturing Cost.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 53. Material Manufacturing Share %

```dax
Material Manufacturing Share % =
DIVIDE([Purchase Material Manufacturing Cost], [Total Manufacturing Cost])
```

**Definition:** Component share of production cost, not sales COGS.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[energy_cost_eur]`, `FactManufacturing[inbound_freight_cost_eur]`, `FactManufacturing[labor_cost_eur]`, `FactManufacturing[manufacturing_overhead_eur]`, `FactManufacturing[purchase_material_cost_eur]`.

**Dependencies / creation order:** Purchase Material Manufacturing Cost, Total Manufacturing Cost.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 54. Inbound Manufacturing Share %

```dax
Inbound Manufacturing Share % =
DIVIDE([Inbound Manufacturing Cost], [Total Manufacturing Cost])
```

**Definition:** Component share of production cost, not sales COGS.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[energy_cost_eur]`, `FactManufacturing[inbound_freight_cost_eur]`, `FactManufacturing[labor_cost_eur]`, `FactManufacturing[manufacturing_overhead_eur]`, `FactManufacturing[purchase_material_cost_eur]`.

**Dependencies / creation order:** Inbound Manufacturing Cost, Total Manufacturing Cost.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 55. Labor Manufacturing Share %

```dax
Labor Manufacturing Share % =
DIVIDE([Manufacturing Labor Cost], [Total Manufacturing Cost])
```

**Definition:** Component share of production cost, not sales COGS.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[energy_cost_eur]`, `FactManufacturing[inbound_freight_cost_eur]`, `FactManufacturing[labor_cost_eur]`, `FactManufacturing[manufacturing_overhead_eur]`, `FactManufacturing[purchase_material_cost_eur]`.

**Dependencies / creation order:** Manufacturing Labor Cost, Total Manufacturing Cost.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 56. Energy Manufacturing Share %

```dax
Energy Manufacturing Share % =
DIVIDE([Manufacturing Energy Cost], [Total Manufacturing Cost])
```

**Definition:** Component share of production cost, not sales COGS.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[energy_cost_eur]`, `FactManufacturing[inbound_freight_cost_eur]`, `FactManufacturing[labor_cost_eur]`, `FactManufacturing[manufacturing_overhead_eur]`, `FactManufacturing[purchase_material_cost_eur]`.

**Dependencies / creation order:** Manufacturing Energy Cost, Total Manufacturing Cost.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 57. Overhead Manufacturing Share %

```dax
Overhead Manufacturing Share % =
DIVIDE([Manufacturing Overhead Cost], [Total Manufacturing Cost])
```

**Definition:** Component share of production cost, not sales COGS.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[energy_cost_eur]`, `FactManufacturing[inbound_freight_cost_eur]`, `FactManufacturing[labor_cost_eur]`, `FactManufacturing[manufacturing_overhead_eur]`, `FactManufacturing[purchase_material_cost_eur]`.

**Dependencies / creation order:** Manufacturing Overhead Cost, Total Manufacturing Cost.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 58. Pool Labor Cost

```dax
Pool Labor Cost =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUM('FactConversion'[labor_cost_eur]))
```

**Definition:** Line-level cost pool activity; independent from product allocation facts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[labor_cost_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 59. Pool Energy Cost

```dax
Pool Energy Cost =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUM('FactConversion'[energy_cost_eur]))
```

**Definition:** Line-level cost pool activity; independent from product allocation facts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[energy_cost_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 60. Labor Hours

```dax
Labor Hours =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUM('FactConversion'[labor_hours]))
```

**Definition:** Line-level cost pool activity; independent from product allocation facts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[labor_hours]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 61. Activity Labor Hours

```dax
Activity Labor Hours =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUM('FactConversion'[production_labor_hours]))
```

**Definition:** Line-level cost pool activity; independent from product allocation facts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[production_labor_hours]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 62. Support Labor Hours

```dax
Support Labor Hours =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUM('FactConversion'[support_labor_hours]))
```

**Definition:** Line-level cost pool activity; independent from product allocation facts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[support_labor_hours]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 63. Energy kWh

```dax
Energy kWh =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUM('FactConversion'[energy_kwh]))
```

**Definition:** Line-level cost pool activity; independent from product allocation facts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[energy_kwh]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 64. Activity Energy kWh

```dax
Activity Energy kWh =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUM('FactConversion'[activity_energy_kwh]))
```

**Definition:** Line-level cost pool activity; independent from product allocation facts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[activity_energy_kwh]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 65. Standby Energy kWh

```dax
Standby Energy kWh =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUM('FactConversion'[base_energy_kwh]))
```

**Definition:** Line-level cost pool activity; independent from product allocation facts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[base_energy_kwh]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 66. Realized Labor Rate

```dax
Realized Labor Rate =
DIVIDE([Pool Labor Cost], [Labor Hours])
```

**Definition:** Pool labor cost per total activity/support hour.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[labor_cost_eur]`, `FactConversion[labor_hours]`.

**Dependencies / creation order:** Labor Hours, Pool Labor Cost.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.0000` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 67. Realized Energy Tariff

```dax
Realized Energy Tariff =
DIVIDE([Pool Energy Cost], [Energy kWh])
```

**Definition:** Pool energy cost per total activity/standby kWh.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[energy_cost_eur]`, `FactConversion[energy_kwh]`.

**Dependencies / creation order:** Energy kWh, Pool Energy Cost.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.0000` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 68. Activity Labor per Attempt

```dax
Activity Labor per Attempt =
DIVIDE([Activity Labor Hours], [Attempted Units])
```

**Definition:** Line mix-weighted standard production hours per attempt.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[production_labor_hours]`, `FactProduction[attempted_units]`.

**Dependencies / creation order:** Activity Labor Hours, Attempted Units.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.0000` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 69. Activity Energy per Attempt

```dax
Activity Energy per Attempt =
DIVIDE([Activity Energy kWh], [Attempted Units])
```

**Definition:** Line mix-weighted standard activity kWh per attempt.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[activity_energy_kwh]`, `FactProduction[attempted_units]`.

**Dependencies / creation order:** Activity Energy kWh, Attempted Units.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/03_manufacturing_costs.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.0000` / 05 Manufacturing.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 70. Purchase Spend

```dax
Purchase Spend =
IF([Complete Month Context], SUM('FactReceipts'[purchase_value_eur]))
```

**Definition:** Receipt purchase-only value.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[purchase_value_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 71. Inbound Receipt Freight

```dax
Inbound Receipt Freight =
IF([Complete Month Context], SUM('FactReceipts'[inbound_freight_eur]))
```

**Definition:** Capitalized inbound freight on receipts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[inbound_freight_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 72. Landed Receipt Value

```dax
Landed Receipt Value =
IF([Complete Month Context], SUM('FactReceipts'[landed_receipt_value_eur]))
```

**Definition:** Purchase plus inbound freight, not another additive expense.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[landed_receipt_value_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 73. Received kg

```dax
Received kg =
IF([Complete Month Context], SUM('FactReceipts'[received_kg]))
```

**Definition:** Receipt weight.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[received_kg]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.000` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 74. Receipt Count

```dax
Receipt Count =
IF([Complete Month Context], COUNTROWS('FactReceipts'))
```

**Definition:** Count of observed receipt rows.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 75. On Time Receipts

```dax
On Time Receipts =
IF([Complete Month Context], CALCULATE(COUNTROWS('FactReceipts'), 'FactReceipts'[on_time] = TRUE()))
```

**Definition:** Receipts on or before expected receipt date.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[on_time]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 76. Receipt OTD %

```dax
Receipt OTD % =
DIVIDE([On Time Receipts], [Receipt Count])
```

**Definition:** Receipt-count on-time ratio, BLANK without receipts.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[on_time]`.

**Dependencies / creation order:** On Time Receipts, Receipt Count.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 77. Supplier Target OTD %

```dax
Supplier Target OTD % =
DIVIDE(SUMX(VALUES('DimSupplier'[supplier_id]), [Receipt Count] * CALCULATE(MAX('DimSupplier'[on_time_delivery_target]))), [Receipt Count])
```

**Definition:** Receipt-weighted supplier target fraction; supports aggregated suppliers.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `DimSupplier[on_time_delivery_target]`, `DimSupplier[supplier_id]`.

**Dependencies / creation order:** Receipt Count.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 78. Supplier Target Gap pp

```dax
Supplier Target Gap pp =
IF(NOT ISBLANK([Receipt OTD %]), 100 * ([Receipt OTD %] - [Supplier Target OTD %]))
```

**Definition:** Observed receipt OTD minus weighted target in percentage points.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `DimSupplier[on_time_delivery_target]`, `DimSupplier[supplier_id]`, `FactReceipts[on_time]`.

**Dependencies / creation order:** Receipt OTD %, Supplier Target OTD %.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00 "pp"` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 79. Mean Lead Days

```dax
Mean Lead Days =
IF([Complete Month Context], AVERAGE('FactReceipts'[actual_lead_time_days]))
```

**Definition:** Receipt-count weighted mean calendar lead days.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[actual_lead_time_days]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 80. Mean Late Days

```dax
Mean Late Days =
IF([Complete Month Context], AVERAGEX('FactReceipts', MAX(0, DATEDIFF('FactReceipts'[expected_receipt_date], 'FactReceipts'[receipt_date], DAY))))
```

**Definition:** Mean nonnegative receipt lateness, calendar days.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[expected_receipt_date]`, `FactReceipts[receipt_date]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 81. Weighted Purchase Price

```dax
Weighted Purchase Price =
DIVIDE([Purchase Spend], [Received kg])
```

**Definition:** Purchase-only EUR per received kg.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[purchase_value_eur]`, `FactReceipts[received_kg]`.

**Dependencies / creation order:** Purchase Spend, Received kg.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.0000` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 82. Weighted Landed Price

```dax
Weighted Landed Price =
DIVIDE([Landed Receipt Value], [Received kg])
```

**Definition:** Landed EUR per received kg.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[landed_receipt_value_eur]`, `FactReceipts[received_kg]`.

**Dependencies / creation order:** Landed Receipt Value, Received kg.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.0000` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 83. Supplier Spend Share %

```dax
Supplier Spend Share % =
DIVIDE([Purchase Spend], CALCULATE([Purchase Spend], REMOVEFILTERS('DimSupplier')))
```

**Definition:** Supplier purchase share of the full supplier population; retains material/date context.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactReceipts[purchase_value_eur]`.

**Dependencies / creation order:** Purchase Spend.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 84. Ordered kg

```dax
Ordered kg =
IF([Complete Month Context], SUM('FactPurchaseOrders'[ordered_kg]))
```

**Definition:** Ordered quantity attributed to order month.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactPurchaseOrders[ordered_kg]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.000` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 85. Outstanding Ordered kg

```dax
Outstanding Ordered kg =
IF([Complete Month Context], SUM('FactPurchaseOrders'[outstanding_kg]))
```

**Definition:** Current imported order-line residual, not historical order backlog.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactPurchaseOrders[outstanding_kg]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/05_supplier_procurement.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.000` / 06 Procurement.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 86. Raw Closing Inventory

```dax
Raw Closing Inventory =
VAR PeriodMonth = MAX('DimDate'[MonthStart])
RETURN IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimLine') || ISCROSSFILTERED('DimSupplier')), CALCULATE(SUM('FactRawInventory'[closing_value_eur]), REMOVEFILTERS('DimDate'), TREATAS({PeriodMonth}, 'FactRawInventory'[month_id])))
```

**Definition:** Inventory at the selected last closing / first opening month, not sum of snapshots.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactRawInventory[closing_value_eur]`, `FactRawInventory[month_id]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Raw supports Date/Material; FG supports Date/Product/Line. Unsupported entity filters return BLANK.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 87. Raw Opening Inventory

```dax
Raw Opening Inventory =
VAR PeriodMonth = MIN('DimDate'[MonthStart])
RETURN IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimLine') || ISCROSSFILTERED('DimSupplier')), CALCULATE(SUM('FactRawInventory'[opening_value_eur]), REMOVEFILTERS('DimDate'), TREATAS({PeriodMonth}, 'FactRawInventory'[month_id])))
```

**Definition:** Inventory at the selected last closing / first opening month, not sum of snapshots.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactRawInventory[month_id]`, `FactRawInventory[opening_value_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Raw supports Date/Material; FG supports Date/Product/Line. Unsupported entity filters return BLANK.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 88. Average Raw Inventory

```dax
Average Raw Inventory =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimLine') || ISCROSSFILTERED('DimSupplier')), AVERAGEX(VALUES('DimDate'[MonthStart]), VAR ThisMonth = 'DimDate'[MonthStart] RETURN CALCULATE(DIVIDE(SUM('FactRawInventory'[opening_value_eur]) + SUM('FactRawInventory'[closing_value_eur]), 2), REMOVEFILTERS('DimDate'), TREATAS({ThisMonth}, 'FactRawInventory'[month_id]))))
```

**Definition:** Mean of monthly opening/closing midpoint inventory, at selected entity grain.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactRawInventory[closing_value_eur]`, `FactRawInventory[month_id]`, `FactRawInventory[opening_value_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Equal month weights; partial-month contexts return BLANK. Approximation to daily inventory.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 89. FG Closing Inventory

```dax
FG Closing Inventory =
VAR PeriodMonth = MAX('DimDate'[MonthStart])
RETURN IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), CALCULATE(SUM('FactFGInventory'[closing_value_eur]), REMOVEFILTERS('DimDate'), TREATAS({PeriodMonth}, 'FactFGInventory'[month_id])))
```

**Definition:** Inventory at the selected last closing / first opening month, not sum of snapshots.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactFGInventory[closing_value_eur]`, `FactFGInventory[month_id]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Raw supports Date/Material; FG supports Date/Product/Line. Unsupported entity filters return BLANK.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 90. FG Opening Inventory

```dax
FG Opening Inventory =
VAR PeriodMonth = MIN('DimDate'[MonthStart])
RETURN IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), CALCULATE(SUM('FactFGInventory'[opening_value_eur]), REMOVEFILTERS('DimDate'), TREATAS({PeriodMonth}, 'FactFGInventory'[month_id])))
```

**Definition:** Inventory at the selected last closing / first opening month, not sum of snapshots.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactFGInventory[month_id]`, `FactFGInventory[opening_value_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Raw supports Date/Material; FG supports Date/Product/Line. Unsupported entity filters return BLANK.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 91. Average FG Inventory

```dax
Average FG Inventory =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), AVERAGEX(VALUES('DimDate'[MonthStart]), VAR ThisMonth = 'DimDate'[MonthStart] RETURN CALCULATE(DIVIDE(SUM('FactFGInventory'[opening_value_eur]) + SUM('FactFGInventory'[closing_value_eur]), 2), REMOVEFILTERS('DimDate'), TREATAS({ThisMonth}, 'FactFGInventory'[month_id]))))
```

**Definition:** Mean of monthly opening/closing midpoint inventory, at selected entity grain.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactFGInventory[closing_value_eur]`, `FactFGInventory[month_id]`, `FactFGInventory[opening_value_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Equal month weights; partial-month contexts return BLANK. Approximation to daily inventory.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 92. Landed Raw Issues

```dax
Landed Raw Issues =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimLine') || ISCROSSFILTERED('DimSupplier')), SUM('FactRawInventory'[issued_material_value_eur]))
```

**Definition:** Raw-material issues at landed cost.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactRawInventory[issued_material_value_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 93. Inventory COGS

```dax
Inventory COGS =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUM('FactFGInventory'[cogs_eur]))
```

**Definition:** Finished-goods monthly COGS for inventory ratios.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactFGInventory[cogs_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 94. FG Turnover

```dax
FG Turnover =
IF(HASONEVALUE('DimDate'[Year]) && COUNTROWS(VALUES('DimDate'[MonthStart])) = 12, DIVIDE([Inventory COGS], [Average FG Inventory]))
```

**Definition:** Annual FG COGS divided by mean monthly midpoint FG.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `DimDate[Year]`, `FactFGInventory[closing_value_eur]`, `FactFGInventory[cogs_eur]`, `FactFGInventory[month_id]`, `FactFGInventory[opening_value_eur]`.

**Dependencies / creation order:** Average FG Inventory, Inventory COGS.

**Filter behavior:** Requires 12 complete months in exactly one calendar year. FG supports Product/Line; raw supports Material; combined supports Date only. Returns BLANK for a partial year.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00 "x"` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 95. Raw Turnover

```dax
Raw Turnover =
IF(HASONEVALUE('DimDate'[Year]) && COUNTROWS(VALUES('DimDate'[MonthStart])) = 12, DIVIDE([Landed Raw Issues], [Average Raw Inventory]))
```

**Definition:** Annual landed raw issues divided by mean raw inventory.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `DimDate[Year]`, `FactRawInventory[closing_value_eur]`, `FactRawInventory[issued_material_value_eur]`, `FactRawInventory[month_id]`, `FactRawInventory[opening_value_eur]`.

**Dependencies / creation order:** Average Raw Inventory, Landed Raw Issues.

**Filter behavior:** Requires 12 complete months in exactly one calendar year. FG supports Product/Line; raw supports Material; combined supports Date only. Returns BLANK for a partial year.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00 "x"` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 96. Combined Closing Inventory

```dax
Combined Closing Inventory =
IF([Company Context Valid], [Raw Closing Inventory] + [FG Closing Inventory])
```

**Definition:** Raw plus FG month-end stock; no WIP.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactFGInventory[closing_value_eur]`, `FactFGInventory[month_id]`, `FactRawInventory[closing_value_eur]`, `FactRawInventory[month_id]`.

**Dependencies / creation order:** Company Context Valid, FG Closing Inventory, Raw Closing Inventory.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 97. Combined Average Inventory

```dax
Combined Average Inventory =
IF([Company Context Valid], [Average Raw Inventory] + [Average FG Inventory])
```

**Definition:** Company average raw plus FG inventory.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactFGInventory[closing_value_eur]`, `FactFGInventory[month_id]`, `FactFGInventory[opening_value_eur]`, `FactRawInventory[closing_value_eur]`, `FactRawInventory[month_id]`, `FactRawInventory[opening_value_eur]`.

**Dependencies / creation order:** Average FG Inventory, Average Raw Inventory, Company Context Valid.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 98. Combined Inventory Turnover

```dax
Combined Inventory Turnover =
IF([Company Context Valid] && HASONEVALUE('DimDate'[Year]) && COUNTROWS(VALUES('DimDate'[MonthStart])) = 12, DIVIDE([Manufacturing COGS], [Combined Average Inventory]))
```

**Definition:** Annual COGS / mean combined inventory.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `DimDate[Year]`, `FactFGInventory[closing_value_eur]`, `FactFGInventory[month_id]`, `FactFGInventory[opening_value_eur]`, `FactRawInventory[closing_value_eur]`, `FactRawInventory[month_id]`, `FactRawInventory[opening_value_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Combined Average Inventory, Company Context Valid, Manufacturing COGS.

**Filter behavior:** Requires 12 complete months in exactly one calendar year. FG supports Product/Line; raw supports Material; combined supports Date only. Returns BLANK for a partial year.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00 "x"` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 99. Selected Calendar Days

```dax
Selected Calendar Days =
IF([Complete Month Context], COUNTROWS(VALUES('DimDate'[Date])))
```

**Definition:** Actual days in the selected month periods (366 in 2024).

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 100. Inventory Days Proxy

```dax
Inventory Days Proxy =
IF([Company Context Valid] && HASONEVALUE('DimDate'[Year]) && COUNTROWS(VALUES('DimDate'[MonthStart])) = 12, DIVIDE([Selected Calendar Days] * [Combined Average Inventory], [Manufacturing COGS]))
```

**Definition:** Calendar-day inventory proxy; not cash conversion cycle.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `DimDate[Year]`, `FactFGInventory[closing_value_eur]`, `FactFGInventory[month_id]`, `FactFGInventory[opening_value_eur]`, `FactRawInventory[closing_value_eur]`, `FactRawInventory[month_id]`, `FactRawInventory[opening_value_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Combined Average Inventory, Company Context Valid, Manufacturing COGS, Selected Calendar Days.

**Filter behavior:** Requires 12 complete months in exactly one calendar year. FG supports Product/Line; raw supports Material; combined supports Date only. Returns BLANK for a partial year.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 101. Closing Inventory Change

```dax
Closing Inventory Change =
VAR Prior = CALCULATE([Combined Closing Inventory], DATEADD('DimDate'[Date], -1, MONTH))
RETURN IF(HASONEVALUE('DimDate'[YearMonth]) && NOT ISBLANK(Prior), [Combined Closing Inventory] - Prior)
```

**Definition:** Change between selected monthly close and prior month close.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `DimDate[YearMonth]`, `FactFGInventory[closing_value_eur]`, `FactFGInventory[month_id]`, `FactRawInventory[closing_value_eur]`, `FactRawInventory[month_id]`.

**Dependencies / creation order:** Combined Closing Inventory.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/06_inventory_turnover.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 07 Inventory.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 102. Customer Revenue Share %

```dax
Customer Revenue Share % =
DIVIDE([Net Revenue], CALCULATE([Net Revenue], ALLSELECTED('DimCustomer')))
```

**Definition:** Revenue share within externally selected customer cohort.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`.

**Dependencies / creation order:** Net Revenue.

**Filter behavior:** Retains Date/Product/Line and customer slicers; removes visual customer rows/columns.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/07_customer_concentration.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 08 Customers.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 103. Top 1 Customer Share %

```dax
Top 1 Customer Share % =
VAR Customers = ADDCOLUMNS(ALLSELECTED('DimCustomer'), "__Revenue", CALCULATE([Net Revenue]))
VAR TopCustomers = TOPN(1, Customers, [__Revenue], DESC, 'DimCustomer'[customer_id], ASC)
RETURN DIVIDE(SUMX(TopCustomers, [__Revenue]), SUMX(Customers, [__Revenue]))
```

**Definition:** Top-N share of selected customer revenue; deterministic customer ID ties.

**Required source columns (transitive):** `DimCustomer[customer_id]`, `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`.

**Dependencies / creation order:** Net Revenue.

**Filter behavior:** Externally selected customer cohort; remove customer slicers to match company-wide SQL.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/07_customer_concentration.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 08 Customers.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 104. Top 5 Customer Share %

```dax
Top 5 Customer Share % =
VAR Customers = ADDCOLUMNS(ALLSELECTED('DimCustomer'), "__Revenue", CALCULATE([Net Revenue]))
VAR TopCustomers = TOPN(5, Customers, [__Revenue], DESC, 'DimCustomer'[customer_id], ASC)
RETURN DIVIDE(SUMX(TopCustomers, [__Revenue]), SUMX(Customers, [__Revenue]))
```

**Definition:** Top-N share of selected customer revenue; deterministic customer ID ties.

**Required source columns (transitive):** `DimCustomer[customer_id]`, `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`.

**Dependencies / creation order:** Net Revenue.

**Filter behavior:** Externally selected customer cohort; remove customer slicers to match company-wide SQL.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/07_customer_concentration.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 08 Customers.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 105. Top 10 Customer Share %

```dax
Top 10 Customer Share % =
VAR Customers = ADDCOLUMNS(ALLSELECTED('DimCustomer'), "__Revenue", CALCULATE([Net Revenue]))
VAR TopCustomers = TOPN(10, Customers, [__Revenue], DESC, 'DimCustomer'[customer_id], ASC)
RETURN DIVIDE(SUMX(TopCustomers, [__Revenue]), SUMX(Customers, [__Revenue]))
```

**Definition:** Top-N share of selected customer revenue; deterministic customer ID ties.

**Required source columns (transitive):** `DimCustomer[customer_id]`, `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`.

**Dependencies / creation order:** Net Revenue.

**Filter behavior:** Externally selected customer cohort; remove customer slicers to match company-wide SQL.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/07_customer_concentration.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 08 Customers.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 106. Customer HHI

```dax
Customer HHI =
VAR Customers = ADDCOLUMNS(ALLSELECTED('DimCustomer'), "__Revenue", CALCULATE([Net Revenue]))
VAR TotalRevenue = SUMX(Customers, [__Revenue])
RETURN IF(TotalRevenue > 0, SUMX(Customers, POWER(100 * DIVIDE([__Revenue], TotalRevenue), 2)))
```

**Definition:** Sum of squared customer percentage shares, 0–10000 scale.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`.

**Dependencies / creation order:** Net Revenue.

**Filter behavior:** Selected customer cohort; descriptive concentration, not market/antitrust risk.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/07_customer_concentration.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00` / 08 Customers.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 107. Active Customers

```dax
Active Customers =
IF([Complete Month Context], COUNTROWS(FILTER(VALUES('DimCustomer'[customer_id]), [Net Revenue] > 0)))
```

**Definition:** Customers with positive recognized net revenue.

**Required source columns (transitive):** `DimCustomer[customer_id]`, `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`.

**Dependencies / creation order:** Complete Month Context, Net Revenue.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/07_customer_concentration.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0` / 08 Customers.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 108. Outbound per Shipped Unit

```dax
Outbound per Shipped Unit =
DIVIDE([Outbound Freight], [Shipped Units])
```

**Definition:** Weighted outbound distribution EUR/unit.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[outbound_freight_eur]`, `FactSales[units_shipped]`.

**Dependencies / creation order:** Outbound Freight, Shipped Units.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/08_logistics_distribution.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.0000` / 09 Logistics.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 109. Outbound Revenue Burden %

```dax
Outbound Revenue Burden % =
DIVIDE([Outbound Freight], [Net Revenue])
```

**Definition:** Outbound freight expense as share of net revenue.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`.

**Dependencies / creation order:** Net Revenue, Outbound Freight.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/08_logistics_distribution.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `0.00%` / 09 Logistics.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 110. Raw Freight Inventory Change

```dax
Raw Freight Inventory Change =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimProduct') || ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimLine') || ISCROSSFILTERED('DimSupplier')), SUMX('FactRawInventory', 'FactRawInventory'[closing_inbound_freight_value_eur] - 'FactRawInventory'[opening_inbound_freight_value_eur]))
```

**Definition:** Net inbound-freight inventory movement across selected complete months.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactRawInventory[closing_inbound_freight_value_eur]`, `FactRawInventory[opening_inbound_freight_value_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/08_logistics_distribution.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 09 Logistics.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 111. FG Freight Inventory Change

```dax
FG Freight Inventory Change =
IF([Complete Month Context] && NOT(ISCROSSFILTERED('DimCustomer') || ISCROSSFILTERED('DimMaterial') || ISCROSSFILTERED('DimSupplier')), SUMX('FactFGInventory', 'FactFGInventory'[closing_inbound_freight_value_eur] - 'FactFGInventory'[opening_inbound_freight_value_eur]))
```

**Definition:** Net inbound-freight inventory movement across selected complete months.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactFGInventory[closing_inbound_freight_value_eur]`, `FactFGInventory[opening_inbound_freight_value_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/08_logistics_distribution.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 09 Logistics.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 112. Inbound Abnormal Loss

```dax
Inbound Abnormal Loss =
IF([Complete Month Context], SUM('FactManufacturing'[inbound_freight_production_loss_expense_eur]))
```

**Definition:** Inbound component expensed on fully defective batches.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactManufacturing[inbound_freight_production_loss_expense_eur]`.

**Dependencies / creation order:** Complete Month Context.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output. SQL oracle: sql/analytics/08_logistics_distribution.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 09 Logistics.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 113. Inbound Freight Bridge Difference

```dax
Inbound Freight Bridge Difference =
IF([Company Context Valid], [Inbound Receipt Freight] - [Inbound Freight COGS] - [Raw Freight Inventory Change] - [FG Freight Inventory Change] - [Inbound Abnormal Loss])
```

**Definition:** Inbound receipt cost reconciles to COGS, stock changes and separately expensed losses.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactFGInventory[closing_inbound_freight_value_eur]`, `FactFGInventory[opening_inbound_freight_value_eur]`, `FactManufacturing[inbound_freight_production_loss_expense_eur]`, `FactRawInventory[closing_inbound_freight_value_eur]`, `FactRawInventory[opening_inbound_freight_value_eur]`, `FactReceipts[inbound_freight_eur]`, `FactSales[inbound_freight_cogs_eur]`.

**Dependencies / creation order:** Company Context Valid, FG Freight Inventory Change, Inbound Abnormal Loss, Inbound Freight COGS, Inbound Receipt Freight, Raw Freight Inventory Change.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Exactly EUR 0.00 for 2024, 2025 and combined. SQL oracle: sql/analytics/08_logistics_distribution.sql (full-precision outputs in Phase 8C report).

**Format / folder:** `#,0.00` / 09 Logistics.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 114. Daily Shipment Revenue

```dax
Daily Shipment Revenue =
CALCULATE(SUM('FactSales'[net_revenue_eur]), USERELATIONSHIP('DimDate'[Date], 'FactSales'[shipment_date]))
```

**Definition:** Revenue attributed to actual shipment day, not monthly accounting date.

**Required source columns (transitive):** `DimDate[Date]`, `FactSales[net_revenue_eur]`, `FactSales[shipment_date]`.

**Dependencies / creation order:** none.

**Filter behavior:** Daily Date filters; only shipment revenue, not company operating profit.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.00` / 10 Daily Roles.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 115. Daily Received kg

```dax
Daily Received kg =
CALCULATE(SUM('FactReceipts'[received_kg]), USERELATIONSHIP('DimDate'[Date], 'FactReceipts'[receipt_date]))
```

**Definition:** Receipt kg by actual day.

**Required source columns (transitive):** `DimDate[Date]`, `FactReceipts[receipt_date]`, `FactReceipts[received_kg]`.

**Dependencies / creation order:** none.

**Filter behavior:** Daily receipt role overrides ReceiptMonth relationship for this measure.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.000` / 10 Daily Roles.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 116. Daily Ordered kg

```dax
Daily Ordered kg =
CALCULATE(SUM('FactPurchaseOrders'[ordered_kg]), USERELATIONSHIP('DimDate'[Date], 'FactPurchaseOrders'[order_date]))
```

**Definition:** Ordered kg by order day.

**Required source columns (transitive):** `DimDate[Date]`, `FactPurchaseOrders[order_date]`, `FactPurchaseOrders[ordered_kg]`.

**Dependencies / creation order:** none.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.000` / 10 Daily Roles.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 117. Expected Receipt kg

```dax
Expected Receipt kg =
CALCULATE(SUM('FactPurchaseOrders'[ordered_kg]), USERELATIONSHIP('DimDate'[Date], 'FactPurchaseOrders'[expected_receipt_date]))
```

**Definition:** Original ordered kg by expected receipt date; not actual delivery or open backlog.

**Required source columns (transitive):** `DimDate[Date]`, `FactPurchaseOrders[expected_receipt_date]`, `FactPurchaseOrders[ordered_kg]`.

**Dependencies / creation order:** none.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.000` / 10 Daily Roles.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 118. COGS Component Difference

```dax
COGS Component Difference =
IF([Complete Month Context], SUM('FactSales'[cogs_eur]) - [Manufacturing COGS])
```

**Definition:** Imported aggregate COGS less five authoritative components.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[cogs_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[overhead_cogs_eur]`.

**Dependencies / creation order:** Complete Month Context, Manufacturing COGS.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** EUR 0.00 in all month/product/customer slices.

**Format / folder:** `#,0.00` / 11 Validation.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 119. Monthly PnL Revenue Difference

```dax
Monthly PnL Revenue Difference =
IF([Company Context Valid], [Net Revenue] - CALCULATE(SUM('RefMonthlyPnL'[revenue]), TREATAS(VALUES('DimDate'[MonthStart]), 'RefMonthlyPnL'[month_id])))
```

**Definition:** Derived revenue less disconnected SQL monthly reference.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`, `RefMonthlyPnL[month_id]`, `RefMonthlyPnL[revenue]`.

**Dependencies / creation order:** Company Context Valid, Net Revenue.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** EUR 0.00 at month, year and combined company level.

**Format / folder:** `#,0.00` / 11 Validation.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 120. Monthly PnL OP Difference

```dax
Monthly PnL OP Difference =
IF([Company Context Valid], [Operating Profit] - CALCULATE(SUM('RefMonthlyPnL'[operating_profit]), TREATAS(VALUES('DimDate'[MonthStart]), 'RefMonthlyPnL'[month_id])))
```

**Definition:** Derived OP less disconnected SQL monthly reference.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`, `RefMonthlyPnL[month_id]`, `RefMonthlyPnL[operating_profit]`.

**Dependencies / creation order:** Company Context Valid, Operating Profit.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** EUR 0.00 at month, year and combined company level.

**Format / folder:** `#,0.00` / 11 Validation.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 121. Material Change %

```dax
Material Change % =
SELECTEDVALUE('ParamMaterial'[Value], 0)
```

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required source columns (transitive):** `ParamMaterial[Value]`.

**Dependencies / creation order:** none.

**Filter behavior:** Disconnected parameter; does not filter source facts.

**Validation method:** Zero/no selection produces zero change. This is prepared code, not an executed scenario.

**Format / folder:** `0.0%` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 122. Inbound Change %

```dax
Inbound Change % =
SELECTEDVALUE('ParamInbound'[Value], 0)
```

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required source columns (transitive):** `ParamInbound[Value]`.

**Dependencies / creation order:** none.

**Filter behavior:** Disconnected parameter; does not filter source facts.

**Validation method:** Zero/no selection produces zero change. This is prepared code, not an executed scenario.

**Format / folder:** `0.0%` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 123. Outbound Change %

```dax
Outbound Change % =
SELECTEDVALUE('ParamOutbound'[Value], 0)
```

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required source columns (transitive):** `ParamOutbound[Value]`.

**Dependencies / creation order:** none.

**Filter behavior:** Disconnected parameter; does not filter source facts.

**Validation method:** Zero/no selection produces zero change. This is prepared code, not an executed scenario.

**Format / folder:** `0.0%` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 124. Labor Change %

```dax
Labor Change % =
SELECTEDVALUE('ParamLabor'[Value], 0)
```

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required source columns (transitive):** `ParamLabor[Value]`.

**Dependencies / creation order:** none.

**Filter behavior:** Disconnected parameter; does not filter source facts.

**Validation method:** Zero/no selection produces zero change. This is prepared code, not an executed scenario.

**Format / folder:** `0.0%` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 125. Energy Change %

```dax
Energy Change % =
SELECTEDVALUE('ParamEnergy'[Value], 0)
```

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required source columns (transitive):** `ParamEnergy[Value]`.

**Dependencies / creation order:** none.

**Filter behavior:** Disconnected parameter; does not filter source facts.

**Validation method:** Zero/no selection produces zero change. This is prepared code, not an executed scenario.

**Format / folder:** `0.0%` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 126. Price Change %

```dax
Price Change % =
SELECTEDVALUE('ParamPrice'[Value], 0)
```

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required source columns (transitive):** `ParamPrice[Value]`.

**Dependencies / creation order:** none.

**Filter behavior:** Disconnected parameter; does not filter source facts.

**Validation method:** Zero/no selection produces zero change. This is prepared code, not an executed scenario.

**Format / folder:** `0.0%` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 127. Scenario Revenue

```dax
Scenario Revenue =
[Net Revenue] * (1 + [Price Change %])
```

**Definition:** Static volume, discounts unchanged proportionally; hypothetical net price sensitivity.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`, `ParamPrice[Value]`.

**Dependencies / creation order:** Net Revenue, Price Change %.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.00` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 128. Scenario Manufacturing COGS

```dax
Scenario Manufacturing COGS =
[Material COGS] * (1 + [Material Change %]) + [Inbound Freight COGS] * (1 + [Inbound Change %]) + [Labor COGS] * (1 + [Labor Change %]) + [Energy COGS] * (1 + [Energy Change %]) + [Overhead COGS]
```

**Definition:** Independent historical recognized-cost exposure, fixed overhead retained.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`.

**Dependencies / creation order:** Energy COGS, Energy Change %, Inbound Change %, Inbound Freight COGS, Labor COGS, Labor Change %, Material COGS, Material Change %, Overhead COGS.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.00` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 129. Scenario Outbound Freight

```dax
Scenario Outbound Freight =
[Outbound Freight] * (1 + [Outbound Change %])
```

**Definition:** Historical distribution-cost sensitivity at unchanged shipped volume.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[outbound_freight_eur]`, `ParamOutbound[Value]`.

**Dependencies / creation order:** Outbound Change %, Outbound Freight.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.00` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 130. Scenario Gross Profit

```dax
Scenario Gross Profit =
[Scenario Revenue] - [Scenario Manufacturing COGS]
```

**Definition:** Hypothetical gross profit under static activity.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamPrice[Value]`.

**Dependencies / creation order:** Scenario Manufacturing COGS, Scenario Revenue.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.00` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 131. Scenario Selling Expenses

```dax
Scenario Selling Expenses =
IF([Company Context Valid], [Fixed Selling Expenses] + [Variable Selling Expenses] * (1 + [Price Change %]))
```

**Definition:** Fixed selling unchanged; revenue-variable selling scales with net price at fixed volume.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`, `FactOpex[variable_amount_eur]`, `ParamPrice[Value]`.

**Dependencies / creation order:** Company Context Valid, Fixed Selling Expenses, Price Change %, Variable Selling Expenses.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.00` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 132. Scenario Operating Profit

```dax
Scenario Operating Profit =
IF([Company Context Valid], [Scenario Gross Profit] - [Scenario Outbound Freight] - [Scenario Selling Expenses] - [Administrative Expenses] - [Separately Expensed Production Costs])
```

**Definition:** Company-only historical sensitivity; idle and abnormal expense held at baseline.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`, `FactOpex[variable_amount_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamOutbound[Value]`, `ParamPrice[Value]`.

**Dependencies / creation order:** Administrative Expenses, Company Context Valid, Scenario Gross Profit, Scenario Outbound Freight, Scenario Selling Expenses, Separately Expensed Production Costs.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.00` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 133. Scenario Operating Margin %

```dax
Scenario Operating Margin % =
DIVIDE([Scenario Operating Profit], IF([Company Context Valid], [Scenario Revenue]))
```

**Definition:** Hypothetical company operating margin.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`, `FactOpex[variable_amount_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamOutbound[Value]`, `ParamPrice[Value]`.

**Dependencies / creation order:** Company Context Valid, Scenario Operating Profit, Scenario Revenue.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `0.00%` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.

## 134. Scenario OP Change

```dax
Scenario OP Change =
[Scenario Operating Profit] - [Operating Profit]
```

**Definition:** Hypothetical operating profit difference from unchanged baseline.

**Required source columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`, `FactOpex[variable_amount_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamOutbound[Value]`, `ParamPrice[Value]`.

**Dependencies / creation order:** Operating Profit, Scenario Operating Profit.

**Filter behavior:** Respects active dimension relationships and complete calendar-month context.

**Validation method:** Compare the same calendar/entity filter with the corresponding Phase 8C SQL output.

**Format / folder:** `#,0.00` / 12 Optional Sensitivity.

**Execution status:** Pending Power BI Desktop execution; static checks do not establish DAX correctness.


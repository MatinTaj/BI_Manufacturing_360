# Audited scenario DAX library

Reuse the same six parameter tables and all 120 core measures. Replace the fourteen earlier optional formulas by name, adding only eight new measures. All 22 use FactSales as home table and the 12 Historical Sensitivity folder. Formulas were statically audited and their mathematics reference-tested; no DAX engine execution occurred.

## 1. Material Change %

```dax
Material Change % =
SELECTEDVALUE('ParamMaterial'[Value], 0)
```

**Action:** update existing scenario measure.

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required columns (transitive):** `ParamMaterial[Value]`.

**Filters:** Disconnected existing parameter; no/multiple selection means zero.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `0.0%`.

## 2. Inbound Change %

```dax
Inbound Change % =
SELECTEDVALUE('ParamInbound'[Value], 0)
```

**Action:** update existing scenario measure.

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required columns (transitive):** `ParamInbound[Value]`.

**Filters:** Disconnected existing parameter; no/multiple selection means zero.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `0.0%`.

## 3. Outbound Change %

```dax
Outbound Change % =
SELECTEDVALUE('ParamOutbound'[Value], 0)
```

**Action:** update existing scenario measure.

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required columns (transitive):** `ParamOutbound[Value]`.

**Filters:** Disconnected existing parameter; no/multiple selection means zero.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `0.0%`.

## 4. Labor Change %

```dax
Labor Change % =
SELECTEDVALUE('ParamLabor'[Value], 0)
```

**Action:** update existing scenario measure.

**Definition:** Existing independent zero-default parameter. Labor affects direct production-labor exposure only.

**Required columns (transitive):** `ParamLabor[Value]`.

**Filters:** Disconnected existing parameter; no/multiple selection means zero.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `0.0%`.

## 5. Energy Change %

```dax
Energy Change % =
SELECTEDVALUE('ParamEnergy'[Value], 0)
```

**Action:** update existing scenario measure.

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required columns (transitive):** `ParamEnergy[Value]`.

**Filters:** Disconnected existing parameter; no/multiple selection means zero.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `0.0%`.

## 6. Price Change %

```dax
Price Change % =
SELECTEDVALUE('ParamPrice'[Value], 0)
```

**Action:** update existing scenario measure.

**Definition:** Selected independent hypothetical change; BLANK/multiple defaults to zero.

**Required columns (transitive):** `ParamPrice[Value]`.

**Filters:** Disconnected existing parameter; no/multiple selection means zero.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `0.0%`.

## 7. Direct Labor COGS Exposure

```dax
Direct Labor COGS Exposure =
IF([Complete Month Context], SUM('FactSales'[direct_labor_cogs_exposure_eur]))
```

**Action:** add only if absent.

**Definition:** Derived direct production-labor subset of booked labor COGS, reconciled through monthly inventory.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[direct_labor_cogs_exposure_eur]`.

**Filters:** Recognized sales context: complete months and Date/Product/Customer/Line.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 8. Support Labor COGS Exposure

```dax
Support Labor COGS Exposure =
IF([Complete Month Context], SUM('FactSales'[support_labor_cogs_exposure_eur]))
```

**Action:** add only if absent.

**Definition:** Derived support-labor subset of booked labor COGS, unchanged by the direct-labor parameter.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[support_labor_cogs_exposure_eur]`.

**Filters:** Recognized sales context: complete months and Date/Product/Customer/Line.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 9. Labor Exposure Difference

```dax
Labor Exposure Difference =
IF([Complete Month Context], [Labor COGS] - [Direct Labor COGS Exposure] - [Support Labor COGS Exposure])
```

**Action:** add only if absent.

**Definition:** Aggregate labor less analytical parts; zero in every supported slice.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[direct_labor_cogs_exposure_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[support_labor_cogs_exposure_eur]`.

**Filters:** Recognized sales context: complete months and Date/Product/Customer/Line.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 10. Scenario Revenue

```dax
Scenario Revenue =
[Net Revenue] * (1 + [Price Change %])
```

**Action:** update existing scenario measure.

**Definition:** Static shipped units, unchanged discount percentages; proportional net-price change.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[net_revenue_eur]`, `ParamPrice[Value]`.

**Filters:** Recognized sales context: complete months and Date/Product/Customer/Line.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 11. Scenario Manufacturing COGS

```dax
Scenario Manufacturing COGS =
IF([Complete Month Context], [Material COGS] * (1 + [Material Change %]) + [Inbound Freight COGS] * (1 + [Inbound Change %]) + [Labor COGS] + [Direct Labor COGS Exposure] * [Labor Change %] + [Energy COGS] * (1 + [Energy Change %]) + [Overhead COGS])
```

**Action:** update existing scenario measure.

**Definition:** Five recognized COGS components once; only direct labor changes, support and overhead fixed.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[direct_labor_cogs_exposure_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`.

**Filters:** Recognized sales context: complete months and Date/Product/Customer/Line.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 12. Scenario Outbound Freight

```dax
Scenario Outbound Freight =
[Outbound Freight] * (1 + [Outbound Change %])
```

**Action:** update existing scenario measure.

**Definition:** Shipment distribution expense, excluded from manufacturing COGS.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[outbound_freight_eur]`, `ParamOutbound[Value]`.

**Filters:** Recognized sales context: complete months and Date/Product/Customer/Line.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 13. Scenario Gross Profit

```dax
Scenario Gross Profit =
IF([Complete Month Context], [Scenario Revenue] - [Scenario Manufacturing COGS])
```

**Action:** update existing scenario measure.

**Definition:** Hypothetical manufacturing gross profit.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[direct_labor_cogs_exposure_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamPrice[Value]`.

**Filters:** Recognized sales context: complete months and Date/Product/Customer/Line.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 14. Scenario Gross Margin %

```dax
Scenario Gross Margin % =
DIVIDE([Scenario Gross Profit], [Scenario Revenue])
```

**Action:** add only if absent.

**Definition:** Hypothetical gross margin fraction.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[direct_labor_cogs_exposure_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamPrice[Value]`.

**Filters:** Recognized sales context: complete months and Date/Product/Customer/Line.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `0.00%`.

## 15. Scenario Selling Expenses

```dax
Scenario Selling Expenses =
IF([Company Context Valid], [Fixed Selling Expenses] + [Variable Selling Expenses] * (1 + [Price Change %]))
```

**Action:** update existing scenario measure.

**Definition:** Fixed selling unchanged; revenue-variable selling follows price at fixed volume.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`, `FactOpex[variable_amount_eur]`, `ParamPrice[Value]`.

**Filters:** Company Date-only; BLANK under Product/Customer/Line/Material/Supplier filters.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 16. Scenario Operating Expenses

```dax
Scenario Operating Expenses =
IF([Company Context Valid], [Scenario Selling Expenses] + [Administrative Expenses])
```

**Action:** add only if absent.

**Definition:** Selling plus administration, matching operating_expenses.csv; outbound and production losses remain separate.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`, `FactOpex[variable_amount_eur]`, `ParamPrice[Value]`.

**Filters:** Company Date-only; BLANK under Product/Customer/Line/Material/Supplier filters.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 17. Scenario Operating Profit

```dax
Scenario Operating Profit =
IF([Company Context Valid], [Scenario Gross Profit] - [Scenario Outbound Freight] - [Scenario Operating Expenses] - [Separately Expensed Production Costs])
```

**Action:** update existing scenario measure.

**Definition:** Company OP with each deduction recognized once.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`, `FactOpex[variable_amount_eur]`, `FactSales[direct_labor_cogs_exposure_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamOutbound[Value]`, `ParamPrice[Value]`.

**Filters:** Company Date-only; BLANK under Product/Customer/Line/Material/Supplier filters.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 18. Scenario Operating Margin %

```dax
Scenario Operating Margin % =
DIVIDE([Scenario Operating Profit], IF([Company Context Valid], [Scenario Revenue]))
```

**Action:** update existing scenario measure.

**Definition:** Hypothetical company margin fraction.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`, `FactOpex[variable_amount_eur]`, `FactSales[direct_labor_cogs_exposure_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamOutbound[Value]`, `ParamPrice[Value]`.

**Filters:** Company Date-only; BLANK under Product/Customer/Line/Material/Supplier filters.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `0.00%`.

## 19. Scenario GP Change

```dax
Scenario GP Change =
IF([Complete Month Context], [Scenario Gross Profit] - [Gross Profit])
```

**Action:** add only if absent.

**Definition:** Absolute gross profit change from unchanged baseline.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[direct_labor_cogs_exposure_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamPrice[Value]`.

**Filters:** Recognized sales context: complete months and Date/Product/Customer/Line.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 20. Scenario GP Change %

```dax
Scenario GP Change % =
DIVIDE([Scenario GP Change], [Gross Profit])
```

**Action:** add only if absent.

**Definition:** Relative GP change; zero base profit returns BLANK.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactSales[direct_labor_cogs_exposure_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamPrice[Value]`.

**Filters:** Recognized sales context: complete months and Date/Product/Customer/Line.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `0.00%`.

## 21. Scenario OP Change

```dax
Scenario OP Change =
IF([Company Context Valid], [Scenario Operating Profit] - [Operating Profit])
```

**Action:** update existing scenario measure.

**Definition:** Absolute OP change, guarded for company context.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`, `FactOpex[variable_amount_eur]`, `FactSales[direct_labor_cogs_exposure_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamOutbound[Value]`, `ParamPrice[Value]`.

**Filters:** Company Date-only; BLANK under Product/Customer/Line/Material/Supplier filters.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `#,0.00`.

## 22. Scenario OP Change %

```dax
Scenario OP Change % =
DIVIDE([Scenario OP Change], [Operating Profit])
```

**Action:** add only if absent.

**Definition:** Relative OP change; zero base OP returns BLANK.

**Required columns (transitive):** `DimDate[Date]`, `DimDate[MonthStart]`, `FactConversion[idle_cost_eur]`, `FactManufacturing[production_loss_expense_eur]`, `FactOpex[amount_eur]`, `FactOpex[expense_category]`, `FactOpex[fixed_amount_eur]`, `FactOpex[variable_amount_eur]`, `FactSales[direct_labor_cogs_exposure_eur]`, `FactSales[energy_cogs_eur]`, `FactSales[inbound_freight_cogs_eur]`, `FactSales[labor_cogs_eur]`, `FactSales[material_cogs_eur]`, `FactSales[net_revenue_eur]`, `FactSales[outbound_freight_eur]`, `FactSales[overhead_cogs_eur]`, `ParamEnergy[Value]`, `ParamInbound[Value]`, `ParamLabor[Value]`, `ParamMaterial[Value]`, `ParamOutbound[Value]`, `ParamPrice[Value]`.

**Filters:** Company Date-only; BLANK under Product/Customer/Line/Material/Supplier filters.

**Validation:** Compare full-precision reference calculator outputs and supplied Desktop scenario matrix; round only final display.

**Format:** `0.00%`.


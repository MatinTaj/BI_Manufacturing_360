# Power BI implementation guide — Phase 9A handoff

Preparation only. Build a **new** model in Power BI Desktop when separately authorized for Phase 9B. No existing PBIX was opened or changed. All required formulas and queries are supplied; no additional SQL/Python development is required for this defined dashboard scope. Desktop execution is still an acceptance gate.

## 1. Connect securely

1. Open a new report, not powerbi/dash1.pbix. Disable Auto date/time and automatic relationship detection/import of relationships in Options for this file.
2. Get Data → PostgreSQL database. Server: localhost:5432. Database: manufacturing_360. Choose Import. The source has only a few thousand rows and validated monthly snapshots; no requirement justifies DirectQuery complexity.
3. Authenticate through the connector using the existing local account/configuration; verified owner account is postgres. Prefer an administrator-provisioned least-privilege reader for ongoing reporting. Credentials belong in the connector credential store, never M or repository files. Existing pgpass used by psql does not prove Power BI connector authentication will work; test the connector separately.
4. Create Blank Queries in Power Query and paste the matching file into Advanced Editor. Name every query exactly as its filename without .m. There are no credentials inside the scripts. A native-query approval prompt is expected because the supplied queries are SELECT projections.
5. Create pServer, pDatabase and fxRead first; keep them as helpers with load disabled where available. pServer is localhost:5432; pDatabase is manufacturing_360. Changing server location requires only parameter values. A gateway or remote Desktop interprets localhost on its own host; use the actual accessible database host then.

## 2. Query creation order

| Order | Queries |
|---|---|
| 1 | pServer, pDatabase, fxRead |
| 2 | DimDate, DimProduct, DimCustomer, DimMaterial, DimSupplier, DimLine |
| 3 | FactSales, FactProduction, FactManufacturing, FactConversion, FactCapacity |
| 4 | FactReceipts, FactPurchaseOrders, FactRawInventory, FactFGInventory, FactOpex, FactConsumption |
| 5 | RefPnL, RefMonthlyPnL (keep disconnected and hidden) |

Paste each full power_query/*.m file. Do not use Native SQL from the legacy public schema. All projections explicitly target manufacturing_v2. No SQL view creation is needed. Check source row counts against TABLE_MAPPING.csv and live source_checks.json in the preparation report, then Close & Apply. Confirm load is enabled for all nineteen model tables, not for scalar/function helpers.

## 3. Relationships and Date setup

Create exactly the 34 entries in RELATIONSHIPS.csv: 30 active Single 1:* and four inactive Date roles. Do not accept extra auto-generated edges. No dimension connects to another dimension; no fact connects to another fact. RefPnL and RefMonthlyPnL must be disconnected. Verify one-side key uniqueness and absence of an unexpected blank dimension member. Mark DimDate[Date] as the Date table. Build a Year/Quarter/YearMonth hierarchy, sorting YearMonth and MonthName as specified in STAR_SCHEMA.md. Hide the Date day column from casual use on monthly pages; expose it only on the dedicated daily operational page.

## 4. Data types, formats and field hygiene

IDs and reference period are Text; dates are Date, not DateTime. Units/counts are Whole Number. Monetary source values with two decimals use Fixed Decimal Currency where supplied. Display EUR amounts with #,0.00 or EUR #,0.00. kg uses three decimals; hours/kWh/rates use four; weighted-average unit cost source columns retain Decimal Number precision and can display eight decimals. Never blanket-convert an eight-decimal unit cost to Currency. Derived percentage/ratio and aggregated NUMERIC fields may arrive as Decimal Number; the M scripts explicitly preserve financial reference amounts as Currency.

DAX percent measures return fractions and use 0.00%; SQL values like 23.3388 are 0–100 percentages, so divide those references by 100 when comparing directly. Percentage-point measures already multiply fraction differences by 100 and use 0.00 "pp". Turnover uses 0.00 "x". Disable default summation for dimension numeric attributes/rates. Hide technical keys, repeated descriptive columns inside facts, precomputed ratio columns, all fact numeric columns used only by explicit measures, legacy material_cost_eur and overlapping aggregates. Use only dimension fields for slicers and named measures for visuals. Keep FactOpex[expense_category] hidden; the company measures own category filtering.

## 5. Measure creation

DAX_LIBRARY.md contains every exact Name = Formula, required source columns, definition, filters, validation method and format. measures.json is the structured equivalent. Create the 120 core measures in numbered order (00 Controls through 11 Validation); folder ordering follows dependency order except that Outbound Freight is defined early because Profitability depends on it. All measures use FactSales as home table for ease of batch creation; display folders organize business subjects.

Manual option: select FactSales → New measure, paste each individual expression from the library and apply its specified format/display folder. The core_measures.dax file is a DEFINE library for query-scoped tests; pasting the entire DEFINE block into New measure is not valid.

Optional batch option: after all named tables exist in a NEW model, use Tabular Editor Advanced Scripting to paste dax/create_core_measures.csx. It aborts on any existing measure name before creating anything, and does not overwrite. It has not been compiled/executed during preparation. Check dependencies/formats in Desktop after creation. If the external tool is unavailable, the manual formulas are complete. Do not run it against the legacy model.

## 6. Reconciliation before visual design

Run the queries in validation/01_annual_financial.dax through 05_filter_edge_cases.dax in Desktop DAX Query View or an attached DAX Studio session after core measures exist. The .dax files are queries, not calculated tables. If using DAX Studio query-scoped measures, prepend core_measures.dax before one EVALUATE query; persisted measures are easier for normal dashboard work. All financial differences must round to EUR 0.00 and annual baseline percent differences must be within 0.00000001 percentage points. Follow FINANCIAL_VALIDATION.md; do not adjust assumptions or reference values to pass a check.

## 7. Report pages and interactions

| Page | Suggested visuals | Allowed slicers / notes |
|---|---|---|
| Executive P&L | Revenue/GP/OP cards, monthly revenue and OP trend, annual YoY matrix, P&L waterfall | Date Year/YearMonth only; no entity slicer on company OP |
| Product economics | Product GP rank bar, revenue-versus-margin scatter, five-component COGS matrix, contribution table | Date, Product/category, Line, Customer/segment for sales only |
| Manufacturing costs | Stacked component cost by year/line, labor/energy intensity, support vs activity, rates | Date/Line; product allocation detail separate from pool visuals |
| Production | Attempted/good/defect cards, utilization trend, defect rate by line/product | Date/Line for utilization; Product only on quality/volume visuals |
| Procurement | Supplier spend/Pareto, receipt OTD/target, lead-day bars, material price trend | Date means receipt month for receipt KPIs; order month for PO KPIs; Supplier/Material |
| Inventory | Raw/FG closing trends, value by component, annual turnover and days, midpoint stock | Raw: Date/Material; FG: Date/Product/Line; combined: Date only |
| Customers | Top-N revenue share, Pareto table, contribution margin, segment mix | Date and Customer/segment; cohort-sensitive shares clearly labeled |
| Logistics | Outbound EUR/unit by segment, outbound/revenue burden, inbound freight recognition bridge | Date/Customer for outbound; company Date only for bridge |
| Daily operations | Daily Shipment Revenue and daily/expected procurement quantities | Daily Date; no monthly OP or inventory on a day-level axis |
| Data quality | SQL reference differences, source counts, zero checks, unsupported-filter warning | Date; hidden/internal page |
| Optional sensitivity | Base vs scenario GP/OP, change waterfall and six parameter slicers | Company Date; label historical static-volume sensitivity |

Use Edit interactions so slicers do not affect visuals with unsupported grain. Do not synchronize Product/Customer/Line slicers onto the Executive page. Use clear titles that identify actual versus scenario, receipt versus order dates, currency and monthly snapshots. Avoid embedding company OP alongside a product breakdown. Add tooltips for startup inventory bias, uniformly on-time synthetic receipts and absent cost lineage. Provide a reset-filters bookmark and visible reporting period. No report pages or visuals were built in this phase.

## 8. Optional sensitivity preparation

The six disconnected table formulas in dax/optional_tables.dax and fourteen optional measures are ready if wanted later. Create each ParamMaterial/Inbound/Outbound/Labor/Energy/Price table separately, then the optional measures in their supplied order. Do not relate parameters to facts. Format Value as percent, use Single select slicers and save each default at 0%. Multiple/no selection deliberately means zero change. All zero parameters must reproduce the baseline before any nonzero test. This does not change base measures or accounting assumptions. See WHAT_IF_READINESS.md for bounds and limitations.

## 9. Refresh and acceptance

Refresh in Import mode, recheck row counts and all reconciliation queries, then test slicer combinations, totals, BLANK handling and daily roles. SQL execution and static checks are already documented; M connector evaluation, actual relationship filtering, DAX compilation/runtime, optional external tool behavior and refresh still need Desktop testing. Publish/gateway setup, credentials/reader grants and RLS are separate deployment choices. No RLS is invented here. Do not proceed to Phase 9B without explicit authorization.

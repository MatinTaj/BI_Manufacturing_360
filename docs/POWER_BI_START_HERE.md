# POWER BI START HERE — independent Manufacturing 360 handover

This is the single build sequence for continuing without ChatGPT Plus or Codex. Keep this guide, the project folders and the verified reference outputs locally. **The v2 Power BI model/dashboard has not been built or executed yet.** No existing PBIX should be edited as part of these steps.

## 0. Prepare your offline workstation

Required: Windows Power BI Desktop, access to the existing PostgreSQL 18 server/database, project files and a text editor. Python 3.12 is optional for rerunning the independent reference tests; it is not needed to paste M/DAX into Desktop. DAX Studio or Tabular Editor are optional conveniences, not required. Install software/dependencies before disconnecting from the internet. The handover ZIP contains project assets and hashes, not third-party installers or wheels. Local report building needs no AI subscription. Service publishing later needs network access and the appropriate account/workspace permissions.

Unzip into a NEW folder if using the handover archive. Open README.md and verify the 19 data/staging CSVs exist. HANDOVER_MANIFEST.json records file hashes in the archive. Do not overwrite your existing project or delete historical backups. For optional Python verification follow [REPRODUCIBILITY](REPRODUCIBILITY.md), including the missing-pointer bootstrap.

## 1. Verify the database, without changing it

Connection: **localhost:5432**, database **manufacturing_360**, schema **manufacturing_v2**. The verified local account was postgres. Prefer a separately configured reader for routine reporting; no role/grants were created by the project. The reader needs SELECT on all sources used by the supplied native queries, including sales, allocation and inventory tables for the direct-labor reconstruction.

If the schema is already present, do not rerun migration. The read-only model checks are manufacturing_v2.audit_validation_results (36 rows, failed_rows=0) and audit_pnl_reconciliation (33 passed rows). [Reproduction instructions](REPRODUCIBILITY.md) provide exact psql commands and the absent-schema-only import process. Never run the retired root sql/v2 CREATE DATABASE plan, DROP/TRUNCATE or a reset to solve a connection problem.

Power BI does not automatically reuse psql pgpass credentials. Enter credentials in its connection dialog; never paste a password into M, SQL, DAX or a repository file. A remote computer/gateway interprets localhost on itself; use the actual accessible server address there.

## 2. Create a new Import report and connection helpers

1. Open a new blank Power BI report. Do not open/save over the legacy dash1.pbix.
2. Disable Auto date/time for this file and disable automatic relationship detection/import. This prevents ambiguous extra links and accidental reference-table relationships.
3. Use the PostgreSQL connector in Import mode to verify server/database/authentication. Do not import every available table/view from Navigator. The supplied query files define the precise model; a second automatic import creates duplicates.
4. Open Transform data / Power Query Editor. Create Blank Queries, open Advanced Editor and replace the entire expression with each local .m file. Name the query exactly as the filename without .m.
5. First create pServer, pDatabase and fxRead from powerbi/phase9a/power_query/. The first two are scalar values and the third a function; keep helper load disabled where available. No secrets are in these files.
6. Native-query approval prompts are expected for the supplied SELECTs. Review the target manufacturing_v2 and approve only those provided queries. Keep credentials in the connector store.

## 3. Import the Phase 9A model in this order

Create dimensions, then facts, then references using the matching Phase 9A M file. The current row counts below were verified against PostgreSQL. Load is enabled for all nineteen model tables.

| Order | Query name | File | Expected rows | Grain |
|---:|---|---|---:|---|
| 1 | DimDate | powerbi/phase9a/power_query/DimDate.m | 731 | one calendar day, full years |
| 2 | DimProduct | powerbi/phase9a/power_query/DimProduct.m | 20 | one product_id |
| 3 | DimCustomer | powerbi/phase9a/power_query/DimCustomer.m | 25 | one customer_id |
| 4 | DimMaterial | powerbi/phase9a/power_query/DimMaterial.m | 10 | one material_id |
| 5 | DimSupplier | powerbi/phase9a/power_query/DimSupplier.m | 15 | one supplier_id |
| 6 | DimLine | powerbi/phase9a/power_query/DimLine.m | 3 | one line_id |
| 7 | FactSales | powerbi/phase9a/power_query/FactSales.m | 2596 | shipment line |
| 8 | FactProduction | powerbi/phase9a/power_query/FactProduction.m | 480 | product/month batch |
| 9 | FactManufacturing | powerbi/phase9a/power_query/FactManufacturing.m | 480 | production batch allocation |
| 10 | FactConversion | powerbi/phase9a/power_query/FactConversion.m | 72 | line/month cost pool |
| 11 | FactCapacity | powerbi/phase9a/power_query/FactCapacity.m | 72 | line/month capacity |
| 12 | FactReceipts | powerbi/phase9a/power_query/FactReceipts.m | 144 | receipt (one complete receipt per PO line) |
| 13 | FactPurchaseOrders | powerbi/phase9a/power_query/FactPurchaseOrders.m | 144 | purchase-order line |
| 14 | FactRawInventory | powerbi/phase9a/power_query/FactRawInventory.m | 240 | material/month snapshot |
| 15 | FactFGInventory | powerbi/phase9a/power_query/FactFGInventory.m | 480 | product/month snapshot |
| 16 | FactOpex | powerbi/phase9a/power_query/FactOpex.m | 48 | month/expense category |
| 17 | FactConsumption | powerbi/phase9a/power_query/FactConsumption.m | 1536 | production batch/material issue |
| 18 | RefPnL | powerbi/phase9a/power_query/RefPnL.m | 3 | approved reference period (annual and combined) |
| 19 | RefMonthlyPnL | powerbi/phase9a/power_query/RefMonthlyPnL.m | 24 | reference month |

Use FactSales from Phase 9A initially so the base model can be validated. Step 7 replaces that SAME query with the final Phase 9B version; do not add a second sales table. Do not import bi_customer_month_performance, product/month/period aggregate views as additional business facts. Their totals overlap the detailed facts.

Close & Apply. In Power Query verify IDs are Text, dates Date, counts Whole Number, amounts Fixed Decimal Currency where supplied, kg three-decimal numbers and eight-decimal weighted-average unit costs Decimal Number. Do not blanket-convert unit costs/rates to Currency. RefPnL and RefMonthlyPnL are hidden, disconnected reference tables, not facts to sum alongside sales.

## 4. Configure the Date table and every relationship

Select DimDate, mark it as the Date table using the Date column. Expected current coverage: 2024-01-01 through 2025-12-31, 731 unique nonblank dates, including leap day. The M query constructs full years dynamically from source dates; no extra DAX Date table is needed. Sort MonthName by MonthNumber and YearMonth by YearMonthSort. Create Year → Quarter → YearMonth hierarchy for accounting pages.

For every row below use 1:* cardinality and Single filtering from dimension to fact. DimDate[Date] is the one-side key; **do not use DimDate[MonthStart]**, which repeats daily. Active monthly links use the stored month_id, ReceiptMonth or OrderMonth. Inactive daily links are activated only by the supplied role measures.

| Dimension/key (1) | Fact/key (*) | Active? |
|---|---|---|
| DimDate[Date] | FactSales[month_id] | Yes |
| DimProduct[product_id] | FactSales[product_id] | Yes |
| DimCustomer[customer_id] | FactSales[customer_id] | Yes |
| DimLine[line_id] | FactSales[line_id] | Yes |
| DimDate[Date] | FactProduction[month_id] | Yes |
| DimProduct[product_id] | FactProduction[product_id] | Yes |
| DimLine[line_id] | FactProduction[line_id] | Yes |
| DimDate[Date] | FactManufacturing[month_id] | Yes |
| DimProduct[product_id] | FactManufacturing[product_id] | Yes |
| DimLine[line_id] | FactManufacturing[line_id] | Yes |
| DimDate[Date] | FactConversion[month_id] | Yes |
| DimLine[line_id] | FactConversion[line_id] | Yes |
| DimDate[Date] | FactCapacity[month_id] | Yes |
| DimLine[line_id] | FactCapacity[line_id] | Yes |
| DimDate[Date] | FactReceipts[ReceiptMonth] | Yes |
| DimMaterial[material_id] | FactReceipts[material_id] | Yes |
| DimSupplier[supplier_id] | FactReceipts[supplier_id] | Yes |
| DimDate[Date] | FactPurchaseOrders[OrderMonth] | Yes |
| DimMaterial[material_id] | FactPurchaseOrders[material_id] | Yes |
| DimSupplier[supplier_id] | FactPurchaseOrders[supplier_id] | Yes |
| DimDate[Date] | FactRawInventory[month_id] | Yes |
| DimMaterial[material_id] | FactRawInventory[material_id] | Yes |
| DimDate[Date] | FactFGInventory[month_id] | Yes |
| DimProduct[product_id] | FactFGInventory[product_id] | Yes |
| DimLine[line_id] | FactFGInventory[line_id] | Yes |
| DimDate[Date] | FactOpex[month_id] | Yes |
| DimDate[Date] | FactConsumption[month_id] | Yes |
| DimProduct[product_id] | FactConsumption[product_id] | Yes |
| DimMaterial[material_id] | FactConsumption[material_id] | Yes |
| DimLine[line_id] | FactConsumption[line_id] | Yes |
| DimDate[Date] | FactSales[shipment_date] | No |
| DimDate[Date] | FactReceipts[receipt_date] | No |
| DimDate[Date] | FactPurchaseOrders[order_date] | No |
| DimDate[Date] | FactPurchaseOrders[expected_receipt_date] | No |

Final count: **30 active + four inactive relationships**. RefPnL/RefMonthlyPnL have no relationships. Never add fact-to-fact, bidirectional, many-to-many or dimension-to-dimension links. DimLine and DimProduct filter the relevant facts independently; there is no DimLine → DimProduct relationship. Hide DimProduct[line_id] and use DimLine for line slicers. Composite fact keys describe grain; they do not require composite relationships.

Monthly financial, production and inventory measures require complete calendar months. Use Year/YearMonth slicers, not a daily range slider. The core Complete Month Context measure returns false for partial days; Company Context Valid also rejects entity filters for unallocated company P&L. Daily Shipment Revenue, Daily Received kg, Daily Ordered kg and Expected Receipt kg explicitly activate the inactive date roles. Do not build daily OP by combining daily sales with monthly costs.

## 5. Install the 120 core DAX measures only

Select FactSales as the home table. Use New measure and paste the exact Name = Formula from [Phase 9A DAX library](../powerbi/phase9a/DAX_LIBRARY.md). Create only the core measures in the order below. **Skip the old Phase 9A optional measures**; Phase 9B replaces them later. Set the documented format and display folder. The core DEFINE file is query-scoped code for DAX Studio, not a block to paste into New measure.

Optional bulk creation: powerbi/phase9a/dax/create_core_measures.csx in Tabular Editor after all tables exist. It stops on name conflicts and was not compiled/executed during preparation. Manual measure expressions are complete if the external tool is unavailable. No paid tool or AI assistance is required for the manual route.

| Order | Core measure |
|---:|---|
| 1 | Complete Month Context |
| 2 | Company Context Valid |
| 3 | Net Revenue |
| 4 | Gross Sales |
| 5 | Sales Discounts |
| 6 | Shipped Units |
| 7 | Requested Units |
| 8 | Unfulfilled Units |
| 9 | Net Realized Price |
| 10 | Revenue Prior Year |
| 11 | Revenue YoY % |
| 12 | Revenue YTD |
| 13 | Material COGS |
| 14 | Inbound Freight COGS |
| 15 | Labor COGS |
| 16 | Energy COGS |
| 17 | Overhead COGS |
| 18 | Manufacturing COGS |
| 19 | COGS per Shipped Unit |
| 20 | Gross Profit |
| 21 | Gross Margin % |
| 22 | Outbound Freight |
| 23 | Contribution after Outbound |
| 24 | Contribution Margin % |
| 25 | Product Gross Profit Rank |
| 26 | Selling Expenses |
| 27 | Administrative Expenses |
| 28 | Fixed Selling Expenses |
| 29 | Variable Selling Expenses |
| 30 | Idle Production Costs |
| 31 | Abnormal Production Losses |
| 32 | Separately Expensed Production Costs |
| 33 | Operating Profit |
| 34 | Operating Margin % |
| 35 | Operating Profit Prior Year |
| 36 | Operating Profit YoY % |
| 37 | Operating Margin Change pp |
| 38 | Operating Profit YTD |
| 39 | Attempted Units |
| 40 | Good Units |
| 41 | Defective Units |
| 42 | Effective Capacity Units |
| 43 | Capacity Utilization % |
| 44 | Defect Rate % |
| 45 | Good Yield % |
| 46 | Purchase Material Manufacturing Cost |
| 47 | Inbound Manufacturing Cost |
| 48 | Manufacturing Labor Cost |
| 49 | Manufacturing Energy Cost |
| 50 | Manufacturing Overhead Cost |
| 51 | Capitalized Production Cost |
| 52 | Total Manufacturing Cost |
| 53 | Material Manufacturing Share % |
| 54 | Inbound Manufacturing Share % |
| 55 | Labor Manufacturing Share % |
| 56 | Energy Manufacturing Share % |
| 57 | Overhead Manufacturing Share % |
| 58 | Pool Labor Cost |
| 59 | Pool Energy Cost |
| 60 | Labor Hours |
| 61 | Activity Labor Hours |
| 62 | Support Labor Hours |
| 63 | Energy kWh |
| 64 | Activity Energy kWh |
| 65 | Standby Energy kWh |
| 66 | Realized Labor Rate |
| 67 | Realized Energy Tariff |
| 68 | Activity Labor per Attempt |
| 69 | Activity Energy per Attempt |
| 70 | Purchase Spend |
| 71 | Inbound Receipt Freight |
| 72 | Landed Receipt Value |
| 73 | Received kg |
| 74 | Receipt Count |
| 75 | On Time Receipts |
| 76 | Receipt OTD % |
| 77 | Supplier Target OTD % |
| 78 | Supplier Target Gap pp |
| 79 | Mean Lead Days |
| 80 | Mean Late Days |
| 81 | Weighted Purchase Price |
| 82 | Weighted Landed Price |
| 83 | Supplier Spend Share % |
| 84 | Ordered kg |
| 85 | Outstanding Ordered kg |
| 86 | Raw Closing Inventory |
| 87 | Raw Opening Inventory |
| 88 | Average Raw Inventory |
| 89 | FG Closing Inventory |
| 90 | FG Opening Inventory |
| 91 | Average FG Inventory |
| 92 | Landed Raw Issues |
| 93 | Inventory COGS |
| 94 | FG Turnover |
| 95 | Raw Turnover |
| 96 | Combined Closing Inventory |
| 97 | Combined Average Inventory |
| 98 | Combined Inventory Turnover |
| 99 | Selected Calendar Days |
| 100 | Inventory Days Proxy |
| 101 | Closing Inventory Change |
| 102 | Customer Revenue Share % |
| 103 | Top 1 Customer Share % |
| 104 | Top 5 Customer Share % |
| 105 | Top 10 Customer Share % |
| 106 | Customer HHI |
| 107 | Active Customers |
| 108 | Outbound per Shipped Unit |
| 109 | Outbound Revenue Burden % |
| 110 | Raw Freight Inventory Change |
| 111 | FG Freight Inventory Change |
| 112 | Inbound Abnormal Loss |
| 113 | Inbound Freight Bridge Difference |
| 114 | Daily Shipment Revenue |
| 115 | Daily Received kg |
| 116 | Daily Ordered kg |
| 117 | Expected Receipt kg |
| 118 | COGS Component Difference |
| 119 | Monthly PnL Revenue Difference |
| 120 | Monthly PnL OP Difference |

All home tables are FactSales for organization; this does not mean every measure reads sales. Hide raw fact numeric columns, repeated descriptive attributes, technical keys and overlapping subtotal columns so users choose explicit measures. Use dimension fields for slicers. Rates, weighted-average prices, percentages and snapshots are not additive. Percentage measures return 0–1 fractions; format as 0.00%. SQL reference percentages use 0–100 units. Percentage-point measures already multiply changes by 100 and use pp formatting.

## 6. Prove the base model before scenarios

Run the prepared queries in powerbi/phase9a/validation/01_annual_financial.dax through 05_filter_edge_cases.dax using DAX Query View or an attached DAX Studio session. Alternatively compare equivalent cards/matrices manually if those query tools are unavailable. Use a clean report page with no entity filters for company P&L. [The full checklist](../powerbi/phase9a/FINANCIAL_VALIDATION.md) describes every expected result.

| EUR | 2024 | 2025 | Combined |
|---|---:|---:|---:|
| Net Revenue | 10,559,374.25 | 10,973,277.52 | 21,532,651.77 |
| Manufacturing COGS | 8,095,663.36 | 8,411,512.20 | 16,507,175.56 |
| Gross Profit | 2,463,710.89 | 2,561,765.32 | 5,025,476.21 |
| Outbound Freight | 286,376.98 | 295,196.43 | 581,573.41 |
| Selling Expenses | 525,761.49 | 539,655.54 | 1,065,417.03 |
| Administrative Expenses | 459,762.00 | 467,970.00 | 927,732.00 |
| Operating Profit | 1,191,810.42 | 1,258,943.35 | 2,450,753.77 |

Idle/abnormal losses are zero in the approved dataset but remain explicit deductions. Financial money differences must round to EUR 0.00; zero-baseline percentage differences use 0.00000001 percentage-point tolerance after converting DAX ratios to percent units. Do not change source/reference numbers or assumptions to make a test pass.

Verify product/customer revenue and COGS sum back to company totals, and adding a dimension does not multiply totals. Company OP under Product/Customer/Line/Material/Supplier filters must be BLANK; use Contribution after Outbound for product/customer economics. Capacity is Date/Line-level; do not invent product capacity allocation. Raw inventory supports Date/Material, FG supports Date/Product/Line, combined inventory company Date only. Closing values are the selected last month, not summed snapshots; annual turnover requires twelve complete months in one year.

## 7. Apply the final Phase 9B overlay without duplicate tables

In Power Query select the EXISTING FactSales query and replace its expression with powerbi/phase9b/power_query/FactSales.m. Reuse fxRead/pServer/pDatabase. Refresh: expect the same 2,596 unique sales rows, every original amount unchanged, plus direct_labor_cogs_exposure_eur and support_labor_cogs_exposure_eur. There are no new model relationships or fact tables.

The query reconstructs an analytical direct/support split through monthly labor inventory using complete history, deterministic cent rules and a fail-on-invalid flag. It does not create a database object or modify booked costs. Direct+support must equal original labor COGS at row/product/month/customer level. Do not filter away earlier source history before reconstruction. The 120 core formulas stay unchanged.

Create/reuse the SAME six parameter tables using powerbi/phase9b/dax/parameter_tables.dax. Each expression is entered separately as a calculated table; format Value as 0%. The names are ParamMaterial, ParamInbound, ParamOutbound, ParamLabor, ParamEnergy and ParamPrice. Each has 151 fixed-decimal values, −50% to +100% in one-percentage-point steps; default zero. No parameter has a relationship. Do not run a wizard that creates six more tables or selector measures.

Use a single-value slider when supported by the installed Desktop, otherwise a Single select Dropdown/List with Select all disabled. A Between/Before/After range slicer gives multiple values and the selector falls back to zero; it is not an appropriate substitute. Show six selected-change cards and a reset-to-zero bookmark. Label labor as Direct production labor cost change. Full setup and limitations: [Phase 9B parameters](../powerbi/phase9b/PARAMETERS.md).

Create/update the following 22 measures from [the exact final scenario library](../powerbi/phase9b/SCENARIO_DAX_LIBRARY.md), in this order. If the older fourteen were already created, update them by the SAME name; add only eight missing measures. Do not install both optional libraries under different names.

| Order | Final scenario measure |
|---:|---|
| 1 | Material Change % |
| 2 | Inbound Change % |
| 3 | Outbound Change % |
| 4 | Labor Change % |
| 5 | Energy Change % |
| 6 | Price Change % |
| 7 | Direct Labor COGS Exposure |
| 8 | Support Labor COGS Exposure |
| 9 | Labor Exposure Difference |
| 10 | Scenario Revenue |
| 11 | Scenario Manufacturing COGS |
| 12 | Scenario Outbound Freight |
| 13 | Scenario Gross Profit |
| 14 | Scenario Gross Margin % |
| 15 | Scenario Selling Expenses |
| 16 | Scenario Operating Expenses |
| 17 | Scenario Operating Profit |
| 18 | Scenario Operating Margin % |
| 19 | Scenario GP Change |
| 20 | Scenario GP Change % |
| 21 | Scenario OP Change |
| 22 | Scenario OP Change % |

The final model has **120 core + 22 scenario = 142 measures**, **19 core + six parameter = 25 tables**, and the SAME 34 relationships. No extra measure table is required. The optional guarded Tabular Editor upgrade script is available, but the manual expressions are complete. Scenario Operating Expenses means selling+administration; outbound and production losses are deducted separately once. Labor changes only direct exposure; support stays fixed. Scenarios do not revalue source inventory or forecast volume/demand.

## 8. Validate the final scenarios

Set all six parameters to zero and repeat every baseline test. Then run powerbi/phase9b/validation/desktop_checks.dax and desktop_scenario_matrix.dax. The matrix explicitly sets parameters/date filters for 22 cases × three periods; compare all 66 rows by period/scenario to the reference CSV/JSON. If testing manually, at minimum execute all eight requested cases for 2024, 2025 and combined. Full results: [financial reconciliation](../reports/phase9b_20261024T234841/FINANCIAL_RECONCILIATION.md).

Combined-period independent reference OP examples (not executed DAX): all zero 2,450,753.7700; material +10% 1,780,851.6660; direct labor +10% 1,761,796.1050; selling price +5% 3,505,853.7070; material +10% with price +5% 2,835,951.6030. Keep full precision when investigating differences; final independent half-cent presentation rounding can differ by one cent. Zero-baseline source amounts still must match approved cents.

Material/inbound/direct-labor/energy shocks affect recognized COGS and GP/OP. Outbound affects OP but not GP. Price changes revenue and variable selling at fixed volume; fixed selling/admin remain fixed. Support labor and overhead remain fixed. Combined material/price change must equal the sum of isolated effects under this linear historical model. Check reset, boundary values and company-scope BLANK behavior. No DAX results have been claimed as tested in this project yet.

## 9. Build report pages and navigation

| Page | Suggested visuals | Slicers and interpretation |
|---|---|---|
| Executive | Revenue/GP/OP cards, monthly trend, annual YoY matrix, P&L bridge | Date only for company OP |
| Product | GP rank, revenue/margin scatter, five-component COGS matrix, contribution | Date/Product/Line; Customer applies sales, not production |
| Manufacturing | Cost mix, labor/energy intensity, support/activity comparisons | Date/Line for pools; keep allocation/product visuals distinct |
| Production | Volume/defect cards, utilization trend, defect line/product bars | Date/Line; Product only on volume/quality |
| Procurement | Supplier spend/Pareto, OTD/target, lead days, material-price trend | Supplier/Material, receipt month versus order month clearly labeled |
| Inventory | Raw/FG stock trends, component stock, annual turnover/days | Supported entity slicers only; stock values are actual historical |
| Customer | Revenue Pareto, top-N share, contribution, segment mix | Selected-cohort definitions; clear filters to match company SQL |
| Logistics | Outbound per unit/burden, inbound recognition bridge | Customer for outbound; company Date only for bridge |
| Daily operations | Daily shipment revenue and procurement quantities | Daily Date role; no daily company OP |
| Sensitivity | Base/scenario GP/OP/margins, profit changes, cost bridge | Six single-value parameters; company Date only for OP |
| Quality (internal) | Baseline differences, source counts, exposure reconciliation | Check before refreshing/publishing |

Use page-navigation buttons, a consistent reporting-period title and reset-filters bookmarks. Use Edit interactions so a slicer does not affect an unsupported visual; do not synchronize entity filters to Executive/Sensitivity company OP pages. State synthetic data and historical sensitivity in titles/tooltips. Use a readable consistent EUR/percent format; do not imply real-company savings or optimized pricing. Add screenshots only after actual completion, under a new documented image folder.

## 10. Troubleshooting without AI

| Symptom | Project-specific check / remedy |
|---|---|
| Authentication fails | Power BI credentials differ from psql pgpass; edit Data source settings. Verify host/port/database/account, do not disable server authentication. |
| Table/column not found | Use exact query names and manufacturing_v2. Do not substitute public or import old processed schemas. Check M script file and capitalization. |
| Native query rejected | Review provided SELECTs and connector approval; ensure reader can SELECT all referenced base tables/views. No CREATE permission is required for report refresh. |
| Duplicate key/ambiguous relationship | Compare the 34-row relationship list, remove only unintended model auto-links, verify DimDate[Date] not MonthStart on the one-side. Never fix by enabling Both filtering. |
| DAX measure missing | Create prior core dependencies in order, then final Phase 9B scenarios. DEFINE is a query library, not a New measure expression. |
| OP is BLANK | Check complete-month selection and remove entity filters. This is intentional shared-cost protection, not an allocation bug. |
| Percent is 100 times too large/small | DAX ratios are fractions; SQL percentage references are 0–100. Use supplied tests/formats. |
| Slider gives no change | Ensure exactly one parameter Value is selected; a range/multiple selection returns zero. Confirm percent units and exact fixed-decimal formulas. |
| Direct labor exposure refresh error | Full history and zero initial FG labor lineage are required. Do not remove early months; inspect SQL checks and provided source query. Never bypass the fail-on-invalid flag. |
| Inventory/year totals too large | Use explicit snapshot/average measures, not SUM of closing columns. Turnover requires one full year. |
| Revenue duplicates | Do not join fact tables or add aggregate views as extra facts. Use dimensions and measures; compare product/customer totals to baseline. |
| Company total changes under Supplier/Material | Those dimensions do not provide sales COGS lineage. Use the documented page scopes, not a bidirectional bridge. |
| Scenario off by a cent | Inspect unrounded values and Currency types; distinguish final half-cent rounding from a real component/double-count error. Never alter the baseline. |

For a failed test record the exact error, active filters, query/measure name, source row count and expected reference value in a local test log. Start from the last passing step and consult the exact formula/source mapping; do not rewrite assumptions to force agreement.

## 11. Save, document and publish later

Save As a NEW file such as powerbi/Manufacturing_360_v2.pbix; PBIX files are ignored by default. Record Desktop version, refresh date, data/model counts and which acceptance queries passed. Add actual dashboard screenshots, a report-page index and tested/untested status after implementation. Keep the legacy PBIX intact.

Optional Power BI service publication is separate: choose an authorized workspace/account, review data-source credentials/privacy, configure the appropriate gateway/refresh for a local PostgreSQL host, and validate the service result. No service publication, license availability, RLS or successful gateway refresh is assumed. A screenshot-based GitHub portfolio is possible without publishing the full dataset/PBIX, subject to your own review.

GitHub publication is a separate approval step: [checklist](GITHUB_PUBLICATION_CHECKLIST.md). Do not embed credentials, personal paths or binary connection metadata in a public repository. This guide, all M/DAX and reference outputs remain usable after any AI subscription ends.

## Completion log

| Gate | Expected | Observed / date |
|---|---|---|
| Core model | 19 tables, 34 relationships, 120 measures | Pending Desktop |
| Final scenario model | 25 tables, same 34 relationships, 142 measures | Pending Desktop |
| Baseline money/percent | Approved annual/combined values | Pending Desktop |
| Scenario checks | 66 reference outcomes + zero baseline | Pending Desktop |
| Filters/snapshots/roles | Documented guards and no fanout | Pending Desktop |
| Refresh/visuals | Repeatable and correctly labeled | Pending Desktop |
| New PBIX/screenshots | Saved separately after acceptance | Pending Desktop |

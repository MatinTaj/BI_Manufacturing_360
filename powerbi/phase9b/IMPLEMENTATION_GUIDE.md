# Power BI What-if implementation and validation guide

No Power BI model was opened or modified during Phase 9B. Work in the new Phase 9A model later; preserve the legacy dash1.pbix. All required code for this static sensitivity scope is supplied.

## 1. Upgrade the existing FactSales query

Keep all nineteen Phase 9A model tables and all 34 relationships. In Power Query select the existing **FactSales** query, open Advanced Editor and replace its expression with power_query/FactSales.m from this Phase 9B folder. Do not add a second FactSales table. Reuse Phase 9A fxRead, pServer and pDatabase. The native SELECT runs against manufacturing_360.manufacturing_v2 without creating any object. It needs SELECT permission on the same sales/production/allocation/inventory sources used by the model.

The query adds direct_labor_cogs_exposure_eur and support_labor_cogs_exposure_eur, both Currency, while preserving every existing field and sales_line_id. The validation flag is checked and removed before load. It was verified to return the same 2,596 unique source rows and original values. Refresh, confirm no error, and hide the two technical exposure columns from report consumers. Do not filter away earlier inventory history before the recursive native query.

## 2. Reuse parameter tables

Reuse ParamMaterial, ParamInbound, ParamOutbound, ParamLabor, ParamEnergy and ParamPrice. Follow PARAMETERS.md and copy the matching formula from dax/parameter_tables.dax into each existing calculated table. Fixed-decimal inputs replace floating numeric steps without changing table/column names, range or defaults. If no optional parameters were created yet, create these six once. Do not add wizard-generated duplicate tables or selector measures. Keep all disconnected; apply 0% format to Value and save a single selected 0% for each.

## 3. Install or update measures

Keep all 120 Phase 9A core measures unchanged. The fourteen former optional measure names are reused. Update those expressions from SCENARIO_DAX_LIBRARY.md and add the eight new measures: Direct Labor COGS Exposure, Support Labor COGS Exposure, Labor Exposure Difference, Scenario Gross Margin %, Scenario Operating Expenses, Scenario GP Change, Scenario GP Change % and Scenario OP Change %. Create in the supplied numbered order; all use FactSales as home table and display folder 12 Historical Sensitivity.

Do not also install the older optional DEFINE file under different names. If using DAX Studio, use the Phase 9B DEFINE library instead of the old optional library. DEFINE scopes query measures only; it does not persist them to the model. For persisted measures, paste each Name = Formula into New measure or edit its existing formula. The optional Tabular Editor script installs/updates the same names only after an explicit allowScenarioUpgrade flag and source-column checks; it has not been compiled or executed here. Manual formulas are complete without that external tool.

## 4. Configure controls

Use six single-value sliders where supported; otherwise use the documented single-select dropdown/list fallback. Never use a Between range slicer with SELECTEDVALUE. Show six selected-change cards to make any fallback-to-zero visible. Values are fractions: 0.10 displays 10%, not 0.10%. Use a 0% reset bookmark and test it after every saved bookmark change. Label the labor control **Direct production labor cost change**, not all labor.

The company scenario page accepts Date Year/YearMonth only, using complete calendar months. Do not sync entity slicers onto its OP visuals: Company Context Valid deliberately returns BLANK when Product/Customer/Line/Material/Supplier filters imply an unsupported expense allocation. Product/customer contribution or gross profit can be analyzed separately at recognized sales grain; source material/supplier filters cannot identify sales COGS lineage.

## 5. Build baseline-versus-scenario visuals

- Baseline and Scenario Revenue, GP and OP cards, paired with absolute and percentage profit-change cards. Always show absolute change beside percentage change.
- Side-by-side baseline/scenario gross and operating margins, formatted 0.00%.
- Clustered columns by year: Operating Profit versus Scenario Operating Profit. Monthly line trend can show the same comparison under the selected static changes.
- Five-component COGS matrix with baseline material/inbound/labor/energy/overhead; label that support labor remains fixed under the labor slider.
- An operating-profit bridge can use the documented isolated effects: price revenue benefit less variable-selling increase, minus material/direct-labor/energy/inbound/outbound increases. Do not add a full COGS subtotal and its components to one waterfall. If using a native waterfall, a small manual disconnected label table is optional; a matrix or clustered bar is sufficient without extra model code.
- Tooltips: historical sensitivity; unchanged units, discounts and source inventories; variable-selling behavior; direct/support attribution; company OP scope; fractional-cent rounding.

Source inventory visuals remain actual historical balances. Do not label them scenario-revalued inventory or combine them into a claimed counterfactual balance sheet.

## 6. Run zero and representative scenario checks

First refresh the upgraded FactSales query. Run validation/desktop_checks.dax: Labor Exposure Difference must be zero in all year/product/customer sales slices; company-guard checks must pass. Set six parameters to zero and rerun the Phase 9A annual/monthly/combined financial tests. Existing approved baseline money must remain unchanged.

Then execute validation/desktop_scenario_matrix.dax in Desktop DAX Query View or attached DAX Studio after measures exist. It sets Date/parameter filters explicitly for all 22 cases × three periods and outputs 66 rows. Compare the eight required cases for 2024, 2025 and combined, plus boundary cases, with scenario_results_full_precision.json or scenario_results.csv in the Phase 9B report. Match by period/scenario, not row order. The query's percentage columns multiply DAX fractions by 100 to match the reference report.

Compare monetary fields at final two-decimal presentation. First inspect unrounded differences: ordinary binary/runtime rounding may produce tiny differences; a single cent at an exact half-cent presentation tie must be documented, not hidden by changing baseline. Zero-baseline source money should round to the exact approved cents. Compare percentages at six decimal places for scenario math, and retain Phase 9A's stricter approved baseline tolerance for zero-baseline comparisons.

Test each driver alone. Material/labor/energy/inbound change COGS and GP/OP; outbound changes OP but leaves GP unchanged; price changes revenue and variable selling while fixed SG&A stays fixed. Combined material/price OP change must equal the sum of isolated changes under the linear static model. Test range endpoints, no selection, multiple selection and reset. Multiple-selection zero fallback is intentional but should not be a normal UI state.

## 7. Desktop acceptance checklist

- [ ] New FactSales M query compiles, refreshes and yields 2,596 unique rows; original financial totals unchanged.
- [ ] Direct+support exposure equals original labor COGS by row/product/month/customer; no extra relationship or sixth COGS component.
- [ ] Six existing parameter tables compile with 151 exact values, percent format and zero single-select defaults.
- [ ] All 22 scenario measures compile; fourteen existing names updated and only eight added; 120 core measures untouched.
- [ ] All-zero annual/combined/monthly financial baselines pass; both profit margins and expense lines agree.
- [ ] The 66-row Desktop matrix reconciles to the independent reference, including all eight required cases.
- [ ] Product-filtered scenario OP/change are BLANK; daily/partial-month contexts do not fabricate monthly company profit.
- [ ] Slider or dropdown behavior, percent scaling, reset bookmark, visual totals and tooltips are correct.
- [ ] Repeat refresh and validation before saving/publishing a new report. Existing PBIX files remain untouched unless separately authorized.

Actual DAX, M, C# and visual execution remain pending. The reference calculator is not a DAX engine. No GitHub finalization, commit, push or publication was performed.

# Phase 9B completion report

**Complete as an audited preparation/reference-validation handoff. Actual Power BI runtime acceptance remains pending.** No GitHub finalization was started.

## Delivered changes

A new powerbi/phase9b overlay reuses the existing six parameters and fourteen scenario measure names. Twenty-two audited scenario measures include only eight additions needed for direct/support labor, decomposition validation, gross margin, operating expenses and profit-change outputs. The 120 core measures, all Phase 9A files, existing relationships and model table count remain unchanged.

The audit identified that Phase 9A's labor parameter affected support as well as direct labor. A read-only recursive SELECT plus an independent Python cent algorithm derive direct/support recognized COGS through the existing monthly weighted-average labor inventory totals. The replacement FactSales M adds exactly two derived exposure columns and preserves all original rows/columns/values. No new PostgreSQL object, CSV field, fact table or relationship is created. The direct-only parameter is now explicitly labeled; support stays fixed. Derived attribution is documented and is not claimed to be a source-booked sixth component.

Existing parameter names and −50%/+100% ranges/default zero are preserved. CURRENCY-based grids yield 151 exact steps, reducing floating value-key risk. Measures add explicit complete-month and company-scope guards and keep outbound, SG&A and separately expensed production costs distinct. Scenario Operating Expenses means selling plus administration, matching the source operating_expenses scope.

## Results verified

The eight required scenarios were evaluated for 2024, 2025 and combined (24 cases). Fourteen additional boundary/all-driver cases per period bring the total to 66. Zero settings matched all 33 approved Phase 7 metrics. Independent closed-form GP/OP equations matched in 132 comparisons. Every scenario conserved five-component COGS and company P&L, with support/overhead/fixed SG&A unchanged as defined. Fifteen in-memory tests passed, including cent ties, zero activity, fully defective additions, rejected unknown initial stock lineage, zero-profit ratios, invalid inputs, outbound isolation and combined linearity.

SQL/Python exposure values agree for 480 product/month labor ledgers and all 2,596 sale rows. The native SQL extracted from the M file matches the reviewed projection and executes read-only with 2,596 unique valid sale IDs and zero labor difference. Every original sales-view value was compared and preserved. An M-string comment-formatting hazard was detected and corrected before handoff; the exact final embedded SQL is part of the static audit.

Combined baseline OP remains EUR 2,450,753.77. Independent reference outputs include material +10% OP EUR 1,780,851.6660; direct labor +10% EUR 1,761,796.1050; price +5% EUR 3,505,853.7070; material +10% with price +5% EUR 2,835,951.6030. These retain fractional cents and are **reference-calculator results, not executed DAX results**. Full annual/combined tables and all financial lines are in FINANCIAL_RECONCILIATION.md and scenario_results_full_precision.json in the report directory.

All 36 existing live SQL integrity checks and 33 live baseline comparisons passed. Before/after hashes for 23 public/v2 tables and definitions match. All 314 pre-existing project files match their original SHA-256 hashes, including datasets, SQL analyses, Phase 9A files and existing PBIX. No source data, accounting assumptions, prices or database objects changed. Only new preparation/report files were written.

## Static checks versus runtime

DAX references, dependency ordering, parameter reuse, component ownership and delimiter structure were checked statically. Native PostgreSQL SELECTs and independent Python mathematics were executed. DAX, M and the optional C# deployment script were not compiled/executed in Desktop. A static PASS is not an engine or connector correctness certificate. The mathematical reference intentionally preserves the established historical accounting baseline rather than forcing margins.

## Remaining manual Power BI Desktop actions

1. In the separately built/new Phase 9A model, replace only the existing FactSales M expression with this phase's file. Refresh, confirm 2,596 unique sales and two exposure columns, and validate unchanged base financial totals.
2. Create/update the same six parameter tables with the fixed-decimal formulas; keep them disconnected, percent-formatted and single-selected at zero. Configure a single-value slider if available or the documented single-select dropdown/list fallback. Test selected-value cards and reset behavior.
3. Update the fourteen existing optional scenario measures and add the eight new measures in supplied order. Preserve all 120 core measures. The optional external-tool script requires an explicit opt-in; manual formulas are complete without it.
4. Execute the Phase 9A baseline checks, Phase 9B labor/scope checks and the 66-row Desktop scenario matrix. Compare reference results with documented percent conversion and final display-rounding rules. Check complete-month guards, entity-scope BLANK behavior and zero denominator behavior.
5. Build/test baseline-versus-scenario cards, trends, cost/expense comparisons, slicer interactions and tooltips. Do not present historical inventories as scenario-revalued or outputs as a forward-looking forecast. Repeat refresh and acceptance before saving a new report; existing PBIX remains untouched.

No additional Python/SQL/Codex development is needed for the supplied static historical sensitivity scope. A prospective forecast with inventory timing, demand/capacity response or material-specific sales lineage is outside this scope and would need separately approved assumptions and work. No commit, push, repository finalization or publication was performed.

## Created files and evidence

All new code/docs are under powerbi/phase9b; all execution evidence is under the report path recorded in report_path.txt. artifact_manifest.json inventories every created file and SHA-256 hash. The evidence includes full-precision scenario outputs, displayed financial tables, baseline driver amounts, zero reconciliation, exposure validation, native SQL/static audit, fifteen unit-test results and before/after protection manifests. No pre-existing file was modified.

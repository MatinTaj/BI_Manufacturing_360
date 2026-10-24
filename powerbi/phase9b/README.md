# Phase 9B â€” finalized historical What-if sensitivity

Prepared and reference-validated, without opening or changing Power BI files. The same six parameter tables and fourteen existing scenario measure names are reused. Eight necessary measures complete direct/support labor exposure, validation, gross margin, SG&A and profit-change outputs. All 120 core measures remain unchanged.

## Start here

- [Desktop implementation guide](IMPLEMENTATION_GUIDE.md): replace the existing FactSales query, reuse parameters, install/update measures, configure controls/visuals and validate.
- [Audited DAX library](SCENARIO_DAX_LIBRARY.md), plus structured/query-scoped versions under dax/.
- [Parameter definitions and single-value controls](PARAMETERS.md).
- [Accounting, direct-labor lineage and limitations](ACCOUNTING_AND_LIMITATIONS.md).
- [Completion report](COMPLETION_REPORT.md), with reference results path and manual acceptance list.
- [Official technical references](REFERENCES.md).

## Important correction

Phase 9A labor COGS included direct production and support labor. Direct-labor-only sensitivity therefore required two analytical exposure columns in the same FactSales model table. The supplied replacement M executes a read-only SQL reconstruction through monthly weighted-average labor inventory and deterministic cent allocation; every existing sale/financial value is preserved. No database object, CSV column, relationship, extra fact table or accounting amount is changed. The labor slider affects only direct exposure; support stays fixed. Do not count the new exposure columns as additional COGS.

The six parameter names and ranges are retained; fixed-decimal CURRENCY grids avoid floating value-key mismatches. No wizard-created duplicate parameters are needed. Phase 9A files remain intact as preparation history; use this phase's replacement optional scenario formulas, not both libraries as separate measures.

## Verified versus pending

The Python reference calculator passed 66 scenario-period cases, 33 zero-baseline comparisons and 132 independent GP/OP delta comparisons. SQL/Python agree for all 2,596 labor sale-line splits and 480 monthly ledgers; 15 mathematical edge tests passed. Existing SQL checks/baseline and protected files remain unchanged. The exact SQL string embedded in the M script was executed read-only and returns 2,596 unique valid rows with zero labor decomposition difference.

DAX, Power Query M, the optional external-tool script, parameter controls and visuals have **not** executed in Power BI Desktop. All necessary code for the defined historical sensitivity is supplied, but manual Desktop installation/refresh/validation remains required. This is not a forward inventory/capacity/demand forecast. No GitHub finalization, commit, push or publication was performed.

## Reproduce the reference checks

From the project root with Python and the existing secure PostgreSQL configuration:

```powershell
python -B powerbi/phase9b/validation/reference_calculator.py
python -B -m unittest discover -s powerbi/phase9b/validation -p test_reference.py -v
```

For the optional static source audit, install/use pglast with PostgreSQL 18 grammar and run static_audit.py with --parser-path as needed. No package installation is needed for the standard-library reference calculator. Its only database operations are SELECT/metadata reads inside READ ONLY transactions and definition-only pg_dump. Reports are written to this phase's report directory, whose path is recorded in report_path.txt; existing source CSV datasets are never written.

[Verified financial reconciliation tables](../../reports/phase9b_20261024T234841/FINANCIAL_RECONCILIATION.md) · [Reference execution summary](../../reports/phase9b_20261024T234841/reference_validation_summary.json)

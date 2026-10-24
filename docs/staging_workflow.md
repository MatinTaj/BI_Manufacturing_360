# Controlled staging workflow

## Generation dependency graph

Python with numpy/pandas is required; Phase 7 records exact runtime/source hashes.
The actual run used bundled Python 3.12.14, pandas 3.0.1 and numpy 2.3.5.

1. `02_generate_master_data.py`: seven master CSVs; seed 360; settings from
   economic_assumptions.py; validates in-memory and exported masters.
2. `03_generate_operations.py`: seven operational CSVs; reads masters from the
   SAME explicit staging directory; seed 361; uses material_valuation.py and
   economic_assumptions.py; validates before export and after readback.
3. `04_generate_financials.py`: five financial CSVs; reads the SAME staged masters/
   operations; seed 362; uses finished_goods_valuation.py and source validators;
   validates before export/readback and runs negative/zero-output regressions.

`01_data_inspection.py` is optional raw-data inspection, not a generation input.
`05_production_analysis.py` reads production data and writes an Excel report; it
is not part of regeneration and is deliberately not executed. Raw Kaggle files
are not sampled or joined into synthetic operations. PostgreSQL and Power BI are
not runtime dependencies of the CSV build.

## Authorized runner

```powershell
python -B scripts/06_stage_financial_model.py --output-dir data/staging
```

All generator entry points now REQUIRE --output-dir. pipeline_io.py permits only
this project's data/staging tree or direct data/staging_repro_* temporary folders,
and exclusively creates CSV files. data/processed, raw, SQL, Power BI, project
root and ancestor traversal are rejected before generation. Processed remains a
read-only default only for audit loader functions; it is never a generator output.

The runner refuses an existing data/staging directory. There is no overwrite or
promotion switch. Preserve/archive an existing candidate through a separately
authorized action before a future run; never remove it merely to bypass refusal.

The runner creates a Europe/Rome timestamped processed backup and SHA-256/schema
manifest FIRST, then runs the test suite. It generates staging, re-reads and
strictly validates all 19 CSVs, then repeats the complete pipeline in a separate
TemporaryDirectory under data/staging_repro_*. Paths are resolved/validated before
use/automatic cleanup. A complete hash equality is required; repeat files are
removed after success and both hash sets remain in the report.

A nonzero generator/test process or failed reconciliation immediately raises;
FAILED.json records the error and protection status. There is no retry, suppression,
automatic correction or promotion. Partial candidates remain unapproved and
are not overwritten. Reports/logs are in reports/phase7_<timestamp>/ and backups
in data/backups/processed_<timestamp>/. Backup manifests preserve all source CSV
bytes and original headers. Protected processed/raw/SQL/Power BI hashes must match.

## Results and scope

The completed run is reports/phase7_20261024T141247792082+0200/. All 61 tests,
strict exported-data checks and 19-file reproducibility checks passed. Initial
sandbox preflight temp-folder access errors were resolved by executing the same
checks with filesystem access before regeneration; no safety assertion was waived.

Candidate operating margin is 11.381570% across 2024-25, versus legacy 60.691730%.
Read the run's economic and migration reports before approval. It is a candidate,
not a production replacement. Full future loads and live Power BI refresh/model
verification require separate authorization and explicit column/type mapping.

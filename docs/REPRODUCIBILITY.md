# Reproduce and validate Manufacturing 360

## Supported setup

The validated setup is Windows + Python 3.12 + PostgreSQL 18, existing database manufacturing_360, schema manufacturing_v2. Install software before going offline. No fresh dependency installation or alternate OS was tested in Phase 10; pinned versions match the executed runtime. Power BI Desktop is needed only for the later manual report/model build.

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$pythonRuntime = (Resolve-Path .\.venv\Scripts\python.exe).Path
& $pythonRuntime -B -m unittest discover -s tests -v
python -B scripts/configure_local_handover.py
```

Expected regression result: 61 tests pass. The bootstrap creates only missing, ignored report pointers and local evidence directories; it preserves existing pointers. It requires the shipped live schema evidence under reports/phase9a_20261024T233001. No database access or data generation occurs.

The validators were originally written for the default Windows PostgreSQL 18 client location C:/Program Files/PostgreSQL/18/bin. Confirm psql.exe and pg_dump.exe there before running those historical helpers. The analytics runner also supports --psql for a custom client path. This Windows-specific default is documented, not a cross-platform compatibility claim. Power Query itself uses only the server/database values, not this filesystem path.

## Secure database connection

Use an existing PostgreSQL 18 server/database that you control. Never target someone else's database. Keep credentials outside the repository. On Windows configure `%APPDATA%/postgresql/pgpass.conf` for psql, restrict it to your account and do not paste the password into scripts or logs. Its line format is host:port:database:user:password; edit the actual value locally. Power BI uses its own connector credential dialog; pgpass success does not prove Power BI authentication.

```powershell
$psqlClient = 'C:/Program Files/PostgreSQL/18/bin/psql.exe'
& $psqlClient -X -w -h localhost -p 5432 -U postgres -d manufacturing_360 -v ON_ERROR_STOP=1 -c "SELECT current_database(), current_user, current_setting('server_version'), to_regnamespace('manufacturing_v2');"
```

This only inspects the environment. The verified local role was postgres; a controlled loader/reader role is preferable for normal operation. The project does not create roles, grants, a server or a database automatically. A reviewer must provision their own development environment separately if absent.

## Load versus inspect

The 19 approved staging CSVs are shipped unchanged and their hashes are pinned by sql/v2/input_manifest.json. The legacy data/processed files remain separate and are required for some regression tests. Never mix their schemas/financial measures.

Run the import preflight without database writes:

```powershell
.\sql\v2\existing_schema\run_schema_import.ps1
```

Expected: PLAN ONLY and matching approved file/reference hashes. If manufacturing_v2 already exists, do not execute migration; run the read-only checks below. If the schema is absent in your own authorized database, inspect the active guide and deliberately execute once:

```powershell
.\sql\v2\existing_schema\run_schema_import.ps1 -Execute
```

This is a future manual setup command, not executed in Phase 10. It creates only the absent schema, loads all 19 datasets and validates before COMMIT. It refuses an existing target, never touches public and provides no DROP/TRUNCATE/reset. Root sql/v2/00â€“05 and apply.psql are the retired separate-database plan; do not execute them. The root run_import.ps1 intentionally errors.

## Read-only validation and analytics

**Recommended in the original workspace:** run `python -B scripts/run_final_acceptance.py` (or use the venv Python). It audits and validates a disposable public-profile copy and bootstraps new local evidence there. Historical Phase 9 pointer/manifests intentionally remain unchanged; running their validators directly in the original workspace after the authorized README update can trip their frozen whole-project hash checks. Do not edit old manifests to bypass that guard.

The individual Python validator commands below are for a fresh extracted/clone workspace AFTER configure_local_handover.py creates the missing local pointers. The direct read-only psql query is safe in either workspace. Install requirements-dev so the parser is importable, or pass --parser-path to the acceptance runner for an isolated pglast installation.

```powershell
& $psqlClient -X -w -h localhost -p 5432 -U postgres -d manufacturing_360 -v ON_ERROR_STOP=1 -c "BEGIN READ ONLY; SELECT * FROM manufacturing_v2.audit_validation_results ORDER BY check_name; SELECT * FROM manufacturing_v2.audit_pnl_reconciliation ORDER BY period,metric; COMMIT;"
& $pythonRuntime -B sql/analytics/run_analytics.py
& $pythonRuntime -B powerbi/phase9b/validation/reference_calculator.py
& $pythonRuntime -B -m unittest discover -s powerbi/phase9b/validation -p test_reference.py -v
& $pythonRuntime -B powerbi/phase9a/validation/check_preparation.py
& $pythonRuntime -B powerbi/phase9b/validation/static_audit.py
```

Expected: 36 model checks have zero failures; 33 financial comparisons pass; eight analytics modules/16 business queries and 83 portfolio gates pass; 66 scenario-period outcomes and 33 zero-baseline comparisons pass; 15 reference unit tests pass. Static DAX/M checks are not execution in Power BI. New result files go to reports/phase8c_* or ignored reports/local paths configured by the bootstrap, never to approved datasets. The historical helpers can refresh their ignored pointer files' result directory; do not confuse those outputs with original frozen evidence.

## Generation policy

Phase 10 did not regenerate data. Reviewers should use the approved supplied CSVs. For a separately authorized generation study, copy scripts/, tests/ and the complete legacy data/processed/ into a NEW sibling workspace that has no data/staging/ directory, install the pinned dependencies, then run `python -B scripts/06_stage_financial_model.py --output-dir data/staging` in that copy. It backs up processed inputs, generates staging exclusively, validates and repeats into a temporary safe directory. Existing output paths are rejected. Never delete or rename the approved original staging directory to bypass the guard; never overwrite processed CSVs. Economic assumptions/seeds must remain unchanged for a like-for-like comparison.

External raw datasets and legacy inspection/Excel-report scripts are not inputs to the 19-table financial pipeline. Raw redistribution rights were not established and the files are excluded from publication. The optional 01_data_inspection.py requires those separately sourced raw files; 05_production_analysis.py is legacy and is not part of validation or generation.

## Offline continuation

Unzip the handover into a new folder and read docs/POWER_BI_START_HERE.md. The ZIP contains project data/code/guides and a SHA-256 manifest, not Microsoft/PostgreSQL installers or a Python wheelhouse. Install/download prerequisites beforehand if working fully offline. The Power BI build can then be completed with local files and the existing database, without ChatGPT/Codex. Optional service publication still needs network access and an appropriately licensed account/workspace.

## Dependency release references

The pins match the executed runtime and their release pages were checked: [numpy 2.3.5](https://pypi.org/project/numpy/2.3.5/), [pandas 3.0.1](https://pypi.org/project/pandas/3.0.1/), [tzdata 2026.5](https://pypi.org/project/tzdata/2026.5/), [pglast 8.7](https://pypi.org/project/pglast/8.7/). This does not certify a fresh pip install or bundle those third-party packages; their own licenses apply.

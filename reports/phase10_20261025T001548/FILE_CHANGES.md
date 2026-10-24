# Phase 10 file changes

Modified pre-existing file: **README.md only**. Every other original file is unchanged. Added files are listed below; local private execution artifacts are noted separately.

## New project code/configuration/documentation

- .gitignore
- docs/FINAL_ACCEPTANCE.md
- docs/GITHUB_PUBLICATION_CHECKLIST.md
- docs/POWER_BI_START_HERE.md
- docs/README.md
- docs/REPRODUCIBILITY.md
- docs/SECURITY_AND_PUBLICATION.md
- requirements-dev.txt
- requirements.txt
- scripts/audit_repository.py
- scripts/configure_local_handover.py
- scripts/run_final_acceptance.py

## New phase report artifacts

- reports/phase10_20261025T001548/README.md
- reports/phase10_20261025T001548/acceptance_results.json
- reports/phase10_20261025T001548/audit_summary.json
- reports/phase10_20261025T001548/execution_logs/bootstrap.log
- reports/phase10_20261025T001548/execution_logs/csv_and_sql_static.log
- reports/phase10_20261025T001548/execution_logs/initial_acceptance_failure.json
- reports/phase10_20261025T001548/execution_logs/phase9a_static_sources.log
- reports/phase10_20261025T001548/execution_logs/publication_preflight.log
- reports/phase10_20261025T001548/execution_logs/python_regressions.log
- reports/phase10_20261025T001548/execution_logs/scenario_reference.log
- reports/phase10_20261025T001548/execution_logs/scenario_static_and_unit_tests.log
- reports/phase10_20261025T001548/execution_logs/sql_analytics.log
- reports/phase10_20261025T001548/original_README.md
- reports/phase10_20261025T001548/protected_before.json

Local-only outputs: reports/local/publication_profile.json, the phase report pointer, disposable test workspaces (cleaned after tests), private execution logs and the retained initial launcher failure. Original README backup/protected-file snapshot remains in the Phase 10 report directory but is ignored. The generated handover ZIP and SHA256.txt are local deliverables excluded from Git. No original backup/report was removed.

Publication exclusions are documented in docs/SECURITY_AND_PUBLICATION.md and enforced by .gitignore; per-file included/excluded inventory is retained privately by the audit helper.

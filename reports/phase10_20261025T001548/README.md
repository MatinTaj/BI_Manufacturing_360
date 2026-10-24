# Phase 10 — final repository audit and independent handover

Status: **PASS for repository preparation and non-destructive acceptance. Publication and Power BI execution remain pending.** Date: 25 October 2026 (Europe/Rome).

## Audit and preservation

The project had no .git, .gitignore, dependency files or remote/branch. The main README still described Phase 7-only status; it was rewritten with current verified scope and explicit pending Power BI work. Git was NOT initialized in the project. A disposable scratch repository only tested ignore semantics.

All 353 pre-existing files were snapshotted. README.md is the only authorized modification; the other 352 files remain byte-identical. No approved CSV, PostgreSQL object, financial assumption, existing PBIX, Phase 8/9 file, historical backup or report was modified/deleted. Duplicate/intermediate reports are retained locally but excluded where unnecessary for public reproduction.

No credential candidates were found by the configured text patterns; five in-memory positive controls proved those patterns detect their intended categories without saving values. Eleven ignore probes protect secret/private paths and retain necessary staging/processed inputs. Personal home paths are absent from the prospective public profile. Generic default Windows client paths remain documented. Opaque PBIX/XLSX contents and Git history are not certified; binaries are withheld and no Git history exists here. No public artifact exceeds the 50 MiB warning threshold (the inspected project is roughly 7 MB).

## Exclusions and reproducibility

.gitignore withholds credentials, caches/environments, external raw data (redistribution rights unverified), backups, PBIX/PBIT/dumps, local report pointers, verbose snapshots/logs and generated ZIPs. It retains source code, tests, both synthetic CSV families, Phase 8/9 inputs and selected compact financial/analysis evidence. Legacy processed CSVs are needed by regression tests; deleting them would break reproduction. The private Phase 7 run index links local logs, so current public findings/financial acceptance replace that navigation while originals remain untouched.

Requirements match the executed Python 3.12 environment; fresh pip installation/other OSes were not tested. Published release pages were checked. Missing local pointer files are recreated only on a fresh clone/extraction; old pointers are preserved. The recommended acceptance runner copies the public profile into a disposable workspace so historical whole-project hash guards are not bypassed or overwritten after the README change.

## Acceptance executed

Six jobs passed: 61 Python regressions; 16 SQL business queries/83 analytics gates; Phase 9A source/static mapping; 66 scenario outcomes/33 zero-baseline comparisons; 15 scenario unit/static tests; 19 CSV/160,078 row constraints plus SQL AST checks. All 36 live model checks and 33 financial baseline comparisons passed; annual cross-analysis totals and 132 scenario delta comparisons passed. Full counts are in acceptance_results.json.

The first launcher attempt stopped at a missing pglast import because an isolated parser-path argument was not forwarded to SQL analytics. The new launcher was corrected, the failed attempt was retained privately, and the complete suite passed. No failed financial validation was suppressed or adjusted.

Read-only before/after database checks in the source validators confirmed the 23 public/v2 tables and definitions unchanged. No data generation, migration setup or Power BI execution occurred.

## Independent handover

The single docs/POWER_BI_START_HERE.md guide includes software/authentication, exact import/table mappings, every relationship, Date configuration, all 120 core measure names/order, final 22 scenario names/order, six parameters, pages/visuals/slicers, financial targets, edge tests, troubleshooting and later save/publication steps. All code/data/reference assets needed by that scope are included in the public profile. The offline ZIP has a per-file SHA-256 manifest and external ZIP checksum; installers/wheels are not bundled.

## Remaining human decisions/actions

Power BI connector/M/DAX execution, relationship/filter/inventory behavior, scenario matrix, refresh and visuals still need Desktop acceptance; save a new PBIX only afterward. Native single-value slider availability is untested, with a single-select dropdown fallback fully documented. Repository URL/visibility/branch and license are not chosen. Raw redistribution rights are unresolved but raw files are excluded. No commit/push/publication/force-push or history rewrite was performed.

See FILE_CHANGES.md, audit_summary.json and acceptance_results.json. Private snapshots/execution logs stay on disk. The generated handover path is handover/Manufacturing_360_PowerBI_Handover.zip, excluded from Git to avoid duplicating the repository.

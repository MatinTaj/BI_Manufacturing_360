# Final acceptance — 25 October 2026

## A. Completed and validated

The final suite ran from a disposable copy of the prospective public-file profile, with external raw files, backups, PBIX and old machine-local report pointers absent. Missing-pointer bootstrap succeeded. Actual SQL used the existing manufacturing_360.manufacturing_v2 database read-only; no schema setup or generation was executed.

| Check | Result |
|---|---:|
| Python regression tests | 61 passed |
| SQL model integrity checks | 36 passed |
| Approved financial comparisons | 33 passed |
| SQL business queries | 16 executed |
| Analytics quality gates | 83 passed |
| Annual cross-analysis reconciliations | 22 passed |
| Scenario-period outcomes | 66 passed |
| Zero-scenario baseline comparisons | 33 passed |
| Independent scenario profit-delta comparisons | 132 passed |
| Scenario unit tests | 15 passed |
| Prepared relationship source mappings | 34 verified |
| CSV tables / row CHECK evaluations | 19 / 160,078 passed |

The original Phase 7 reproducibility record contains matching 19-file generation hash sets; generation was not repeated in Phase 10. The first new acceptance-launcher attempt omitted the isolated parser path for SQL analytics; it stopped before those queries, was corrected, and the full suite passed. The failed-attempt record remains local; no financial check was waived.

The main README is the only modified pre-existing file. All other 352 original files remain byte-identical, including approved datasets, accounting code, SQL and Phase 8/9 deliverables/PBIX. No backup/report was deleted. Security/link/Git-ignore audit passed with no credential candidates, public personal-home paths or broken public/local Markdown file links. This is a pattern-based audit, not a forensic binary/history guarantee. Git is not initialized, so there is no branch, remote or tracked history to certify.

## B. Prepared, not executed in Power BI

The final build inputs are ready: 19 core tables plus six disconnected parameters, 34 relationships, 120 core measures plus 22 final scenario measures, M source scripts and reconciliation queries. This preparation does not establish DAX/M compilation, Desktop refresh, semantic-model behavior or completed dashboards. No Power BI execution result or real-company business impact is claimed.

## C. Manual work after any AI subscription expires

Follow [POWER_BI_START_HERE](POWER_BI_START_HERE.md): install/verify software, connect securely, import in order, configure relationships/Date, create core measures, apply the final scenario overlay and test all financial/filter/snapshot results. Then build visuals, repeat refresh and save a NEW PBIX. Review permissions/credentials and service/gateway/account requirements before optional publication.

No additional AI service is required to read/paste the supplied project files. Third-party installers, Python wheels and credentials are not in the ZIP; obtain/install prerequisites before fully offline work. The provided reference tests do not replace Desktop acceptance.

## Publication status

The public profile is prepared for human review, not automatically published. Choose repository/visibility/branch and a license explicitly; raw-data redistribution rights remain unresolved and raw files are withheld. Generic Windows/default-client assumptions and untested fresh installs/other OSes are documented. [Publication checklist and proposed commands](GITHUB_PUBLICATION_CHECKLIST.md) require approval before commit/push. No project git init, commit, push, force-push or history rewrite was performed.

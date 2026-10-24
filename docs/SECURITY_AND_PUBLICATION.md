# Security and public-repository policy

The audit is a pattern-based text scan and file-policy review, not a forensic guarantee. No credential candidates were found in the inspected project text. Opaque PBIX contents and nonexistent Git history cannot be certified; PBIX files are excluded. Credentials must remain in local PostgreSQL/Power BI credential stores outside the repository.

## Retain publicly

Source code, tests, current/historical technical docs, Phase 8/9 preparation assets, approved 19 staging CSVs, legacy processed CSVs needed by regression tests, and compact financial/analysis evidence. Both CSV families are synthetic and clearly separated. Input hashes and the Phase 7 financial comparison remain available so validators do not depend on deleted inputs.

## Exclude without deleting

- .env variants, pgpass/service credential files, private keys and credential/secret-named files.
- Python environments/caches, editor/runtime settings, logs and temporary files.
- data/backups and temporary regeneration directories; originals stay on disk.
- data/raw: external source provenance/licensing was not established, and these are not financial-generation inputs.
- PBIX/PBIT binaries and database dumps: avoid binary connection metadata/unreviewed contents; no completed v2 dashboard claim.
- Local report pointers and verbose data/definition/hash snapshots; bootstrap missing pointers on another machine with scripts/configure_local_handover.py.
- The original Phase 7 run index (links private machine-local logs); current public acceptance/economic/financial evidence replaces that navigation, not the retained original files.
- Generated handover ZIP/checksum: local deliverable, not committed duplicate project content.

No original backup/report or validated Phase 8/9 file was deleted. Generic Windows PostgreSQL client paths remain documented defaults, not personal home paths or a cross-platform claim. Personal home paths are not allowed in the prospective public profile. .gitignore is tested using dummy filenames in a disposable scratch Git repo; the project itself is not initialized.

An ignore rule does not remove a file already tracked in Git and cannot purge history. The audit stops if an excluded file is already tracked, or a credential candidate/public home path appears. No history was available here because the project has no .git. Review again after initialization and before staging. No commit/push/force-push/history rewrite is automated.

External raw-data rights and the project license are unresolved publication decisions: raw files are withheld, and no open-source license was invented. Choose an appropriate project license explicitly before claiming one. No large public file exceeded 50 MiB in the inspected snapshot; Git LFS is not currently needed for this source/data profile.

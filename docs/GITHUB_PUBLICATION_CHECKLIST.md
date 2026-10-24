# GitHub publication approval checklist

Audit state: this project folder has no Git repository, current branch or configured remote. No commit, push or publication has occurred. A temporary scratch Git repository was used only to test ignore rules. Target GitHub owner/repository and branch choice need your approval.

## Before approval

- [ ] Read README and FINAL_ACCEPTANCE; Power BI runtime/dashboard remains pending.
- [ ] Review scripts/audit_repository.py output and .gitignore exclusions; credentials remain outside the project.
- [ ] Retain staged AND processed synthetic CSVs; do not publish external raw files, backups, PBIX or local logs/pointers.
- [ ] Confirm no confidential/company data or third-party assets were added since the audit.
- [ ] Choose an explicit license; no license grant was assumed. Raw redistribution rights are unverified and raw files are excluded.
- [ ] Select your GitHub repository URL/visibility and approved branch. No destination is invented here.
- [ ] Review every prospective staged file and rerun tests/audit before committing.

## Proposed commands — NOT executed

Run only after reviewing/approving the corresponding steps. A fresh main branch is a proposal, not an existing branch.

```powershell
git init -b main
git status --short --branch
python -B scripts/audit_repository.py
git add --dry-run .
# Inspect the dry-run list before any actual staging.
git add .
git diff --cached --name-only
git diff --cached --check
git diff --cached --stat
# Commit and push require explicit publication approval.
git commit -m "Add validated manufacturing BI portfolio and Power BI handover"
git remote add origin https://github.com/APPROVED_OWNER/APPROVED_REPOSITORY.git
git remote -v
git push -u origin main
```

Replace the URL with your approved destination; never include a token/password in it. If the remote already has commits or the push is rejected, stop and review rather than force-push or rewrite history. If sensitive content is found, stop and follow a deliberate credential/history response; ignore rules alone are insufficient. No Git command above was run against this project during Phase 10.

Publishing a future PBIX/report is a separate decision after Desktop acceptance and credential/data review. The current public profile deliberately excludes all PBIX files.

# Contributing — farmer-health (GA pipeline)

Locked path for all changes to `main`:

**Issue → branch → code (+ tests) → docs → draft PR → CI → review → squash merge → CD (manual)**

## 1. Issue first
- Open a **Bug** or **Feature / task** issue (templates required).
- Fill acceptance criteria. No issue → no PR.

## 2. Branch
From latest `main`:

```bash
git fetch origin
git checkout -b <issue-number>-short-slug origin/main
# e.g. 42-fix-health-survey-filter
```

## 3. Code + tests + docs
- Add/update automated tests for behavior changes in the **same PR**.
- Update README / env / deploy notes in the **same PR** when user-facing or ops behavior changes.
- Docs-only or chore: mark tests N/A in the PR template; the CI **Test** smoke check must still pass.

## 4. Pull request
- Open as **Draft** until CI is green and you’re ready for humans.
- PR template must include `Closes #<issue>` (or `Fixes #<issue>`).
- Linked-issue check fails the PR if the body has no issue reference and the branch is not named from an issue.

## 5. Review & merge
- At least **1 approving review** from a CODEOWNER.
- Stale approvals dismiss on new pushes; conversations must be resolved.
- Required checks: **Test**, **Linked issue** (must be green).
- **Squash merge** only; branch auto-deletes after merge.
- Do not approve your own last push; another reviewer must approve after the final push.

## 6. Deploy
- Production deploy is **manual** (`workflow_dispatch` on CD) after secrets + `production` environment are set.
- Do not push directly to `main` (ruleset blocks it except org-admin break-glass).

## Local commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py test
```

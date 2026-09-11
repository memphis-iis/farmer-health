# AGENTS.md

Guidance for LLM coding agents (Cursor, Copilot, Claude, etc.) working in this repo.

## What this repo is

**farmer-health** is an IIS Django/Python project repository. Governance, CI, and contribution rules live here from day one; application code will grow under this tree.

| Path | Role |
|------|------|
| `config/` | Django project settings, urls, wsgi/asgi |
| `tests/` | Automated tests (bootstrap smoke + future app tests) |
| `.github/` | CI/CD, CODEOWNERS, issue/PR templates |
| `CONTRIBUTING.md` | Human contribution pipeline (read this) |

## Hard rules (do not bypass)

1. **No direct commits to `main`.** Use the GA pipeline: issue → branch → PR → review → squash merge.
2. **Every change needs an issue.** Branch as `<issue-number>-short-slug`. PR body must include `Closes #<n>` (or `Fixes #<n>`).
3. **Do not commit secrets.** Never commit `.env`, API keys, SSH keys, or production credentials. Use `.env.example` as the template only when one exists.
4. **Do not expand scope.** Touch only files required for the task. No drive-by refactors, unrelated lint cleanup, or extra markdown unless asked.
5. **Do not invent deploy/prod changes** unless the task is explicitly about deploy/CI. Production deploy is manual (`workflow_dispatch` on CD) and needs IIS secrets.
6. **Tests are required** for behavior changes. Do not skip or delete the CI **Test** gate.
7. **Match existing style.** Prefer patterns already in the repo. Do not introduce new libraries without a clear need stated in the issue.

## Pipeline agents must follow

```text
Issue → branch (<id>-slug) → code + tests (+ docs if needed) → draft PR → CI green → CODEOWNER review → squash merge → CD (manual)
```

Required checks on PRs: **Test**, **Linked issue**.  
Merge method: **squash only**. Branches delete on merge.

Details: [CONTRIBUTING.md](./CONTRIBUTING.md).

## Environment & commands

Python **3.12+** (CI uses 3.12). Django **5.2**.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py test
```

## How to make a change (agent checklist)

1. Confirm or create a GitHub issue with clear acceptance criteria.
2. `git fetch origin && git checkout -b <id>-short-slug origin/main`
3. Implement the smallest change that meets acceptance criteria.
4. Add/update tests for behavior changes.
5. Update README / env / deploy notes **in the same PR** when user-facing or ops behavior changes; otherwise mark docs N/A in the PR template.
6. Open a **draft** PR with the template filled and `Closes #<id>`.
7. Ensure **Test** and **Linked issue** are green; then mark ready for review.
8. Do not merge your own PR unless policy and CODEOWNER review allow; prefer human CODEOWNER approval.

## What agents should ask humans about

- Production secrets, IIS SSH, or network/deploy changes
- Auth configuration that affects real users
- Broad dependency upgrades or major framework bumps

# farmer-health

IIS farmer-health repository (Django / Python).

## Contributing

All changes follow the GA pipeline: **issue → branch → PR → review → squash merge**.

See [CONTRIBUTING.md](./CONTRIBUTING.md). Agents: see [AGENTS.md](./AGENTS.md).

## Local setup

Python **3.12+** recommended (CI uses 3.12).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional local overrides
python manage.py test
python manage.py runserver
```
## Draft questionnaire questions (dev and demo only)

These ten questions are drafts for development. They will be replaced by the
validated set from the sponsor's independent study. Do not load them into a
real deployment.

```bash
python manage.py migrate
python manage.py seed_questions
```

Safe to run more than once: it updates the questions in place and never
creates duplicates.
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

# BuildLog

BuildLog is a digital journal for construction sites, built with Django.
It follows the works on a site from excavation to handover: which activities are planned,
which contractors carry them out, how far they have progressed and which inspection
findings are still open.

> The project is under active development. This file is extended as features are added.

## Planned features

- Construction sites identified by their construction permit
- Contractors with their main trade
- Work activities grouped by construction stage, with progress reporting
- Inspection findings with severity, deadline and resolution

## Requirements

- Python 3.12 or newer
- Django 6.1 (installed from `requirements.txt`)

## Run the project locally

```bash
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

## Run the tests

```bash
python manage.py test
```

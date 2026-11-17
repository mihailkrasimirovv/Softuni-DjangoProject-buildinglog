# BuildLog - construction site journal

BuildLog is a Django web application for following construction works from excavation
to handover. It answers the questions that come up on a building site every day:

- Which works are running late, and on which site?
- Which contractor is responsible for them?
- Which inspection findings are still not fixed, and which of them are overdue?

It is a course project for the Django Basics course.

## Features

| Area | What you can do |
| --- | --- |
| **Construction sites** | Register a site with its construction permit, type, investor, area and deadlines. Search, filter by status, sort and page through the list. See the overall progress of each site. |
| **Contractors** | Keep the companies you work with: EIK, main trade, contact person. Filter by trade and availability. |
| **Work activities** | Plan works by construction stage (excavation, foundations, structure, ...), assign several contractors, report progress. The state (upcoming / in progress / delayed / completed) is calculated automatically. |
| **Inspections** | Record findings from site inspections with severity and deadline, resolve them with a note, reopen them if needed. |
| **Dashboard** | Key figures, sites with the nearest deadlines, progress by construction stage and the latest open findings. |
| **CSV report** | Download the activities of a site as a CSV progress report that opens in Excel. |

Business rules enforced by the application:

- A permit number and a company EIK are unique and become read-only after registration.
- An activity cannot start before its site, cannot be moved to another site and its title
  is unique within the site.
- Only active contractors can be assigned to activities; a contractor with unfinished
  activities cannot be deactivated.
- A site can be marked as completed only when all of its activities are at 100%.
- A critical finding must have a deadline; an inspection cannot be dated in the future.
- Activities with recorded inspections (and their sites) cannot be deleted.

## Technologies

- Python 3.12+
- Django 6.1 (class-based views, Django Template Engine, ModelForms)
- SQLite
- Bootstrap 5.3 and Bootstrap Icons (loaded from a CDN) plus a small custom stylesheet

No other third-party packages are required.

## Getting started

Requirements: Python 3.12 or newer and Git.

```bash
# 1. Clone the repository and enter the project folder
git clone <repository-url>
cd <repository-folder>

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # macOS / Linux

# 3. Install the dependencies
pip install -r requirements.txt

# 4. Create the database
python manage.py migrate

# 5. Start the development server
python manage.py runserver
```

Open http://127.0.0.1:8000/ in a browser.

The database starts empty. Everything is created from the user interface - there are no
fixtures, no data migrations and the admin panel is not needed.

### Suggested first steps

1. **Add new -> Construction site** (the permit number looks like `RS-145/2026`).
2. **Add new -> Contractor** (the EIK has 9 or 13 digits).
3. Open the site and press **Add activity**; tick the contractor to assign it.
4. Open the activity, press **Edit / report progress**, then **Record inspection**.
5. Open the inspection and press **Resolve**. Go back to the site and download the **CSV report**.

## Environment variables

The project runs with its default configuration; **no environment variables or
credentials are required**. The following optional variables can change the defaults:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DJANGO_DEBUG` | `False` | Set to `True` to see Django's debug pages. It is off by default so that the custom 404 page is displayed. |
| `DJANGO_SECRET_KEY` | a development-only key | Secret key used by Django. Set your own value outside local testing. |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma separated list of host names the site may be served from. |

Examples:

```bash
set DJANGO_DEBUG=True              # Windows (cmd)
$env:DJANGO_DEBUG = "True"         # Windows (PowerShell)
export DJANGO_DEBUG=True           # macOS / Linux
```

Because `DEBUG` is off by default, static files are served by an explicit URL pattern in
`buildlog/urls.py`, so `python manage.py runserver` works without extra flags.

## Project structure

```
buildlog/        project settings and root URL configuration
common/          home/dashboard, about page, shared mixins, validators, template tags
sites/           construction sites
contractors/     contractor companies
works/           work activities and the CSV report
inspections/     inspection findings and their resolution
templates/       base template, reusable partials and the pages of every app
static/css/      custom stylesheet
```

Each app has its own `models.py`, `forms.py`, `views.py`, `urls.py`, `admin.py` and a
`tests/` package.

### Data model

| Model | App | Relationships |
| --- | --- | --- |
| `ConstructionSite` | `sites` | has many `WorkActivity` |
| `Contractor` | `contractors` | many-to-many with `WorkActivity` |
| `WorkActivity` | `works` | many-to-one to `ConstructionSite` (cascade), many-to-many with `Contractor` |
| `Inspection` | `inspections` | many-to-one to `WorkActivity` (protected) |

All models inherit the abstract `TimeStampedModel` (`created_at`, `updated_at`) from the
`common` app. Values that can be calculated are not stored in the database - they are
properties of the models, for example `ConstructionSite.progress` and `WorkActivity.state`.

### Pages

| Section | Pages |
| --- | --- |
| Common | dashboard, about, custom 404 and 500 pages |
| Sites | list (search / filter / sort / pagination), details, create, edit, delete confirmation |
| Contractors | list (search / filter / pagination), details, create, edit, delete confirmation |
| Activities | list (search / filter / sort / pagination), details, create, edit, delete confirmation, CSV report |
| Inspections | list (filter / sort / pagination), details, create, edit, resolve, delete confirmation |

Every page is reachable from the navigation bar, the "Add new" menu or links on the pages
themselves. The test in `common/tests/test_navigation.py` opens every page and checks that
it has the navigation bar and the footer.

### Forms and validation

- Create and edit forms for all four models, a resolve form for inspections, read-only
  summary forms on the delete confirmation pages and GET filter forms on the list pages.
- Custom labels, help texts, placeholders and error messages.
- Read-only (disabled) fields: permit number, EIK, the site of an activity, the activity
  of an inspection and the finding fields of the resolve form.
- Validation in the models (validators, unique and check constraints, `clean()`), and in
  the forms (`clean_<field>()` and `clean()` for rules that involve several fields).

### Template features

- Template inheritance from `templates/base.html` and reusable partials in
  `templates/partials/` (navigation bar, footer, messages, form fields, filter form,
  pagination, site card, activity table, inspection item, delete confirmation).
- Custom filters and tags in `common/templatetags/buildlog_tags.py`:
  `badge_class`, `deadline_label` and the `progress_bar` inclusion tag.
- Built-in filters and tags such as `date`, `timesince`, `pluralize`, `truncatechars`,
  `floatformat`, `linebreaksbr`, `urlize`, `default`, `querystring` and `now`.

## Running the tests

```bash
python manage.py test
```

There are tests for the models, the forms, the views, the template tags, the dashboard
and the CSV report.

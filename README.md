# Django-Octo QA

**Unified Django quality assurance and automated test orchestrator (Pytest, Behave BDD, and Locust) under the Django-Octo ecosystem.**

`django-octo-qa` automatically discovers unit tests (`pytest`), behavioral specifications (`behave`), and load test suites (`locust`) across your Django apps and executes them safely from the Django Admin with persistent execution history.

## Features

- **Granular Test Discovery:** Scans installed apps and project roots to list individual Pytest functions, Behave scenarios, and Locust user classes.
- **On-Demand Execution:** Run individual test cases or full suites directly from **Admin -> QA -> Quality Assurance**.
- **Execution History & Log Viewer:** Stores timestamps, target scope, duration, status badges, full console logs (with one-click copy), and downloadable Locust HTML reports.
- **Production Safety Guardrails:** Restricted to superusers and requires `OCTO_QA_ALLOW_RUNNER = True` (enabled automatically when `DEBUG = True`).

## Installation

```bash
pip install django-octo-qa
```

## Quick Start

1. Add `django_octo_qa` to `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.admin",
    "django_octo_qa",
]
```

2. Run migrations:

```bash
python manage.py migrate django_octo_qa
```

3. Open **Admin -> QA -> Quality Assurance** to inspect discovered tests and run suites.

## License

MIT License.

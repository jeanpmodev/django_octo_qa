# Django-Octo QA
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Framework: Django](https://img.shields.io/badge/Framework-Django-darkgreen)](https://djangoproject.com)
[![Package Manager: Rye](https://img.shields.io/badge/Package_Manager-Rye-orange)](https://astral.sh)
![PyPI Version](https://img.shields.io/pypi/v/django_octo_qa)
[![Latest on Django Packages](https://img.shields.io/badge/Django_Packages-django__octo__qa-8c3c26.svg)](https://djangopackages.org/packages/p/django_octo_qa/)
[![Tests: pytest](https://img.shields.io/badge/Tests-pytest%20passed-2ea44f.svg)](https://github.com/jeanpmodev/django_octo_qa/blob/main/TESTING.md)
[![BDD: Behave](https://img.shields.io/badge/BDD-Behave%20verified-009688.svg)](https://github.com/jeanpmodev/django_octo_qa/blob/main/TESTING.md)
[![Load Test: Locust](https://img.shields.io/badge/Load_Test-11ms_median_%7C_0%25_fails-blueviolet.svg)](https://github.com/jeanpmodev/django_octo_qa/blob/main/performance/locust_load_report.pdf)
[![CI](https://img.shields.io/github/actions/workflow/status/jeanpmodev/django_octo_qa/ci.yml?branch=main&label=CI)](https://github.com/jeanpmodev/django_octo_qa/actions/workflows/ci.yml)
[![Code Style: PEP 8](https://img.shields.io/badge/code%20style-PEP%208-blue)](https://peps.python.org/pep-0008/)
[![PyPI Provenance](https://img.shields.io/badge/PyPI-With%20Provenance-blue?logo=pypi&logoColor=white)](https://pypi.org/project/django-octo-qa/#provenance)
[![Snyk Vulnerabilities](https://img.shields.io/badge/Snyk%20Vulnerabilities-0%20known-brightgreen?logo=snyk&logoColor=white)](https://uml.snyk.io/package/pip/django-octo-qa)
[![security Audit](https://github.com/jeanpmodev/django_octo_qa/actions/workflows/security.yml/badge.svg)](https://github.com/jeanpmodev/django_octo_qa/actions/workflows/security.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/jeanpmodev/django_octo_qa/badge)](https://scorecard.dev/viewer/?uri=github.com/jeanpmodev/django_octo_qa)
[![Socket Badge](https://badge.socket.dev/pypi/package/django-octo-qa/0.1.0?artifact_id=tar-gz)](https://badge.socket.dev/pypi/package/django-octo-qa/0.1.0?artifact_id=tar-gz)
[![codecov](https://codecov.io/github/jeanpmodev/django_octo_qa/graph/badge.svg?token=YUOBIXZE9A)](https://codecov.io/github/jeanpmodev/django_octo_qa)
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

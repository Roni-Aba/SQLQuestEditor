# CLAUDE.md

Guidance for Claude Code and other AI coding assistants working in this repository.

## Project Overview

SQL Quest Editor is a Django-based web editor for working with SQL Spell Quest level data. The app currently uses server-rendered Django templates, Bootstrap from a CDN, static CSS files, and SQLite for local development.

The active Django project lives in `backend/`.

## Tech Stack

- Python with Django 4.2
- SQLite database at `backend/db.sqlite3` when created locally
- Django templates under `backend/editor/templates/`
- Static CSS and images under `backend/editor/static/`
- Bootstrap 5.3.2 loaded in `backend/editor/templates/editor/base.html`

## Common Commands

Run commands from the repository root unless noted otherwise.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Run tests:

```bash
cd backend
python manage.py test
```

Useful local URLs after starting the server:

- `http://127.0.0.1:8000/` - start page and JSON upload
- `http://127.0.0.1:8000/level/` - level overview
- `http://127.0.0.1:8000/createLevel/` - create-level wizard
- `http://127.0.0.1:8000/auswahl/` - selection step
- `http://127.0.0.1:8000/components/` - component test page

## Repository Structure

```text
backend/
  manage.py
  requirements.txt
  SQLSpellQuest.json
  config/
    settings.py
    urls.py
  editor/
    views.py
    urls.py
    templates/editor/
      base.html
      start.html
      level.html
      createLevel.html
      auswahl.html
      test.html
      components/
    static/editor/
      css/
      components/
      img/
documentation/
  Konvertierung/
  mockups/
StartPagePlugin.html
```

## Django App Notes

- Root URLs are included from `backend/config/urls.py` into `backend/editor/urls.py`.
- Views are simple function-based views in `backend/editor/views.py`.
- Templates extend `editor/base.html`.
- Shared UI fragments live under `backend/editor/templates/editor/components/`.
- Component-specific styles live under `backend/editor/static/editor/components/`.
- Page-specific styles live under `backend/editor/static/editor/css/`.

When adding a new page:

1. Add a view in `backend/editor/views.py`.
2. Add a route in `backend/editor/urls.py`.
3. Add a template under `backend/editor/templates/editor/`.
4. Extend `editor/base.html`.
5. Add page CSS under `backend/editor/static/editor/css/` and include it in the template's `additional_css` block.

## Template Conventions

Use Django template tags consistently:

```django
{% extends "editor/base.html" %}
{% load static %}

{% block title %}
Page Title | SQL Spell Quest Editor
{% endblock %}

{% block additional_css %}
<link rel="stylesheet" href="{% static 'editor/css/page.css' %}">
{% endblock %}

{% block content %}
...
{% endblock %}
```

Use `{% include %}` for reusable components, passing context explicitly with `with` when needed.

Example:

```django
{% include "editor/components/button/button.html" with title="Start" %}
```

Always prefer existing reusable components before creating new markup. Check
`backend/editor/templates/editor/components/` and
`backend/editor/static/editor/components/` first, then reuse or extend the
available component if it fits the task. Create a new component only when no
existing component can reasonably cover the UI need.

## Styling Conventions

- Prefer page-level classes such as `.start-page`, `.create-level-page`, and component-level classes for reusable elements.
- Keep component CSS next to the component directory under `static/editor/components/`.
- Keep page CSS in `static/editor/css/`.
- Bootstrap utility classes are already used; keep using them where they fit instead of duplicating simple layout rules.
- The UI language is primarily German, with some existing English labels. Match the surrounding page language when editing copy.

## Data Handling

- JSON upload is handled by `upload_json_view` in `backend/editor/views.py`.
- The sample game file is `backend/SQLSpellQuest.json`.
- Current code expects uploaded JSON to contain a top-level `level` array and reads each level's `id`.
- Validate uploaded JSON before expanding this flow; avoid assuming malformed input is safe.

## Testing Guidance

There are currently no meaningful tests in `backend/editor/tests.py`.

For backend changes, add focused Django tests for:

- URL routing and status codes
- Template rendering
- JSON upload success and error paths
- Invalid JSON handling when implemented

Run `python manage.py test` from `backend/` before finishing backend changes.

## Important Constraints

- Do not commit secrets or production credentials. `settings.py` currently contains a development-only `SECRET_KEY` and `DEBUG = True`.
- Keep changes scoped. This is a small app, so avoid adding frameworks, build tools, or large abstractions unless the task clearly requires them.
- Do not change existing URLs, routes, or URL names unless the user explicitly asks for it.
- Do not automatically modify existing `.html` files without explicit permission when implementing additional Figma designs.
- If multiple Figma designs map to the same base page name, create new templates with numbered names instead of overwriting the existing one. For additional `createLevel` designs, use `createLevel1.html`, `createLevel2.html`, `createLevel3.html`, and so on up to `createLevelN.html` for `N >= 1`.
- Do not move templates or static files without updating their Django references.
- Preserve user work in the repository. Check `git status --short` before making broad edits.

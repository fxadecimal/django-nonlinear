# Django-Nonlinear

## Manage your Django project inside your Django project


![screenshot.png](screenshot.png)


Overview
--------

Typically I use [TODO.md](https://github.com/todomd/todo.md) as my product management method. After working on ~5 person project with non-technical people, I needed a light-weight PM tool to add to an existing django project that wasn't Jira. On larger projects I'd recommend a more comprehensive tool.

Tries it's best to get out of your way so you can focus on building the product & not managing the tool.



Quick Start: Run Sample Project
------------------------------


```sh
git clone git@github.com:fxadecimal/django-nonlinear.git
cd django-nonlinear/sample_project

# (Optional) Create virtual environment
pip -m venv .venv 
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# Run test server
./manage.py migrate --noinput
./manage.py createsuperuser
./manage.py runserver
```

Create a new workspace & add yourself:

- [http://localhost:8000/admin/nonlinear/workspace/](http://localhost:8000/admin/nonlinear/workspace/)


Quick Start: Add to an existing Project:
----------------------------------------

```sh
# using your python environment
git clone git@github.com:fxadecimal/django-nonlinear.git
pip install ./django-nonlinear
```

Add dependencies to Django `settings.py`:

```py
INSTALLED_APPS = [
    ...
    "django.contrib.humanize",
    "markdownify.apps.MarkdownifyConfig",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "nonlinear",
]
```

Add to Django `urls.py`:

```py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("nonlinear/", include("nonlinear.urls")),
]
```

Migrate Nonlinear:

```sh
./manage.py migrate nonlinear
```

(optional) Collect Static: `./manage.py collectstatic`


Quickstart: Docker-compose
--------------------------

```sh
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```


Features
========


- Git branch name generator e.g. `workspace-1_create-gpt-5`
- Draggable task list (Sortable / HTMX)
- Multiple Workspaces supported
- Markdown Support
- Task Exporter Command: `./manage.py nonlinear_dump workspace_slug`


Planned Features
================

- User Comments
- Task Activity
- Project View
- Calendar View
- User Centric Lists
- DRF API


References
==========

- [Nearbeach](https://github.com/nearbeach/NearBeach/)
- [django-countries](https://github.com/SmileyChris/django-countries)
- [djangox](https://github.com/wsvincent/djangox)

from django.conf import settings
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from model_bakery import baker
from pprint import pprint

User = get_user_model()


from nonlinear.models import (
    Task,
    Workspace,
    Project,
    TASK_STAGES,
    PROJECT_STATUSES,
    TaskComment,
    TaskActivity,
    # TaskActivity,
    # TaskComment,
    # TaskLinkedGenericObject,
)

from common.utils import MD_LOREM

WORKSPACE_NAME = "Test Workspace"
WORKSPACE_SLUG = "wrk"


class Command(BaseCommand):

    def handle(self, *args, **options):
        # self.generate_test_data()
        self.generate_nonlinear_tasks()

    def generate_test_data(self, *args, **options):
        user = User.objects.first()

        workspace, _ = Workspace.objects.get_or_create(
            created_by=user,
            name=WORKSPACE_NAME,
            slug=WORKSPACE_SLUG,
            # add_sample_tasks=True,
        )

        pprint(workspace.__dict__)

        project = baker.make(
            Project,
            workspace=workspace,
            created_by=user,
            name="Test Project",
            description=MD_LOREM,
            _fill_optional=True,
        )

        parent_task = baker.make(
            Task,
            workspace=workspace,
            created_by=user,
            name="Parent Task",
            description=MD_LOREM,
            # _fill_optional=True,
        )

        counter = 0
        for stage in TASK_STAGES:
            stage = stage[0]
            for is_deleted in [True, False]:
                counter += 1
                task = baker.make(
                    Task,
                    workspace=workspace,
                    created_by=user,
                    name=f"Task {counter}: {stage}",
                    parent_task=parent_task,
                    description=MD_LOREM,
                    stage=stage,
                    _fill_optional=False,
                    is_deleted=is_deleted,
                )
                task.save()

                print(task)
                project.tasks.add(task)
                project.save()

                comments = baker.make(
                    TaskComment,
                    task=task,
                    created_by=user,
                    text="A comment",
                    _fill_optional=True,
                    _quantity=3,
                )
                comments[-1].is_deleted = True
                comments[-1].save()

                activities = baker.make(
                    TaskActivity,
                    task=task,
                    created_by=user,
                    verb="updated",
                    _quantity=3,
                    _fill_optional=True,
                )
                activities[-1].is_deleted = True
                activities[-1].save()

        pprint(project.__dict__)
        pprint(task.__dict__)
        pprint(workspace.__dict__)


    def generate_nonlinear_tasks(self):
        user = User.objects.first()

        workspace, _ = Workspace.objects.get_or_create(
            created_by=user,
            name="nonlinear",
            slug="nl",
        )
        workspace.users.add(user)
        workspace.save()


        ####################################
        # Dump / Load Too
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="MVP load and dump tool",
        )
        task.stage = "in_progress"
        task.description = "Basic json io serializer for named workspace."
        task.assigned_to.add(user)
        task.tags_csv = "function, test"
        task.save()

        ####################################
        # Sub Tasks
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Issue: Disable HTMX Polling on Sortatble dragstart",
        )
        task.stage = "todo"
        task.description = """
Artifact:

- Polling continues in the background & disables current drag operation

Todo:

- Sortable:onStart()
    - Disable Polling
- Idea: Create seperate Polling object & start/stop on drag

"""
        task.assigned_to.add(user)
        task.tags_csv = "ui, bug"
        task.save()


        ####################################
        # Admin Interface
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Nonlinear Admin Interface",
        )
        task.stage = "backlog"
        task.assigned_to.add(user)
        task.tags_csv = "feature, admin, ui"
        task.save()

        ####################################
        # Sub Tasks
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Create Realistic Test Data",
        )
        task.stage = "done"
        task.assigned_to.add(user)
        task.tags_csv = "test"
        task.save()

        ####################################
        # Python / Git Project
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Git / Python Project",
        )
        task.description=SETUP_PIPY_MD
        task.stage = "backlog"
        task.assigned_to.add(user)
        task.tags_csv = "non-functional, git"
        task.save()


        ####################################
        # Sub Tasks
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Sub Tasks",
        )
        task.assigned_to.add(user)
        task.tags_csv = "feature, ui"
        task.save()

        ####################################
        # Comments System
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Comments System",
        )
        task.description="""
- Add comments to tasks
- Edit comments using a modal / EasyMDE
- Delete Comments
- Create Activity for comments
            """
        task.tags_csv = "functional, comments, ui"
        task.save()


        ####################################
        # Activity System
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Activity System",
        )
        task.tags_csv = "functional, activity, ui"
        task.assigned_to.add(user)
        task.save()

        ####################################
        # Per User Task Ordering
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Per-User task ordering",
        )
        task.assigned_to.add(user)
        task.tags_csv = "feature, ui"
        task.save()


        ####################################
        # Light / Dark Mode
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Dark / Light Mode",
        )
        task.assigned_to.add(user)
        task.tags_csv = "ui"
        task.save()





        ####################################
        # Attachments
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Attachments System",
        )
        task.assigned_to.add(user)
        task.save()


        ####################################
        # Compact UI
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="More Compact UI",
        )
        task.assigned_to.add(user)
        task.tags_csv = "ui, design"
        task.save()

        ####################################
        # Public View
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Public view of tasks on workspace",
        )
        task.assigned_to.add(user)
        task.tags_csv = "feature, ui, design"
        task.save()

        ####################################
        # Project Management / Manager View
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Project Mangement/Manager View",
        )
        task.assigned_to.add(user)
        task.tags_csv = "user-role, feature, ui"
        task.save()

        ####################################
        # Tags
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Tags",
        )
        task.assigned_to.add(user)
        task.tags_csv = "refactor"
        task.save()

        ####################################
        # Inline edit features
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Inline Status Change",
        )
        task.assigned_to.add(user)
        task.tags_csv = "ui"
        task.save()

        ####################################
        # Dump / Load Tool
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="Dump / Load Tools",
        )
        task.assigned_to.add(user)
        task.tags_csv = "functional"
        task.save()


        ####################################
        # ChatGPT
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            created_by=user,
            name="ChatGPT Todo list generator",
        )
        task.assigned_to.add(user)
        task.tags_csv = "functional"
        task.save()




SETUP_PIPY_MD="""
Creating a Django project and publishing it on PyPI so that others can install it using `pip` involves several steps. Below is a step-by-step guide to achieve this:

**References:**

- https://github.com/jpadilla/django-project-template
- https://github.com/rochacbruno/python-project-template/tree/main
- https://forum.djangoproject.com/t/newbie-django-polls-tutorial-packaging-not-picking-up-templates-static-files/20292


### 1. Set Up Your Django Project

First, you need to create a Django project if you don't already have one.

```bash
django-admin startproject myproject
cd myproject
```

### 2. Prepare Your Project for Packaging

Ensure your Django project is structured correctly for packaging. Typically, the structure looks like this:

```
myproject/
    myproject/
        __init__.py
        settings.py
        urls.py
        wsgi.py
    manage.py
    setup.py
    README.md
```

### 3. Create `setup.py`

Create a `setup.py` file in the root directory of your project. This file is used by setuptools to package your project.

```python
from setuptools import find_packages, setup

setup(
    name='myproject',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.0',
        # Add other dependencies your project needs here
    ],
    entry_points={
        'console_scripts': [
            'myproject-manage = myproject.manage:main',
        ],
    },
)
```

### 4. Create a `MANIFEST.in`

A `MANIFEST.in` file is used to include additional files in your package that are not automatically included by `setuptools`.

```text
include myproject/*.py
recursive-include myproject/templates *
recursive-include myproject/static *
```

### 5. Create a `README.md`

Include a `README.md` file with your project. This file should describe your project and provide instructions on how to install and use it.

### 6. Test Your Setup

Before publishing your package, it's important to test it locally.

```bash
pip install -e .
```

This command will install your package in editable mode, allowing you to test it as if it were installed via `pip`.

### 7. Build Your Package

Use `setuptools` to build your package.

```bash
python setup.py sdist bdist_wheel
```

### 8. Upload Your Package to PyPI

First, ensure you have an account on [PyPI](https://pypi.org/).

Install `twine` if you haven't already:

```bash
pip install twine
```

Upload your package using `twine`:

```bash
twine upload dist/*
```

You will be prompted to enter your PyPI username and password.

### 9. Install Your Package

Once your package is published, you can install it using `pip`:

```bash
pip install myproject
```

### Additional Tips

- **Versioning**: Follow semantic versioning for your package versions.
- **Documentation**: Consider adding more documentation to your `README.md` or using tools like Sphinx to generate documentation.
- **Testing**: Include tests in your project and use CI/CD pipelines (like GitHub Actions, Travis CI) to automate testing and deployment.

### Example Project Structure with Files

**`setup.py`**

```python
from setuptools import find_packages, setup

setup(
    name='myproject',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.0',
        # Add other dependencies your project needs here
    ],
    entry_points={
        'console_scripts': [
            'myproject-manage = myproject.manage:main',
        ],
    },
)
```

**`MANIFEST.in`**

```text
include myproject/*.py
recursive-include myproject/templates *
recursive-include myproject/static *
```

**`README.md`**

```markdown
# MyProject

A simple Django project.

## Installation

```bash
pip install myproject
```

## Usage

To run the project:

```bash
myproject-manage runserver
```
```

By following these steps, you can create a Django project, package it, and make it available for installation via `pip` on PyPI.
"""
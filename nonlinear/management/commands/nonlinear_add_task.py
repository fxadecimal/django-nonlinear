from django.conf import settings
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management.base import CommandParser
from model_bakery import baker
from pprint import pprint

User = get_user_model()

from nonlinear.models import (
    Task,
    Workspace,
    Project,
    # TaskActivity,
    # TaskComment,
    # TaskLinkedGenericObject,
)

from common.utils import MD_LOREM


WORKSPACE_NAME = "Test Workspace"
WORKSPACE_SLUG = "wrk"

# nonlinear_add_task --workspace wrk --name "my task" --priority 1 --stage "backlog" --description "# Some Markdown etc"


class Command(BaseCommand):

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("name", type=str, help="Name of the task")
        parser.add_argument("--description", type=str, help="Description of the task")
        parser.add_argument("--workspace_slug", type=str, help="Slug of the workspace")
        parser.add_argument(
            "--task_priority", type=str, help="Type of the task", required=False
        )
        parser.add_argument(
            "--user_pk",
            type=str,
            help="user id of the task to be created",
            required=False,
        )
        parser.add_argument(
            "--user_email",
            type=str,
            help="user email of the task to be created",
            required=False,
        )

    def handle(self, *args, **options):

        # TODO: get arguments
        name = options["name"]
        task_description = options["name"]
        user_pk = options["user_pk"]
        user_email = options["user_email"]
        workspace_slug = options["workspace_slug"]

        workspace = Workspace.objects.get(slug=workspace_slug)

        user = None

        if user_pk:
            user = User.objects.get(id=user_pk)
        if user_email:
            user = User.objects.get(email=user_email)
        if user_email or user_pk:
            if user == None:
                raise ValueError("User not found")
        task = Task.objects.create(
            name=name,
            created_by=user,
            workspace=workspace,
        )
        task.task_description = task_description
        task.save()

        # task_type = options["name"]
        # task_stage = None
        # task_priority = None

        # task.task_type = task_type
        # task.task_stage = task_stage
        # task.task_priority = task_priority

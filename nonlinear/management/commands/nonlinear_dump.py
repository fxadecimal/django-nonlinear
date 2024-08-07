from django.conf import settings
from django.core.management import BaseCommand
from django.core.management.base import CommandParser
from pprint import pprint
import json
from django.core import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

from nonlinear.models import (
    Task,
    Workspace,
)

from nonlinear.serializers import serialize_workspace


class Command(BaseCommand):

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("workspace_slug", type=str, help="Slug of the workspace")
        parser.add_argument("--format", type=str, help="Output format", default="json")
        parser.add_argument(
            "--exclude-deleted", action="store_true", help="input as JSON"
        )

    def handle(self, *args, **options):
        format = options["format"]
        workspace_slug = options["workspace_slug"]
        exclude_deleted = options["exclude_deleted"]

        workspace = Workspace.objects.get(slug=workspace_slug)

        if format == "json":
            data = serialize_workspace(workspace, exclude_deleted=exclude_deleted)
            print(json.dumps(data, indent=4))

        if format == "yaml":
            import yaml

            data = serialize_workspace(workspace, exclude_deleted=exclude_deleted)
            print(yaml.dump(data))

        if format == "csv":
            raise NotImplementedError("CSV format is not implemented yet")

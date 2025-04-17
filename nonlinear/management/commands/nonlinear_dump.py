from django.conf import settings
from django.core.management import BaseCommand
from django.core.management.base import CommandError

from django.contrib.auth import get_user_model

User = get_user_model()

import json

from nonlinear.utils import serailize_workspace
import csv
import io
from django.utils import timezone


MARKDOWN_WORKSPACE_TEMPLATE = """% Nonlinear Markdown Export
% workspace: {name}
% slug: {slug}
% created_at: {created_at}
% updated_at: {updated_at}
% generated_at: {generated_at}


# {name}

"""

MARKDOWN_TASK_TEMPLATE = """

## Task: {workspace_slug}-{workspace_order}: {name}

|Key|Value|
|-|-|
|priority|{priority}|
|status|{status}|
|tags|{tags}|
|start_date|{start_date}|
|end_date|{end_date}|
|started_date|{started_date}|
|ended_date|{ended_date}|


**Description:**

---

{description}


---

"""


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "workspace_slug",
            type=str,
            help="The slug of the workspace to dump data from.",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["json", "yaml", "md", "csv"],
            default="json",
            help="Output format (json or yaml)",
        )

    def handle(self, *args, **options):

        format = options["format"]
        workspace_slug = options["workspace_slug"]

        workspace_dict = serailize_workspace(workspace_slug=workspace_slug)

        if format == "json":
            output = json.dumps(workspace_dict, indent=4)

        elif format == "yaml":
            import yaml

            output = yaml.dump(workspace_dict, default_flow_style=False)

        elif format == "csv":
            tasks = workspace_dict["tasks"]

            fieldnames = ["index", "id"] + sorted(tasks[0]["fields"].keys())
            fieldnames.remove("description")
            fieldnames.append("description")

            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=fieldnames,
                quoting=csv.QUOTE_ALL,
            )
            writer.writeheader()

            for i, task in enumerate(tasks):
                fields = task["fields"]
                fields["index"] = i + 1
                fields["id"] = task["pk"]
                fields["description"] = (
                    fields["description"].replace("\n", "\\n")
                    if fields["description"]
                    else ""
                )
                writer.writerow(fields)
            output.seek(0)
            output = output.getvalue()

        elif format == "md":
            workspace_fields = workspace_dict["workspace"][0].get("fields", {})
            workspace_fields["id"] = workspace_dict["workspace"][0]["pk"]
            workspace_fields["generated_at"] = timezone.now().isoformat()
            output = MARKDOWN_WORKSPACE_TEMPLATE.format(**workspace_fields)

            for i, task in enumerate(workspace_dict["tasks"]):
                task_fields = task["fields"]
                task_fields["id"] = task["pk"]
                task_fields["workspace_slug"] = workspace_fields["slug"]
                output += MARKDOWN_TASK_TEMPLATE.format(**task_fields)

        self.stdout.write(output)

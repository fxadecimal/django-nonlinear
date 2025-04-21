import json
from django.contrib.auth import get_user_model

User = get_user_model()

from nonlinear.models import TaskComment, Tag, Task, Workspace
from django.core.serializers import serialize


def serailize_workspace(workspace_slug=None, workspace=None):

    def _dserialize(obj, **options):
        return json.loads(serialize("json", obj, **options))

    if not workspace:
        workspace = Workspace.objects.filter(slug=workspace_slug).first()

    if not workspace:
        raise ValueError(f"Workspace with slug '{workspace_slug}' does not exist.")

    tasks = Task.objects.filter(workspace=workspace)
    users = workspace.users.all()
    tags = Tag.objects.filter(workspace=workspace)
    task_comments = TaskComment.objects.filter(task__workspace=workspace)

    data = {
        "workspace": _dserialize([workspace]),
        "tasks": _dserialize(tasks),
        "users": _dserialize(users),
        "tags": _dserialize(tags),
        "task_comments": _dserialize(task_comments),
    }
    return data

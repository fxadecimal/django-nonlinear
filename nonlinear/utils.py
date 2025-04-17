import json
from django.contrib.auth import get_user_model

User = get_user_model()

from nonlinear.models import TaskComment, Tag, Task, Workspace
from django.core.serializers import serialize


def serailize_workspace(workspace_slug=None, workspace=None):

    if not workspace:
        workspace = Workspace.objects.filter(slug=workspace_slug).first()

    if not workspace:
        raise ValueError(f"Workspace with slug '{workspace_slug}' does not exist.")

    tasks = Task.objects.filter(workspace=workspace)
    users = workspace.users.all()
    tags = Tag.objects.filter(workspace=workspace)
    task_comments = TaskComment.objects.filter(task__workspace=workspace)

    data = {
        "workspace": json.loads(serialize("json", [workspace])),
        "tasks": json.loads(serialize("json", tasks)),
        "users": json.loads(serialize("json", users)),
        "tags": json.loads(serialize("json", tags)),
        "task_comments": json.loads(serialize("json", task_comments)),
    }
    return data

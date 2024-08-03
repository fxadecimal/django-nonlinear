from pprint import pprint
import json
from django.core import serializers
from nonlinear.models import TaskComment, TaskActivity, Task


def serialize_workspace(
    workspace, exclude_deleted=False, include_comments=True, include_activities=True
):
    comments = TaskComment.objects.get_queryset_all().filter(
        task__workspace_id=workspace.id
    )
    activities = TaskActivity.objects.get_queryset_all().filter(
        task__workspace_id=workspace.id
    )
    tasks = Task.objects.get_queryset_all().filter(workspace_id=workspace.id)

    if exclude_deleted == False:
        comments = comments.filter(is_deleted=False)
        activities = activities.filter(is_deleted=False)
        tasks = tasks.filter(is_deleted=False)

    # work around: serialize, deserialize, then use json lib to reserialize
    workspace_serialized = serializers.serialize("json", [workspace])
    tasks_serialized = serializers.serialize("json", tasks)
    comments_serialized = serializers.serialize("json", comments.all())
    activites_serialized = serializers.serialize("json", activities.all())

    _tasks = json.loads(tasks_serialized)
    _workspace = json.loads(workspace_serialized)
    _comments = json.loads(comments_serialized)
    _activites = json.loads(activites_serialized)

    # combine
    output = [
        *_workspace,
        *_tasks,
    ]

    if include_comments:
        output.extend(_comments)

    if include_activities:
        output.extend(_activites)

    return output

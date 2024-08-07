from pprint import pprint
import json
from django.core import serializers
from nonlinear.models import TaskComment, TaskActivity, Task


def serialize_deserialize(
    objects, use_natural_foreign_keys=False, use_natural_primary_keys=False, fields=None
):
    # work around: serialize, deserialize
    return json.loads(
        serializers.serialize(
            "json",
            objects,
            use_natural_foreign_keys=use_natural_foreign_keys,
            use_natural_primary_keys=use_natural_primary_keys,
            fields=fields,
        )
    )


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

    workspace_list = serialize_deserialize([workspace])
    tasks_list = serialize_deserialize(tasks)

    # combine
    output = [
        *workspace_list,
        *tasks_list,
    ]

    if include_comments:
        comments_list = serialize_deserialize(comments.all())
        output.extend(comments_list)

    if include_activities:
        activities_list = serialize_deserialize(activities.all())
        output.extend(activities_list)

    return output

from pprint import pprint
import json
from django.core import serializers
from nonlinear.models import TaskComment, TaskActivity, Task


def _serialize_deserialize(objects):
    # work around: serialize, deserialize
    return json.loads(serializers.serialize("json", objects))

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

    workspace_list = _serialize_deserialize([workspace])
    tasks_list = _serialize_deserialize(tasks) 

    # combine
    output = [
        *workspace_list,
        *tasks_list,
    ]

    if include_comments:
        comments_list = _serialize_deserialize(comments.all()) 
        output.extend(comments_list)

    if include_activities:
        activities_list = _serialize_deserialize(activities.all()) 
        output.extend(activities_list)

    return output

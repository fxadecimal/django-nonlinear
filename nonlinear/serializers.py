from django.contrib.auth import get_user_model

User = get_user_model()

from nonlinear.models import TaskComment, Tag, Task, Workspace
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["id", "slug", "created_at", "updated_at"]
        extra_kwargs = {
            "description": {"required": False},
            "due_date": {"required": False},
            "tags": {"required": False},
        }

    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    )
    workspace = serializers.PrimaryKeyRelatedField(queryset=Workspace.objects.all())
    # assigned_to = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.all(), required=False
    # )


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = "__all__"
        read_only_fields = ["id", "slug"]

    tasks = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    )
    workspace = serializers.PrimaryKeyRelatedField(queryset=Workspace.objects.all())

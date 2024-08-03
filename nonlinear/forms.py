from django import forms
from .models import Task


def datetime_split_widget(required=False):
    return forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_format="%Y-%m-%d",
            time_format="%H:%M",
            date_attrs={"type": "date"},
            time_attrs={"type": "time"},
        ),
        required=required,
    )


class TaskForm(forms.ModelForm):
    """
    _fields = [
        "name",
        "stage",
        "priority",
        "story_points",
        "tags_csv",
        "starts_at",
        "due_at",
        "assigned_to",
        # "description",
        "started_at",
        "ended_at",
        "parent_task",
    ]
    """

    starts_at = datetime_split_widget()
    due_at = datetime_split_widget()
    started_at = datetime_split_widget()
    ended_at = datetime_split_widget()

    class Meta:
        model = Task
        # fields = ["started_at", "ended_at"]
        fields = [
            "name",
            "stage",
            "priority",
            "story_points",
            "tags_csv",
            "assigned_to",
            "starts_at",
            "due_at",
            "started_at",
            "ended_at",
            "description",
            # "parent_task",
        ]

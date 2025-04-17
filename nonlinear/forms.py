from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"data-role": "tagsinput", "class": "form-control"}
        ),
    )

    class Meta:
        model = Task
        fields = ["name", "description", "due_date", "tags"]

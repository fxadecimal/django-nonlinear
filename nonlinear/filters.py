import django_filters
from .models import Task, TASK_STAGES
from django.db.models import Q


class TaskFilter(django_filters.FilterSet):
    # name = django_filters.CharFilter(lookup_expr="icontains")
    search = django_filters.CharFilter(
        method="search_name_and_description", label="Search"
    )
    stage = django_filters.MultipleChoiceFilter(
        choices=TASK_STAGES,
        label="Stage",
        field_name="stage",
    )

    def exclude_archived(self, queryset, name, value):
        return queryset.exclude(stage="archived")

    class Meta:
        model = Task
        fields = ["search", "stage", "priority", "assigned_to"]

    def search_name_and_description(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(tags_csv__icontains=value)
            | Q(_workspace_slug__icontains=value)
        )

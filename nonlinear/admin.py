from django import forms
from django.contrib import admin
from django.utils.html import mark_safe
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html

# Register your models here.
from nonlinear.models import Workspace, Task, TaskComment, Tag


# admin.site.register(TaskComment)
admin.site.register(Tag)


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):

    # inlines = [TaskInline]  # Add this line to include tasks
    list_display = (
        "name",
        "slug",
        "get_task_count",
        "updated_at",
        "created_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "display_tags",
        "task_counter",
        "get_tasks",
        "version",
    )
    autocomplete_fields = ["users"]  # Assuming there's a users field in Workspace
    search_fields = ["name", "slug"]  # Fields to search in Workspace

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make created_by read-only if it's already set
        if "created_by" not in self.readonly_fields:
            self.readonly_fields = self.readonly_fields + ("created_by",)

    def save_model(self, request, obj, form, change):
        if not change:  # Only for new objects
            obj.created_by = request.user
            obj.save()
        super().save_model(request, obj, form, change)

    def get_search_results(self, request, queryset, search_term):
        # This method handles search functionality in admin
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        return queryset, use_distinct

    @admin.display(description="Task Count")
    def get_task_count(self, obj):
        return obj.tasks.count()

    @admin.display(description="Tags")
    def display_tags(self, obj):
        tags = obj.tags.all()
        tag_display = (
            "No tags" if not tags else ", ".join([tag.with_hash for tag in tags])
        )

        # Create the add tag URL
        add_url = reverse("admin:nonlinear_tag_add") + f"?workspace={obj.id}"

        # Add a small plus symbol with a link
        plus_link = format_html(
            '<a href="{}" style="margin-left: 5px; text-decoration: none;" title="Add new tag">⊕</a>',
            add_url,
        )

        return format_html("{} {}", mark_safe(tag_display), plus_link)

    @admin.display(description="Tasks")
    def get_tasks(self, obj):
        tasks = obj.tasks.all()[:20]
        task_display = (
            "No tasks"
            if not tasks
            else "<br />".join([task.full_slug for task in tasks])
        )

        return format_html("{}", mark_safe(task_display))


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "name",
        "workspace",
        "created_at",
        "updated_at",
    )
    list_filter = ["workspace"]  # Add filter for workspace
    search_fields = ["name", "slug"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "slug",
        "version",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If the URL has a workspace parameter, filter by it
        workspace_id = request.GET.get("workspace__id__exact")
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)
        return qs

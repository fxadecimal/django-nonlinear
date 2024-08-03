from django.contrib import admin

# Register your models here.
from nonlinear.models import (
    Task,
    Workspace,
    TaskActivity,
    TaskComment,
)
from django.utils.html import format_html


class CreatedByMixin:
    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class WorkspaceAdmin(CreatedByMixin, admin.ModelAdmin):
    readonly_fields = ("created_by",)
    list_display = (
        "slug",
        "id",
        "name",
        "get_task_counter",
        "get_count_users",
        "created_by",
        "get_url_view",
    )
    autocomplete_fields = ("users",)

    def get_count_users(self, obj):
        return obj.users.count()

    get_count_users.short_description = "Users"

    def get_url_view(self, obj):
        return format_html(
            "<a href='{}' target='_blank'>View</a>", obj.get_absolute_url
        )

    get_url_view.allow_tags = True
    get_url_view.short_description = "View Workspace"

    def get_task_counter(self, obj):
        return obj.tasks.count()

    get_task_counter.short_description = "#Tasks"


class ProjectAdmin(CreatedByMixin, admin.ModelAdmin):
    readonly_fields = ("created_by",)
    list_display = ("name", "id", "created_by", "workspace")


class TaskAdmin(CreatedByMixin, admin.ModelAdmin):
    list_display = (
        "get_workspace_slug",
        "order",
        "name",
        "id",
        "created_by",
        "stage",
        "version",
    )
    search_fields = ("name", "description", "tags_csv")

    # queryset = Task.objects.get_queryset_all()
    def get_queryset(self, request):
        return Task.objects.get_queryset_all()

    def get_workspace_slug(self, obj):
        return obj.workspace_slug

    get_workspace_slug.short_description = "Workspace Slug"


admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskActivity)
admin.site.register(TaskComment)

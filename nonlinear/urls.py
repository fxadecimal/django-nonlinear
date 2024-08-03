from django.urls import path
from django.views.generic import TemplateView
from nonlinear.views import (
    WorkspaceList,
    TaskView,
    TaskCreate,
    TaskUpdate,
    TaskDelete,
    TasksFilterView,
    TaskCommentCreate,
    SubTaskCreate,
    users_tasks,
    users_tasks_active,
)

urlpatterns = [
    path("", WorkspaceList.as_view(), name="nonlinear"),
    # path("tasks/", TaskFilterView.as_view(), name="nonlinear-tasks"),
    path(
        "workspace/<int:workspace_pk>",
        TasksFilterView.as_view(),
        name="nonlinear-workspace-view",
    ),
    path(
        "workspace/<int:workspace_pk>/new",
        TaskCreate.as_view(),
        name="nonlinear-task-create",
    ),
    path("task/<int:pk>/edit", TaskUpdate.as_view(), name="nonlinear-task-edit"),
    path(
        "task/<int:pk>/comment-create",
        TaskCommentCreate.as_view(),
        name="nonlinear-comment-create",
    ),
    path(
        "task/<int:pk>/subtask-create",
        SubTaskCreate.as_view(),
        name="nonlinear-subtask-create",
    ),
    path(
        "task/<int:pk>/delete",
        TaskDelete.as_view(),
        name="nonlinear-task-delete",
    ),
    path(
        "workspace/<int:workspace_pk>/mine",
        users_tasks,
        name="nonlinear-tasks-user",
    ),
    path(
        "workspace/<int:workspace_pk>/mine-active",
        users_tasks_active,
        name="nonlinear-tasks-user-active",
    ),
]

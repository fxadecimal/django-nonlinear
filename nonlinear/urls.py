from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from nonlinear.views import (
    WorkspaceView,
    TaskUpdateView,
    TaskCreateView,
    WorkspaceListView,
    TaskDeleteView,
    create_comment,
    CommentDeleteView,
)

urlpatterns = [
    path("", WorkspaceListView.as_view(), name="nonlinear_workspace_list"),
    path(
        "task/<slug:pk>/",
        TaskUpdateView.as_view(),
        name="nonlinear_task_detail",
    ),
    path(
        "task/<slug:pk>/comment",
        create_comment,
        name="nonlinear_task_comment",
    ),
    path(
        "comment/<int:pk>/delete",
        CommentDeleteView.as_view(),
        name="nonlinear_task_comment_delete",
    ),
    path("<slug:slug>/", WorkspaceView.as_view(), name="nonlinear_workspace"),
    path("<slug:slug>/create", TaskCreateView.as_view(), name="nonlinear_task_create"),
    path("<slug:pk>/delete", TaskDeleteView.as_view(), name="nonlinear_task_delete"),
]

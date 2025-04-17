from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from nonlinear.views import (
    WorkspaceView,
    TaskView,
    TaskCreateView,
    WorkspaceListView,
    TaskDeleteView,
)

urlpatterns = [
    path("", WorkspaceListView.as_view(), name="nonlinear_workspace_list"),
    path("<slug:slug>/", WorkspaceView.as_view(), name="nonlinear_workspace"),
    path(
        "task/<slug:pk>/",
        TaskView.as_view(),
        name="nonlinear_task_detail",
    ),
    path("<slug:slug>/create", TaskCreateView.as_view(), name="nonlinear_task_create"),
    path("<slug:pk>/delete", TaskDeleteView.as_view(), name="nonlinear_task_delete"),
    path("<slug:slug>/tasks", TaskView.as_view(), name="nonlinear_task_list"),
]

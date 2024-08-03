from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import (
    CreateView,
    UpdateView,
    DetailView,
    ListView,
    DeleteView,
    TemplateView,
    View,
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from nonlinear.models import Task, Workspace, TaskComment
from django.db.models import Q, F

from django.db import DatabaseError, transaction
from django.urls import reverse_lazy
from django_filters.views import FilterView
from nonlinear.filters import TaskFilter
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from nonlinear.utils import detect_position_changes
from pprint import pprint
from .forms import TaskForm


class AuthRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class AuthUserinWorkspaceUsers(LoginRequiredMixin, UserPassesTestMixin):

    def get_workspace(self):
        workspace_pk = self.kwargs.get("workspace_pk", None)
        return Workspace.objects.get(pk=workspace_pk)

    def test_func(self):
        workspace = self.get_workspace()
        user = self.request.user

        if not workspace:
            return False

        if user == workspace.created_by:
            return True

        if user in workspace.users.all():
            return True


class WorkspaceList(LoginRequiredMixin, ListView):
    model = Workspace
    template_name = "nonlinear/cbv/list.html"

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(Q(created_by=user) | Q(users=user))
        return qs


# http://localhost:8000/nonlinear/new/workspace/1
class TasksFilterView(AuthUserinWorkspaceUsers, FilterView):
    model = Task
    filterset_class = TaskFilter
    template_name = "nonlinear/workspace/workspace.html"

    def get_queryset(self):
        workspace_pk = self.kwargs.get("workspace_pk", None)

        qs = super().get_queryset()
        if workspace_pk:
            qs = qs.filter(workspace=workspace_pk)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace_pk = self.kwargs.get("workspace_pk")
        context["workspace"] = Workspace.objects.get(pk=workspace_pk)
        return context

    def post(self, request, *args, **kwargs):
        tasks_id = request.POST.getlist("task_id", None)

        for i, task_pk in enumerate(tasks_id):
            task = Task.objects.get(pk=task_pk)
            task.order = i
            task.save()

        response = super().get(request, *args, **kwargs)
        return response


# CreateViews
class TaskCreate(AuthRequiredMixin, CreateView):
    model = Task
    fields = ["name"]
    template_name = "nonlinear/cbv/form.html"

    def form_valid(self, form):
        workspace_pk = self.kwargs.get("workspace_pk")
        workspace = Workspace.objects.get(pk=workspace_pk)
        form.instance.workspace = workspace
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("nonlinear-task-edit", kwargs={"pk": self.object.pk})


class TaskUpdate(AuthRequiredMixin, UpdateView):
    template_name = "nonlinear/workspace/task_edit.html"
    model = Task
    form_class = TaskForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["assigned_to"].queryset = self.object.workspace.users.all()
        return form

    def get_parent_task(self):
        return Task.objects.filter(workspace=self.object.workspace)

    def get_success_url(self) -> str:
        # return user back to the original
        return self.request.get_full_path()


class TaskDelete(AuthRequiredMixin, DeleteView):
    model = Task
    template_name = "nonlinear/cbv/confirm.html"

    def get_success_url(self):
        return reverse_lazy(
            "nonlinear-workspace-view",
            kwargs={"workspace_pk": self.object.workspace.id},
        )


class TaskView(AuthRequiredMixin, UpdateView):
    template_name = "nonlinear/workspace/task_view.html"
    slug_field = "workspace_index"
    model = Task
    fields = "__all__"


class TaskCommentCreate(AuthRequiredMixin, CreateView):
    model = TaskComment
    fields = ["description"]
    template_name = "nonlinear/cbv/form.html"

    def form_valid(self, form):
        task_pk = self.kwargs.get("pk")
        task = Task.objects.get(pk=task_pk)
        form.instance.task = task
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        task_pk = self.kwargs.get("pk")
        return reverse_lazy("nonlinear-task-edit", kwargs={"pk": task_pk})


class TaskCommentDelete(AuthRequiredMixin, DeleteView):
    model = TaskComment

    def get_success_url(self):
        task_pk = self.kwargs.get("pk")
        return reverse_lazy("nonlinear-task-edit", kwargs={"pk": task_pk})


@login_required
def users_tasks(request, workspace_pk: int):
    user = request.user
    url = reverse_lazy(
        "nonlinear-workspace-view", kwargs={"workspace_pk": workspace_pk}
    )
    return redirect(f"{url}?assigned_to={user.id}")


@login_required
def users_tasks_active(request, workspace_pk: int):
    user = request.user
    url = reverse_lazy(
        "nonlinear-workspace-view", kwargs={"workspace_pk": workspace_pk}
    )
    return redirect(f"{url}?assigned_to={user.id}&stage=todo&stage=in_progress&")


class SubTaskCreate(AuthRequiredMixin, CreateView):
    model = Task
    fields = ["name"]

    def form_valid(self, form):
        task_pk = self.kwargs.get("pk")
        task = Task.objects.get(pk=task_pk)
        form.instance.parent_task = task
        form.instance.workspace = task.workspace
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        task_pk = self.kwargs.get("pk")
        return reverse_lazy("nonlinear-task-edit", kwargs={"pk": task_pk})

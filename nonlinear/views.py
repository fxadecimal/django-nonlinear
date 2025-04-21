from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.views.generic import (
    DetailView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from nonlinear.models import Task, Workspace, TaskComment, Tag
from django_filters import FilterSet, CharFilter, ModelChoiceFilter
from django_filters.views import FilterView
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Case, When
from django.contrib.auth import get_user_model
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required


class UserInWorkspaceMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        # Get the workspace slug from the URL
        slug = kwargs.get("slug")
        # Get the workspace object
        workspace = get_object_or_404(Workspace, slug=slug)
        # Check if the user is in the workspace
        if request.user not in workspace.users.all():
            raise PermissionDenied(
                "You do not have permission to access this workspace."
            )
        return super().dispatch(request, *args, **kwargs)


# Create a filter for Task model
class TaskFilter(FilterSet):
    search = CharFilter(method="filter_search", label="Search")

    # have to initialize with a
    assigned_to = ModelChoiceFilter(
        queryset=get_user_model().objects.none(), label="Assigned To"
    )

    def __init__(self, *args, **kwargs):
        # Extract workspace from kwargs before passing to parent
        self.workspace = kwargs.pop("workspace", None)
        super().__init__(*args, **kwargs)

        # Update assigned_to queryset with workspace users
        if self.workspace:
            self.filters["assigned_to"].queryset = self.workspace.users.all()

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(description__icontains=value)
            | Q(tags__name__icontains=value.lstrip("#"))  # Remove leading # if present
        ).distinct()

    class Meta:
        model = Task
        fields = [
            "search",
            "status",
            "priority",
            "assigned_to",
        ]

        # Changed from dictionary format to list to control field order with 'search' first


class WorkspaceListView(LoginRequiredMixin, ListView):
    model = Workspace
    template_name = "nonlinear/list.html"

    def get_queryset(self):
        queryset = Workspace.objects.filter(users=self.request.user)
        if not queryset.exists():
            raise Http404("No workspaces found")
        return queryset


# Create your views here.
class WorkspaceView(UserInWorkspaceMixin, FilterView):
    model = Task
    template_name = "nonlinear/workspace.html"
    context_object_name = "tasks"
    filterset_class = TaskFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace = Workspace.objects.get(slug=self.kwargs.get("slug"))
        filtered_queryset = self.filterset.qs

        if self.filterset.data:  # if filters are applied
            context["sortable"] = False
        else:
            context["sortable"] = True

        users_tasks = Task.objects.filter(
            workspace=workspace, assigned_to=self.request.user
        )

        # tasks_by_status = {}

        # counter = 0
        # for status, _ in Task.STATUS_CHOICES:
        #     tasks_by_status[status] = filtered_queryset.filter(status=status)
        #     for task in tasks_by_status[status]:
        #         task.qs_position = counter
        #         counter += 1

        # context["tasks_by_status"] = tasks_by_status

        context["statuses"] = Task.STATUS_CHOICES
        context["workspace"] = workspace
        context["users_tasks"] = users_tasks.count()
        context["users_tasks_pending"] = users_tasks.filter(status="todo").count()
        return context

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        workspace = Workspace.objects.get(slug=slug)

        return Task.objects.active().filter(workspace=workspace)

    def post(self, request, *args, **kwargs):
        tasks_id = request.POST.getlist("task_id", None)
        # filtered_queryset = self.filterset.qs.filter(pk__in=tasks_id)

        # Update the status of the tasks based on the order in the request
        for index, task_id in enumerate(tasks_id):
            Task.objects.filter(pk=task_id).update(
                workspace_order=index,
            )

        return self.get(request, *args, **kwargs)

    def get_filterset_kwargs(self, *args, **kwargs):
        kwargs = super().get_filterset_kwargs(*args, **kwargs)
        workspace = get_object_or_404(Workspace, slug=self.kwargs.get("slug"))
        kwargs["workspace"] = workspace
        return kwargs


class TaskCreateView(UserInWorkspaceMixin, CreateView):
    model = Task
    # form_class = TaskForm
    template_name = "nonlinear/task_form.html"
    fields = ["name", "status"]

    def get_success_url(self):
        # return reverse("nonlinear_workspace", kwargs={"slug": self.kwargs["slug"]})
        return reverse_lazy("nonlinear_task_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.workspace = get_object_or_404(Workspace, slug=self.kwargs["slug"])
        form.instance.created_by = self.request.user
        form.instance.description = ""
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workspace"] = get_object_or_404(Workspace, slug=self.kwargs["slug"])
        return context

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["nonlinear/task_form_partial.html"]
        return [self.template_name]


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = "nonlinear/task_form.html"
    context_object_name = "task"
    fields = [
        "name",
        "description",
        "status",
        "priority",
        "tags",
        "assigned_to",
        "start_date",
        "end_date",
    ]

    def dispatch(self, request, *args, **kwargs):
        # Get task and its workspace
        task = self.get_object()
        workspace = task.workspace

        if request.user not in workspace.users.all():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Get the workspace for the current task
        workspace = self.object.workspace
        # Filter the assigned_to field to only show users in this workspace
        form.fields["assigned_to"].queryset = workspace.users.all()
        form.fields["tags"].queryset = Tag.objects.filter(workspace=workspace).order_by(
            "name"
        )

        # Set date input widgets for date fields
        form.fields["start_date"].widget = forms.DateInput(attrs={"type": "date"})
        form.fields["end_date"].widget = forms.DateInput(attrs={"type": "date"})
        return form

    def get_success_url(self):
        return reverse_lazy(
            "nonlinear_workspace", kwargs={"slug": self.object.workspace.slug}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        context["comments"] = TaskComment.objects.filter(task=task)
        context["workspace"] = task.workspace
        return context


class TaskDeleteView(LoginRequiredMixin, UpdateView):
    model = Task
    context_object_name = "task"
    template_name = "nonlinear/confirm_delete.html"
    fields = []

    def dispatch(self, request, *args, **kwargs):
        # check user is in the workspace
        task = self.get_object()
        workspace = task.workspace

        if request.user not in workspace.users.all():
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "nonlinear_workspace", kwargs={"slug": self.object.workspace.slug}
        )

    def form_valid(self, form):
        self.object.is_deleted = True
        self.object.save()
        messages.success(self.request, f'Task "{self.object.name}" has been deleted.')
        return super().form_valid(form)


@login_required
def create_comment(request, pk):

    if request.method == "POST":
        task = get_object_or_404(Task, pk=pk)

        if request.user not in task.workspace.users.all():
            raise PermissionDenied

        comment_text = request.POST.get("comment")
        TaskComment.objects.create(
            task=task, text=comment_text, created_by=request.user
        )
        return redirect("nonlinear_task_detail", pk=task.pk)
    else:
        raise Http404("Invalid request method.")


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = TaskComment
    template_name = "nonlinear/confirm_delete.html"
    context_object_name = "comment"

    def dispatch(self, request, *args, **kwargs):
        # check user is in the workspace
        comment = self.get_object()
        task = comment.task
        workspace = task.workspace

        if request.user not in workspace.users.all():
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("nonlinear_task_detail", kwargs={"pk": self.object.task.pk})

    def form_valid(self, form):
        self.object.is_deleted = True
        self.object.save()
        messages.success(self.request, f'Task "{self.object}" has been deleted.')
        return super().form_valid(form)

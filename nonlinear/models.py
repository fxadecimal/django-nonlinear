# -*- coding: utf-8 -*-
import re
import uuid
from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q, F
from django.db.models.functions import Concat


User = get_user_model()

TASK_TYPES = (
    ("ticket", "Ticket"),
    ("task", "Task"),
)

TASK_STAGES = (
    ("in_progress", "In Progress"),
    ("todo", "To Do"),
    ("backlog", "Backlog"),
    ("done", "Done"),
)

PROJECT_STATUSES = (
    ("pending", "Pending"),
    ("active", "Active"),
    ("completed", "Completed"),
    ("archived", "Archived"),
)

URGENCY_LEVELS = (
    (1, "Severe"),
    (2, "High"),
    (3, "Medium"),
    (4, "Low"),
)

TSHIRT_SIZES = (
    (1, "XS"),
    (2, "S"),
    (4, "M"),
    (8, "L"),
    (16, "XL"),
    (32, "XXL"),
)


class LockAbstract(models.Model):
    class Meta:
        abstract = True

    locked_at = models.DateTimeField(blank=True, null=True)
    locked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="locked_%(class)s",
        blank=True,
        null=True,
    )


class BaseModel(models.Model):
    APP_NAME = "nonlinear"

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        # related_name="%(class)s_created",
        related_name="+",
        blank=True,
        null=True,
    )
    is_deleted = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)

    name = models.CharField(max_length=256, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tags_csv = models.CharField(
        max_length=256, blank=True, null=True
    )  # todo: replace this with django-taggit

    def save(self, *args, **kwargs):
        self.version += 1
        return super().save(*args, **kwargs)

    @property
    def tags(self) -> list:
        return re.split(r",\s*", self.tags_csv) if self.tags_csv else []

    def delete(self, soft_delete=True, *args, **kwargs):
        if soft_delete == False:
            super().delete(*args, **kwargs)
        else:
            self.is_deleted = True
            self.save()

    def get_url_action(
        self,
        action="view",
        workspace_pk=None,
    ):
        actions = ["view", "edit", "delete"]
        if action not in actions:
            raise ValueError(f"Invalid action: {action}")

        if workspace_pk is None:
            workspace = getattr(self, "workspace", None)
            if workspace is None:
                raise ValueError(
                    f"workspace_pk is required for {self.__class__.__name__}"
                )
            workspace_pk = workspace.pk

        _class = self.__class__.__name__.lower()
        return reverse(
            f"{self.APP_NAME}-{_class}-{action}", kwargs={"workspace_pk": workspace_pk}
        )

    @property
    def get_slug(self):
        return self.pk

    @property
    def get_url_delete(self):
        return self.get_url_action("delete", workspace_pk=self.workspace.pk)


class BaseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def get_queryset_all(self):
        return super().get_queryset()


class TaskManger(BaseManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(is_archived=False)
            .annotate(
                _workspace_slug=models.ExpressionWrapper(
                    Concat(
                        models.F("workspace__slug"),
                        models.Value("-"),
                        models.F("workspace_index"),
                    ),
                    output_field=models.CharField(),
                )
            )
        )


# Create your models here.
class Workspace(BaseModel):
    objects = BaseManager()

    slug = models.SlugField(max_length=16, unique=True)
    users = models.ManyToManyField(User, related_name="+", blank=True)
    # cycle_duration = models.DurationField(blank=True, null=True, default=86400*14)
    # cycle_starts_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Workspace({self.slug}): {self.name}"

    @property
    def get_absolute_url(self):
        return self.get_url_action("view", workspace_pk=self.pk)


class Task(BaseModel):
    objects = TaskManger()
    # form_class = TaskForm

    class Meta:
        unique_together = [("workspace", "workspace_index")]
        ordering = ["order", "created_at"]

    is_archived = models.BooleanField(default=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.PROTECT, related_name="tasks"
    )
    workspace_index = models.PositiveIntegerField(editable=True, blank=True, null=True)
    slug = models.SlugField(max_length=256, null=True, blank=True)

    assigned_to = models.ManyToManyField(User, related_name="+", blank=True)

    priority = models.IntegerField(choices=URGENCY_LEVELS, blank=True, null=True)
    stage = models.CharField(max_length=32, choices=TASK_STAGES, default="backlog")
    story_points = models.PositiveIntegerField(
        blank=True, null=True, choices=TSHIRT_SIZES
    )

    starts_at = models.DateTimeField(blank=True, null=True)
    due_at = models.DateTimeField(blank=True, null=True)

    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    order = models.PositiveIntegerField(blank=True, null=True)

    parent_task = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="sub_tasks",
    )

    def save(self, *args, **kwargs):

        if not self.workspace_index:
            next_task_index = (
                Task.objects.get_queryset_all().filter(workspace=self.workspace).count()
                + 1
            )
            self.workspace_index = next_task_index
            self.order = next_task_index

        if self.name:
            self.slug = slugify(self.name)

        if not self.started_at and self.stage == "in_progress":
            self.started_at = timezone.now()

        if not self.ended_at and (self.stage in ["done", "archived"]):
            self.ended_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def workspace_slug(self):
        return f"{self.workspace.slug}-{self.workspace_index}"

    @property
    def git_slug(self):
        return f"{self.workspace_slug}_{self.slug}"[0:254]


# class UserTaskOrder(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     task = models.ForeignKey(Task, on_delete=models.CASCADE)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         unique_together = ("user", "task")


class TaskCommentManager(BaseManager):
    pass


class TaskComment(BaseModel):
    objects = TaskCommentManager()

    class Meta:
        ordering = ["-created_at"]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")

    @property
    def text(self):
        return self.description


class TaskActivityManager(BaseManager):
    pass


class TaskActivity(models.Model):
    """
    Inspiration: https://github.com/django-notifications/django-notifications?tab=readme-ov-file

    - Actor. The object that performed the activity.
    - Verb. The verb phrase that identifies the action of the activity.
    - Action Object. (Optional) The object linked to the action itself.
    - Target. (Optional) The object to which the activity was performed.

    """

    objects = TaskActivityManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Task Activities"

    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="activities")
    verb = models.CharField(max_length=64)
    action = models.CharField(max_length=256)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        # related_name="%(class)s_created",
        related_name="+",
        blank=True,
        null=True,
    )
    is_deleted = models.BooleanField(default=False)

    @property
    def phrase(self):
        #  justquick (actor) closed (verb) issue 2 (action_object) on activity-stream (target) 12 hours ago
        return f"{self.created_by} {self.verb} {self.task.name} on {self.created_at}"

    @property
    def phrase_html(self):
        return f'<p id="task-activity-{self.id}"> <a href="#">{self.created_by}</a> {self.verb} on <a href="#">{self.task.name}</a></p>'

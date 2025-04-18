import uuid
from django.db import models

from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


from django.db.models import (
    F,
    Value,
    Q,
    Count,
    Sum,
    CharField,
    IntegerField,
    FloatField,
    Window,
)
from django.db.models.functions import Concat, Cast, LPad, RowNumber
from django.utils.text import slugify
from colorfield.fields import ColorField


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Versioned(models.Model):
    version = models.IntegerField(default=1)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.version = 1
        else:
            self.version += 1
        return super().save(*args, **kwargs)


# Create your models here.
class Workspace(TimestampedModel, Versioned):
    class Meta:
        ordering = ["-updated_at"]

    name = models.CharField(max_length=100)
    slug = models.SlugField(
        unique=True, max_length=10, help_text="Unique identifier for the workspace"
    )
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(
        User, related_name="nonlinear_workspaces", blank=True
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="+", null=True, blank=True
    )
    is_deleted = models.BooleanField(default=False)
    task_counter = models.IntegerField(
        default=0,
    )

    def get_absolute_url(self):
        return reverse("nonlinear_workspace", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name


class TaskManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                _slug=Concat(
                    F("workspace__slug"),
                    Value("-"),
                    LPad(
                        Cast(models.F("workspace_index"), models.CharField()),
                        3,
                        Value("0"),
                    ),
                    output_field=models.CharField(),
                )
            )
        )

    def active(self):
        return self.get_queryset().filter(is_deleted=False)

    def deleted(self):
        return self.get_queryset().filter(is_deleted=True)


class Task(TimestampedModel, Versioned):
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("todo", "To Do"),
        ("backlog", "Backlog"),
        ("done", "Done"),
        ("archived", "Archived"),
        ("cancelled", "Cancelled"),
    ]

    objects = TaskManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        ordering = ["workspace", "status", "workspace_order", "updated_at"]
        unique_together = (
            "workspace",
            "workspace_index",
        )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    is_deleted = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="tasks"
    )
    workspace_order = models.IntegerField(null=True)
    workspace_index = models.IntegerField(null=True, editable=False)

    subtasks = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="+"
    )

    assigned_to = models.ManyToManyField(
        User,
        blank=True,
        through="UserTask",
    )

    priority = models.IntegerField(
        choices=[
            (0, "Severe"),
            (1, "High"),
            (2, "Medium"),
            (3, "Low"),
        ],
        default=2,
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default="backlog",
    )
    tags = models.ManyToManyField("Tag", blank=True, related_name="tasks")

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    started_date = models.DateTimeField(null=True, blank=True)
    ended_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.slug} - {self.name}"

    @property
    def slug(self):
        # return self._slug
        return f"{self.workspace.slug}-{self.workspace_index:03d}"

    @property
    def full_slug(self):
        return slugify(f"{self.slug}_{self.name}")

    def save(self, *args, **kwargs):
        if not self.workspace_index:
            self.workspace_index = self.workspace.tasks.count() + 1
        if not self.workspace_order:
            self.workspace_order = self.workspace_index

        # updated_at
        self.workspace.save()

        super().save(*args, **kwargs)

    @property
    def get_absolute_url(self):
        return reverse("nonlinear_task_detail", kwargs={"pk": self.pk})


class UserTask(TimestampedModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="nonlinear_user_task"
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="nonlinear_user_task"
    )
    order = models.PositiveIntegerField(default=0)


class TaskComment(TimestampedModel):
    is_deleted = models.BooleanField(default=False)
    text = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="task_comments"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")


class Tag(TimestampedModel):
    name = models.CharField(max_length=64)
    color = ColorField(
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="tags", null=True
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="tags"
    )

    class Meta:
        unique_together = ("name", "workspace")
        ordering = ["workspace", "name"]

    def __str__(self):
        return self.with_hash

    @property
    def with_hash(self):
        return f"#{self.name}"

    @property
    def text_color(self):
        """
        inverts the color for better contrast
        """
        if self.color:
            r, g, b = self.color[1:3], self.color[3:5], self.color[5:7]
            r, g, b = int(r, 16), int(g, 16), int(b, 16)
            # Calculate the luminance
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            # Return black or white based on luminance
            return "#000000" if luminance > 0.5 else "#FFFFFF"
        return "#000000"


# class AcitivityLog(models.Model):

#     created_at = models.DateTimeField(auto_now_add=True)
#     action = models.CharField(max_length=255)
#     details = models.TextField(null=True, blank=True)

#     workspace = models.ForeignKey(
#         Workspace,
#         on_delete=models.CASCADE,
#         related_name="activity_logs",
#         null=True,
#         blank=True,
#     )

#     created_by = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="activity_logs",
#         null=True,
#         blank=True,
#     )

#     task = models.ForeignKey(
#         Task,
#         on_delete=models.CASCADE,
#         related_name="activity_logs",
#         null=True,
#         blank=True,
#     )

#     def __str__(self):
#         return f"{self.user} - {self.action} - {self.task}"

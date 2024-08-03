import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("version", models.PositiveIntegerField(default=1)),
                ("name", models.CharField(blank=True, max_length=256, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("tags_csv", models.CharField(blank=True, max_length=256, null=True)),
                ("is_archived", models.BooleanField(default=False)),
                ("workspace_index", models.PositiveIntegerField(blank=True, null=True)),
                ("slug", models.SlugField(blank=True, max_length=256, null=True)),
                (
                    "priority",
                    models.IntegerField(
                        blank=True,
                        choices=[(1, "Severe"), (2, "High"), (3, "Medium"), (4, "Low")],
                        null=True,
                    ),
                ),
                (
                    "stage",
                    models.CharField(
                        choices=[
                            ("in_progress", "In Progress"),
                            ("todo", "To Do"),
                            ("backlog", "Backlog"),
                            ("done", "Done"),
                        ],
                        default="backlog",
                        max_length=32,
                    ),
                ),
                (
                    "story_points",
                    models.PositiveIntegerField(
                        blank=True,
                        choices=[
                            (1, "XS"),
                            (2, "S"),
                            (4, "M"),
                            (8, "L"),
                            (16, "XL"),
                            (32, "XXL"),
                        ],
                        null=True,
                    ),
                ),
                ("starts_at", models.DateTimeField(blank=True, null=True)),
                ("due_at", models.DateTimeField(blank=True, null=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("order", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "assigned_to",
                    models.ManyToManyField(
                        blank=True, related_name="+", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "parent_task",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sub_tasks",
                        to="nonlinear.task",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="TaskActivity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("verb", models.CharField(max_length=64)),
                ("action", models.CharField(max_length=256)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to="nonlinear.task",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Task Activities",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="TaskComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("version", models.PositiveIntegerField(default=1)),
                ("name", models.CharField(blank=True, max_length=256, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("tags_csv", models.CharField(blank=True, max_length=256, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="nonlinear.task",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Workspace",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("version", models.PositiveIntegerField(default=1)),
                ("name", models.CharField(blank=True, max_length=256, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("tags_csv", models.CharField(blank=True, max_length=256, null=True)),
                ("slug", models.SlugField(max_length=16, unique=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "users",
                    models.ManyToManyField(
                        blank=True, related_name="+", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="task",
            name="workspace",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tasks",
                to="nonlinear.workspace",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="task",
            unique_together={("workspace", "workspace_index")},
        ),
    ]

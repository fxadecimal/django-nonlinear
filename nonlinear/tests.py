from django.test import TestCase

from django.contrib.auth import get_user_model
from nonlinear.serializers import serialize_workspace, serialize_deserialize

User = get_user_model()

from .models import (
    Workspace,
    Task,
)


# Create your tests here.
class TestNonLinear(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="test", password="test", is_staff=True, is_superuser=True
        )
        self.workspace = Workspace.objects.create(name="Test Workspace", slug="test")
        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            workspace=self.workspace,
        )

    def test_create_workspace(self):
        workspace2 = Workspace.objects.create(name="Test Workspace2", slug="test2")
        self.assertEqual(workspace2.name, "Test Workspace2")
        self.assertEqual(workspace2.slug, "test2")

    def test_create_task(self):
        self.assertEqual(self.task.slug, "test-task")
        self.assertEqual(self.task.git_slug, "test-1_test-task")
        task2 = Task.objects.create(
            name="Test Task 2",
            description="Test Description 2",
            workspace=self.workspace,
        )
        task2_id = task2.id
        self.assertEqual(task2.workspace_index, 2)
        task2.delete(soft_delete=True)
        task2.refresh_from_db()
        self.assertTrue(Task.objects.get_queryset_all().filter(id=task2_id).exists())
        task2.delete(soft_delete=False)
        self.assertFalse(Task.objects.get_queryset_all().filter(id=task2_id).exists())

    def test_change_task_state(self):
        self.assertIsNone(self.task.started_at)
        self.assertIsNone(self.task.ended_at)

        self.task.stage = "in_progress"
        self.task.save()
        self.task.refresh_from_db()
        self.assertIsNotNone(self.task.started_at)

        self.task.stage = "done"
        self.task.save()
        self.task.refresh_from_db()
        self.assertIsNotNone(self.task.ended_at)

    def test_serializer(self):
        l = serialize_deserialize([self.workspace])
        self.assertEqual(l[0]["fields"]["name"], "Test Workspace")

        l = serialize_workspace(self.workspace)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0]["fields"]["name"], "Test Workspace")
        self.assertEqual(l[1]["fields"]["name"], "Test Task")

    def test_task_comment(self):
        self.task.comments.create(description="Test Comment")
        self.assertEqual(self.task.comments.first().description, "Test Comment")
        self.assertEqual(self.task.comments.first().text, "Test Comment")
        self.assertEqual(self.task.comments.first().task, self.task)

    def test_filters(self):
        from nonlinear.filters import TaskFilter

        qs = Task.objects.get_queryset()
        f = TaskFilter(
            {"search": "Test Task"},
            qs,
        )
        self.assertEqual(f.qs.count(), 1)
        self.assertEqual(f.qs.first().name, "Test Task")

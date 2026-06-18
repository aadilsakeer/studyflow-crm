from django.test import TestCase

from accounts.models import Company, CustomUser, Role

from core.models import Task
from core.task_service import (
    create_task,
    filter_tasks_for_user,
    get_task_summary,
    update_task,
)


class TaskServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Task Co')
        self.admin_role = Role.objects.create(name='Admin')
        self.tele_role = Role.objects.create(name='Telecaller')
        self.admin = CustomUser.objects.create_user(
            username='admin1',
            password='pass1234',
            company=self.company,
            role=self.admin_role,
        )
        self.telecaller = CustomUser.objects.create_user(
            username='tele1',
            password='pass1234',
            company=self.company,
            role=self.tele_role,
        )

    def test_create_and_complete_task(self):
        task = create_task(
            self.company,
            self.admin,
            title='Call lead',
            task_type='follow_up_call',
            assigned_to=self.telecaller,
            priority='high',
        )

        self.assertEqual(task.status, 'pending')

        update_task(
            task,
            self.telecaller,
            {'status': 'completed'},
        )
        task.refresh_from_db()

        self.assertEqual(task.status, 'completed')
        self.assertIsNotNone(task.completed_at)

    def test_telecaller_sees_assigned_tasks_only(self):
        create_task(
            self.company,
            self.admin,
            title='Mine',
            assigned_to=self.telecaller,
        )
        create_task(
            self.company,
            self.admin,
            title='Other',
            assigned_to=self.admin,
        )

        qs = filter_tasks_for_user(
            Task.objects.filter(company=self.company),
            self.telecaller,
        )

        self.assertEqual(qs.count(), 1)

    def test_task_summary(self):
        create_task(
            self.company,
            self.admin,
            title='Pending task',
            assigned_to=self.telecaller,
        )

        summary = get_task_summary(
            self.company,
            self.admin,
        )

        self.assertEqual(summary['pending_tasks'], 1)

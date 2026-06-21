from django.conf import settings
from django.db import models

from admissions.models import Student

from auditlogs.models import AuditLog


class ActivityLog(models.Model):

    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    module = models.CharField(
        max_length=100,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.title


class StudentTimeline(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='timeline_events',
    )

    event_type = models.CharField(
        max_length=50,
        db_index=True,
    )

    action = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    audit_log = models.ForeignKey(
        AuditLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['student', '-created_at'],
                name='student_timeline_created_idx',
            ),
            models.Index(
                fields=['student', 'event_type', '-created_at'],
                name='student_timeline_event_idx',
            ),
        ]

    def __str__(self):
        return self.action

from django.db import models
from django.conf import settings

from core.models import Company


class AuditLog(models.Model):

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    module = models.CharField(
        max_length=100
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )

    object_id = models.PositiveIntegerField()

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.module} - {self.action}"
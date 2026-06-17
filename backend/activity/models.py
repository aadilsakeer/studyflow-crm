from django.db import models
from django.conf import settings

from core.models import Company


class ActivityLog(models.Model):

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

    title = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    object_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
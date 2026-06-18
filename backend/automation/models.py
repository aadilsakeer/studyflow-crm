from django.conf import settings
from django.db import models

from core.models import Company


class WorkflowAlertLog(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )

    alert_key = models.CharField(
        max_length=160,
        db_index=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['alert_key', 'user'],
                name='uniq_workflow_alert_per_user',
            ),
        ]
        indexes = [
            models.Index(
                fields=['company', '-created_at'],
                name='workflow_alert_co_created_idx',
            ),
        ]

    def __str__(self):
        return self.alert_key

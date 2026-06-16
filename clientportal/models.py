from django.db import models

from admissions.models import Student


class ClientPortalAccess(models.Model):

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE
    )

    username = models.CharField(
        max_length=150,
        unique=True
    )

    password = models.CharField(
        max_length=255
    )

    is_active = models.BooleanField(
        default=True
    )

    last_login = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.username
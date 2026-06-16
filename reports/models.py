from django.db import models

from core.models import Company


class Report(models.Model):

    REPORT_TYPES = [
        ('admissions', 'Admissions'),
        ('finance', 'Finance'),
        ('recruitment', 'Recruitment'),
        ('hrm', 'HRM'),
        ('workvisa', 'Work Visa'),
        ('custom', 'Custom'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generated', 'Generated'),
        ('failed', 'Failed'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPES
    )

    generated_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True
    )

    file = models.FileField(
        upload_to='reports/',
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class ReportSchedule(models.Model):

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    report_type = models.CharField(
        max_length=50
    )

    frequency = models.CharField(
        max_length=50,
        choices=FREQUENCY_CHOICES
    )

    email_to = models.EmailField()

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.report_type} - {self.frequency}"
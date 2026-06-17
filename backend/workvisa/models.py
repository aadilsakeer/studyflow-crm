from django.db import models

from core.models import Company
from accounts.models import CustomUser
from recruitment.models import Candidate


class WorkVisaCase(models.Model):

    STATUS_CHOICES = [
        ('new', 'New'),
        ('documents_pending', 'Documents Pending'),
        ('documents_completed', 'Documents Completed'),
        ('submitted', 'Submitted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('deployed', 'Deployed'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE
    )

    assigned_staff = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    destination_country = models.CharField(
        max_length=100
    )

    visa_type = models.CharField(
        max_length=100
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='new'
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.candidate} - {self.destination_country}"


class WorkVisaDocument(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    visa_case = models.ForeignKey(
        WorkVisaCase,
        on_delete=models.CASCADE
    )

    document_name = models.CharField(
        max_length=255
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending'
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.document_name


class WorkVisaTimeline(models.Model):

    visa_case = models.ForeignKey(
        WorkVisaCase,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
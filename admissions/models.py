from django.db import models

from leads.models import Lead
from accounts.models import CustomUser
from core.models import Company, Branch


class Student(models.Model):

    STATUS_CHOICES = [
        ('counselling', 'Counselling'),
        ('application', 'Application'),
        ('offer_received', 'Offer Received'),
        ('visa_processing', 'Visa Processing'),
        ('visa_approved', 'Visa Approved'),
        ('enrolled', 'Enrolled'),
        ('closed', 'Closed'),
    ]

    lead = models.OneToOneField(
        Lead,
        on_delete=models.CASCADE
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    assigned_counselor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    student_id = models.CharField(
        max_length=50,
        unique=True
    )

    passport_number = models.CharField(
        max_length=50,
        blank=True
    )

    destination_country = models.CharField(
        max_length=100,
        blank=True
    )

    preferred_university = models.CharField(
        max_length=255,
        blank=True
    )

    intake = models.CharField(
        max_length=100,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='counselling'
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.student_id
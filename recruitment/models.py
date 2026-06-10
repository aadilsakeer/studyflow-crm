from django.db import models

from core.models import Company
from accounts.models import CustomUser


class Employer(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=255
    )

    contact_person = models.CharField(
        max_length=255,
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    country = models.CharField(
        max_length=100,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


class JobOpening(models.Model):

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('on_hold', 'On Hold'),
    ]

    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    country = models.CharField(
        max_length=100
    )

    vacancies = models.PositiveIntegerField(
        default=1
    )

    salary = models.CharField(
        max_length=100,
        blank=True
    )

    requirements = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='open'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class Candidate(models.Model):

    STATUS_CHOICES = [
        ('new', 'New'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('deployed', 'Deployed'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    assigned_staff = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    full_name = models.CharField(
        max_length=255
    )

    phone = models.CharField(
        max_length=30
    )

    email = models.EmailField(
        blank=True
    )

    passport_number = models.CharField(
        max_length=100,
        blank=True
    )

    preferred_country = models.CharField(
        max_length=100,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='new'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.full_name


class Interview(models.Model):

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE
    )

    interview_date = models.DateField()

    interviewer = models.CharField(
        max_length=255,
        blank=True
    )

    remarks = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='scheduled'
    )

    def __str__(self):
        return f"{self.candidate} Interview"


class CandidateDocument(models.Model):

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE
    )

    document_name = models.CharField(
        max_length=255
    )

    remarks = models.TextField(
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.document_name


class Deployment(models.Model):

    candidate = models.OneToOneField(
        Candidate,
        on_delete=models.CASCADE
    )

    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE
    )

    joining_date = models.DateField()

    country = models.CharField(
        max_length=100
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.candidate} Deployment"
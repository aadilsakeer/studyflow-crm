from django.db import models
from django.conf import settings


class Company(models.Model):

    name = models.CharField(
        max_length=255
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    logo = models.ImageField(
        upload_to='company_logos/',
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Branch(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=255
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Task(models.Model):

    TASK_TYPE_CHOICES = [
        ('follow_up_call', 'Follow-up Call'),
        ('document_collection', 'Document Collection'),
        ('application_submission', 'Application Submission'),
        ('offer_review', 'Offer Review'),
        ('visa_appointment', 'Visa Appointment'),
        ('general_task', 'General Task'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )

    task_type = models.CharField(
        max_length=40,
        choices=TASK_TYPE_CHOICES,
        default='general_task',
        db_index=True,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    lead = models.ForeignKey(
        'leads.Lead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
    )

    student = models.ForeignKey(
        'admissions.Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
    )

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        db_index=True,
    )

    due_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    reminder_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['company', 'status', '-due_date'],
                name='task_co_status_due_idx',
            ),
            models.Index(
                fields=['company', 'assigned_to', 'status'],
                name='task_co_assign_status_idx',
            ),
            models.Index(
                fields=['company', 'reminder_at'],
                name='task_co_reminder_idx',
            ),
        ]

    def __str__(self):
        return self.title


class TaskComment(models.Model):

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user} - {self.task}"
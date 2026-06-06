from django.db import models
from accounts.models import CustomUser
from core.models import Company, Branch


class LeadSource(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class LeadTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Lead(models.Model):

    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('follow_up', 'Follow Up'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        unique=True,
        db_index=True
    )

    email = models.EmailField(
        blank=True,
        null=True,
        db_index=True
    )

    country_interest = models.CharField(
        max_length=100,
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    visa_type = models.CharField(
        max_length=100,
        blank=True
    )

    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    source = models.ForeignKey(
        LeadSource,
        on_delete=models.SET_NULL,
        null=True
    )

    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tags = models.ManyToManyField(
        LeadTag,
        blank=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='new'
    )

    score = models.IntegerField(
        default=0
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CallLog(models.Model):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE
    )

    called_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True
    )

    outcome = models.CharField(
        max_length=200
    )

    notes = models.TextField(
        blank=True
    )

    call_time = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.outcome


class FollowUp(models.Model):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE
    )

    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True
    )

    follow_up_date = models.DateTimeField()

    notes = models.TextField(
        blank=True
    )

    completed = models.BooleanField(
        default=False
    )

    def __str__(self):
        return str(self.follow_up_date)


class LeadTimeline(models.Model):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE
    )

    action = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    performed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.action

class LeadAuditLog(models.Model):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE
    )

    field_changed = models.CharField(
        max_length=100
    )

    old_value = models.TextField(
        blank=True
    )

    new_value = models.TextField(
        blank=True
    )

    changed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True
    )

    changed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.field_changed
    
class LeadImportLog(models.Model):

    file_name = models.CharField(
        max_length=255
    )

    imported_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True
    )

    total_records = models.IntegerField(
        default=0
    )

    imported_records = models.IntegerField(
        default=0
    )

    duplicate_records = models.IntegerField(
        default=0
    )

    failed_records = models.IntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.file_name

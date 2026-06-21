from django.db import models
from accounts.models import CustomUser
from core.models import Company, Branch
from core.soft_delete import SoftDeleteModel


class LeadSource(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class LeadTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Lead(SoftDeleteModel):

    STATUS_CHOICES = [
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('called', 'Called'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('follow_up', 'Follow-up'),
        ('documents_requested', 'Documents Requested'),
        ('documents_received', 'Documents Received'),
        ('qualified', 'Qualified'),
        ('counsellor_assigned', 'Counsellor Assigned'),
        ('profile_evaluation', 'Profile Evaluation'),
        ('university_selection', 'University Selection'),
        ('application_ready', 'Application Ready'),
        ('converted', 'Converted'),
    ]

    PIPELINE_STAGES = [
        'qualified',
        'counsellor_assigned',
        'profile_evaluation',
        'university_selection',
        'application_ready',
        'converted',
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
        blank=True,
        related_name='assigned_leads',
    )

    assigned_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    assigned_counsellor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='counsellor_leads',
    )

    counsellor_assigned_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    qualified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    qualified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qualified_leads',
    )

    profile_evaluation_notes = models.TextField(
        blank=True,
    )

    recommended_countries = models.JSONField(
        default=list,
        blank=True,
    )

    recommended_universities = models.JSONField(
        default=list,
        blank=True,
    )

    application_readiness = models.JSONField(
        default=dict,
        blank=True,
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "phone"],
                condition=models.Q(is_deleted=False),
                name="unique_lead_phone_alive",
            ),
        ]
        indexes = [
            models.Index(
                fields=["company", "is_deleted", "status"],
                name="lead_co_del_status_idx",
            ),
            models.Index(
                fields=["company", "is_deleted", "-created_at"],
                name="lead_co_del_created_idx",
            ),
            models.Index(
                fields=[
                    "company",
                    "assigned_to",
                    "is_deleted",
                    "status",
                ],
                name="lead_co_assign_status_idx",
            ),
            models.Index(
                fields=[
                    "company",
                    "assigned_counsellor",
                    "is_deleted",
                    "status",
                ],
                name="lead_co_couns_status_idx",
            ),
        ]

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
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['called_by', '-call_time'],
                name='calllog_user_time_idx',
            ),
        ]

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

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["lead", "completed", "follow_up_date"],
                name="followup_lead_status_date_idx",
            ),
            models.Index(
                fields=[
                    "assigned_to",
                    "completed",
                    "follow_up_date",
                ],
                name="followup_user_status_date_idx",
            ),
        ]

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

    event_type = models.CharField(
        max_length=50,
        blank=True,
        default='',
        db_index=True,
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

    class Meta:
        indexes = [
            models.Index(
                fields=["lead", "-created_at"],
                name="timeline_lead_created_idx",
            ),
            models.Index(
                fields=["lead", "event_type", "-created_at"],
                name="timeline_lead_event_idx",
            ),
        ]

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

    class Meta:
        indexes = [
            models.Index(
                fields=["lead", "-changed_at"],
                name="auditlog_lead_changed_idx",
            ),
        ]

    def __str__(self):
        return self.field_changed
    
class LeadImportLog(models.Model):

    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('mapped', 'Mapped'),
        ('validated', 'Validated'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    DUPLICATE_RULE_CHOICES = [
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('phone_email', 'Phone + Email'),
    ]

    ASSIGNMENT_CHOICES = [
        ('manual', 'Manual'),
        ('round_robin', 'Round Robin'),
        ('even_distribution', 'Even Distribution'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    file_name = models.CharField(
        max_length=255,
    )

    stored_file = models.FileField(
        upload_to='lead_imports/',
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded',
    )

    column_mapping = models.JSONField(
        default=dict,
        blank=True,
    )

    source_columns = models.JSONField(
        default=list,
        blank=True,
    )

    preview_rows = models.JSONField(
        default=list,
        blank=True,
    )

    duplicate_rule = models.CharField(
        max_length=20,
        choices=DUPLICATE_RULE_CHOICES,
        default='phone',
    )

    assignment_mode = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_CHOICES,
        blank=True,
    )

    telecaller = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lead_imports',
    )

    error_report = models.JSONField(
        default=list,
        blank=True,
    )

    imported_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='lead_import_logs',
    )

    total_records = models.IntegerField(
        default=0,
    )

    imported_records = models.IntegerField(
        default=0,
    )

    duplicate_records = models.IntegerField(
        default=0,
    )

    failed_records = models.IntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['company', '-created_at'],
                name='import_company_created_idx',
            ),
        ]

    def __str__(self):
        return self.file_name

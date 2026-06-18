from django.db import models
import os
import uuid

from leads.models import Lead
from accounts.models import CustomUser
from core.models import Company, Branch
from core.soft_delete import SoftDeleteModel


class Student(SoftDeleteModel):

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
    portal_access = models.BooleanField(
    default=False
    )

    assigned_counselor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    student_id = models.CharField(
        max_length=50,
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student_id"],
                condition=models.Q(is_deleted=False),
                name="unique_student_id_alive",
            ),
        ]
        indexes = [
            models.Index(
                fields=["company", "is_deleted", "-created_at"],
                name="student_co_del_created_idx",
            ),
        ]

    def __str__(self):
        return self.student_id

class Application(SoftDeleteModel):

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('offer_received', 'Offer Received'),
        ('rejected', 'Rejected'),
        ('visa_processing', 'Visa Processing'),
        ('completed', 'Completed'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    university_name = models.CharField(
        max_length=255
    )

    course_name = models.CharField(
        max_length=255
    )

    intake = models.CharField(
        max_length=100
    )

    application_status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='draft'
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["student", "is_deleted", "-created_at"],
                name="app_stu_del_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.student.student_id} - {self.university_name}"
    
class Document(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    application = models.ForeignKey(
        Application,
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

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.document_name
class VisaCase(models.Model):

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('preparing', 'Preparing'),
        ('submitted', 'Submitted'),
        ('biometrics_completed', 'Biometrics Completed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE
    )

    submission_date = models.DateField(
        null=True,
        blank=True
    )

    biometrics_date = models.DateField(
        null=True,
        blank=True
    )

    decision_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='not_started'
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Visa - {self.application}"
    
class University(models.Model):

    name = models.CharField(
        max_length=255
    )

    country = models.CharField(
        max_length=100
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


class Course(models.Model):

    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=255
    )

    level = models.CharField(
        max_length=100
    )

    duration = models.CharField(
        max_length=100,
        blank=True
    )

    tuition_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

class OfferLetter(models.Model):

    STATUS_CHOICES = [
        ('conditional', 'Conditional'),
        ('unconditional', 'Unconditional'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE
    )

    offer_number = models.CharField(
        max_length=100,
        unique=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='conditional'
    )

    issue_date = models.DateField(
        null=True,
        blank=True
    )

    acceptance_deadline = models.DateField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.offer_number
class SupportTicket(models.Model):

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    subject = models.CharField(
        max_length=255
    )

    description = models.TextField()

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='open'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.subject


class TicketComment(models.Model):

    ticket = models.ForeignKey(
        SupportTicket,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.ticket} - {self.user}"


def student_document_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    return (
        f"student_documents/"
        f"{instance.company_id}/"
        f"{instance.student_id}/"
        f"{safe_name}"
    )


class StudentDocument(SoftDeleteModel):

    DOCUMENT_TYPE_CHOICES = [
        ('10th_marksheet', '10th Marksheet'),
        ('12th_marksheet', '12th Marksheet'),
        ('degree_certificate', 'Degree Certificate'),
        ('degree_transcript', 'Degree Transcript'),
        ('passport', 'Passport'),
        ('ielts', 'IELTS'),
        ('pte', 'PTE'),
        ('sop', 'SOP'),
        ('lor', 'LOR'),
        ('resume', 'Resume'),
        ('bank_statement', 'Bank Statement'),
        ('sponsor_letter', 'Sponsor Letter'),
        ('sponsor_id', 'Sponsor ID'),
        ('income_proof', 'Income Proof'),
        ('education_loan_letter', 'Education Loan Letter'),
        ('experience_letter', 'Experience Letter'),
        ('payslip', 'Payslip'),
        ('employment_offer_letter', 'Employment Offer Letter'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('uploaded', 'Uploaded'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    CATEGORY_MAP = {
        '10th_marksheet': 'academic',
        '12th_marksheet': 'academic',
        'degree_certificate': 'academic',
        'degree_transcript': 'academic',
        'passport': 'identity',
        'ielts': 'language',
        'pte': 'language',
        'sop': 'application',
        'lor': 'application',
        'resume': 'application',
        'bank_statement': 'financial',
        'sponsor_letter': 'financial',
        'sponsor_id': 'financial',
        'income_proof': 'financial',
        'education_loan_letter': 'financial',
        'experience_letter': 'professional',
        'payslip': 'professional',
        'employment_offer_letter': 'professional',
        'other': 'other',
    }

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='documents',
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='requested',
    )

    document_number = models.CharField(
        max_length=100,
        blank=True,
    )

    issue_date = models.DateField(
        null=True,
        blank=True,
    )

    expiry_date = models.DateField(
        null=True,
        blank=True,
    )

    version = models.PositiveIntegerField(
        default=1,
    )

    file = models.FileField(
        upload_to=student_document_upload_path,
        blank=True,
        null=True,
    )

    original_filename = models.CharField(
        max_length=255,
        blank=True,
    )

    file_size = models.PositiveIntegerField(
        default=0,
    )

    mime_type = models.CharField(
        max_length=100,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    rejection_remarks = models.TextField(
        blank=True,
    )

    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_student_documents',
    )

    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_student_documents',
    )

    approved_at = models.DateTimeField(
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
                fields=['student', '-created_at'],
                name='studdoc_student_created_idx',
            ),
            models.Index(
                fields=['company', 'document_type'],
                name='studdoc_company_type_idx',
            ),
            models.Index(
                fields=['company', 'status'],
                name='studdoc_company_status_idx',
            ),
        ]

    @property
    def category(self):
        return self.CATEGORY_MAP.get(
            self.document_type,
            'other',
        )

    def refresh_expiry_status(self):
        from django.utils import timezone

        if (
            self.expiry_date
            and self.expiry_date < timezone.localdate()
            and self.status == 'approved'
        ):
            self.status = 'expired'

    def save(self, *args, **kwargs):
        self.refresh_expiry_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.get_document_type_display()}"
        )


class DocumentChecklistTemplate(models.Model):

    TEMPLATE_CODE_CHOICES = [
        ('uk_student', 'UK Student'),
        ('australia_student', 'Australia Student'),
        ('canada_student', 'Canada Student'),
        ('germany_student', 'Germany Student'),
        ('work_visa_applicant', 'Work Visa Applicant'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    code = models.CharField(
        max_length=50,
        choices=TEMPLATE_CODE_CHOICES,
    )

    name = models.CharField(
        max_length=255,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'code'],
                name='uniq_checklist_template_company_code',
            ),
        ]

    def __str__(self):
        return self.name


class DocumentChecklistTemplateItem(models.Model):

    template = models.ForeignKey(
        DocumentChecklistTemplate,
        on_delete=models.CASCADE,
        related_name='items',
    )

    document_type = models.CharField(
        max_length=50,
        choices=StudentDocument.DOCUMENT_TYPE_CHOICES,
    )

    is_required = models.BooleanField(
        default=True,
    )

    sort_order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ['sort_order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['template', 'document_type'],
                name='uniq_checklist_template_item_type',
            ),
        ]

    def __str__(self):
        return (
            f"{self.template.name} - "
            f"{self.document_type}"
        )
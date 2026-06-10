from django.db import models

from admissions.models import Student
from workvisa.models import WorkVisaCase
from knowledgebase.models import Country


class ChecklistTemplate(models.Model):

    PROCESS_TYPES = [
        ('study_abroad', 'Study Abroad'),
        ('work_visa', 'Work Visa'),
    ]

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE
    )

    process_type = models.CharField(
        max_length=50,
        choices=PROCESS_TYPES
    )

    name = models.CharField(
        max_length=255
    )

    def __str__(self):
        return self.name


class ChecklistItem(models.Model):

    template = models.ForeignKey(
        ChecklistTemplate,
        on_delete=models.CASCADE,
        related_name='items'
    )

    document_name = models.CharField(
        max_length=255
    )

    mandatory = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.document_name


class StudentChecklist(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    checklist_item = models.ForeignKey(
        ChecklistItem,
        on_delete=models.CASCADE
    )

    is_completed = models.BooleanField(
        default=False
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.student} - {self.checklist_item}"


class WorkVisaChecklist(models.Model):

    visa_case = models.ForeignKey(
        WorkVisaCase,
        on_delete=models.CASCADE
    )

    checklist_item = models.ForeignKey(
        ChecklistItem,
        on_delete=models.CASCADE
    )

    is_completed = models.BooleanField(
        default=False
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.visa_case} - {self.checklist_item}"
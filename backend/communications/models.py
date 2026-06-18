from django.db import models

from accounts.models import CustomUser
from admissions.models import Student
from core.models import Company
from leads.models import Lead


class CommunicationNote(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='communication_notes',
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='communication_notes',
    )

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='communication_notes',
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['company', '-created_at'],
                name='comm_note_co_created_idx',
            ),
        ]

    def __str__(self):
        return self.content[:50]


class EmailLog(models.Model):

    DIRECTION_CHOICES = [
        ('outbound', 'Outbound'),
        ('inbound', 'Inbound'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='email_logs',
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='email_logs',
    )

    logged_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='email_logs',
    )

    recipient_email = models.EmailField()

    subject = models.CharField(
        max_length=255,
    )

    body = models.TextField(
        blank=True,
    )

    direction = models.CharField(
        max_length=20,
        choices=DIRECTION_CHOICES,
        default='outbound',
    )

    sent_at = models.DateTimeField(
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(
                fields=['company', '-sent_at'],
                name='email_log_co_sent_idx',
            ),
        ]

    def __str__(self):
        return self.subject


class WhatsAppLog(models.Model):

    DIRECTION_CHOICES = [
        ('outbound', 'Outbound'),
        ('inbound', 'Inbound'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='whatsapp_logs',
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='whatsapp_logs',
    )

    logged_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='whatsapp_logs',
    )

    contact_number = models.CharField(
        max_length=20,
    )

    message = models.TextField()

    direction = models.CharField(
        max_length=20,
        choices=DIRECTION_CHOICES,
        default='outbound',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['company', '-created_at'],
                name='wa_log_co_created_idx',
            ),
        ]

    def __str__(self):
        return self.contact_number

from django.db import models

from core.models import Company
from accounts.models import CustomUser


class WhatsAppAccount(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE
    )

    phone_number = models.CharField(
        max_length=20,
        unique=True
    )

    session_id = models.CharField(
        max_length=255,
        unique=True
    )

    is_connected = models.BooleanField(
        default=False
    )

    last_connected_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.phone_number}"


class WhatsAppMessage(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    MESSAGE_TYPE_CHOICES = [
        ('manual', 'Manual'),
        ('follow_up', 'Follow-up'),
        ('document_reminder', 'Document Reminder'),
        ('offer_reminder', 'Offer Reminder'),
        ('visa_update', 'Visa Update'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    account = models.ForeignKey(
        WhatsAppAccount,
        on_delete=models.CASCADE
    )

    lead = models.ForeignKey(
        'leads.Lead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_messages',
    )

    student = models.ForeignKey(
        'admissions.Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_messages',
    )

    recipient_number = models.CharField(
        max_length=20
    )

    message = models.TextField()

    message_type = models.CharField(
        max_length=30,
        choices=MESSAGE_TYPE_CHOICES,
        default='manual',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    response_data = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.recipient_number


class WhatsAppReminderLog(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
    )

    alert_key = models.CharField(
        max_length=160,
        unique=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=['company', '-created_at'],
                name='wa_reminder_co_created_idx',
            ),
        ]

    def __str__(self):
        return self.alert_key
    
class WhatsAppServer(models.Model):

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE
    )

    base_url = models.URLField()

    api_key = models.CharField(
        max_length=255
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.company.name
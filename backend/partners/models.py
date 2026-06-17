from django.db import models

from core.models import Company


class PartnerUniversity(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=255
    )

    country = models.CharField(
        max_length=100
    )

    website = models.URLField(
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


class PartnerContact(models.Model):

    university = models.ForeignKey(
        PartnerUniversity,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=255
    )

    designation = models.CharField(
        max_length=255,
        blank=True
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=50,
        blank=True
    )

    def __str__(self):
        return self.name


class PartnerAgreement(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    ]

    university = models.ForeignKey(
        PartnerUniversity,
        on_delete=models.CASCADE
    )

    agreement_date = models.DateField()

    expiry_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.university} Agreement"


class PartnerCommission(models.Model):

    university = models.ForeignKey(
        PartnerUniversity,
        on_delete=models.CASCADE
    )

    course_level = models.CharField(
        max_length=100
    )

    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f"{self.university} - "
            f"{self.commission_percentage}%"
        )
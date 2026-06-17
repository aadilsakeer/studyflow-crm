from django.db import models


class Module(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=50,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name
    
from core.models import Company


class SubscriptionPlan(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    yearly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


class CompanyModule(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE
    )

    is_enabled = models.BooleanField(
        default=True
    )

    class Meta:
        unique_together = (
            'company',
            'module'
        )

    def __str__(self):
        return f"{self.company} - {self.module}"


class CompanySubscription(models.Model):

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.company} - {self.plan}"
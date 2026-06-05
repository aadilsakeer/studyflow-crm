from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)

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
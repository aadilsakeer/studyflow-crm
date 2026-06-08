from django.db import models


class Country(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=10,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


class CountryGuide(models.Model):

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    content = models.TextField()

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class CountryIntake(models.Model):

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE
    )

    intake_name = models.CharField(
        max_length=100
    )

    documentation_start = models.CharField(
        max_length=100
    )

    application_deadline = models.CharField(
        max_length=100,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.country} - {self.intake_name}"


class CountryRequirement(models.Model):

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    details = models.TextField()

    def __str__(self):
        return self.title


class CountryHighlight(models.Model):

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=255
    )

    details = models.TextField()

    def __str__(self):
        return self.title


class CountryScholarship(models.Model):

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE
    )

    scholarship_name = models.CharField(
        max_length=255
    )

    amount = models.CharField(
        max_length=100,
        blank=True
    )

    details = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.scholarship_name
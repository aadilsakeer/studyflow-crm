from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import Company, Branch


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Permission(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    code = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (
            'role',
            'permission'
        )

    def __str__(self):
        return f"{self.role} - {self.permission}"


class CustomUser(AbstractUser):

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username


class StaffProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE
    )

    joining_date = models.DateField(
        null=True,
        blank=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    emergency_contact = models.CharField(
        max_length=20,
        blank=True
    )

    reporting_manager = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )

    is_active_employee = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.user.username
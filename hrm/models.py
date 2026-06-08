from django.db import models

from accounts.models import CustomUser
from core.models import Company


class Attendance(models.Model):

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('leave', 'Leave'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    attendance_date = models.DateField()

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='present'
    )

    check_in = models.TimeField(
        null=True,
        blank=True
    )

    check_out = models.TimeField(
        null=True,
        blank=True
    )

    remarks = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.employee} - {self.attendance_date}"


class LeaveRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending'
    )

    applied_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee} Leave"
    
class EmployeeLetter(models.Model):

    LETTER_TYPES = [
        ('appointment', 'Appointment Letter'),
        ('confirmation', 'Confirmation Letter'),
        ('experience', 'Experience Letter'),
        ('relieving', 'Relieving Letter'),
        ('termination', 'Termination Letter'),
        ('warning', 'Warning Letter'),
    ]

    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    letter_type = models.CharField(
        max_length=50,
        choices=LETTER_TYPES
    )

    issue_date = models.DateField()

    subject = models.CharField(
        max_length=255
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee} - {self.letter_type}"

class Resignation(models.Model):

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    resignation_date = models.DateField()

    last_working_day = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='submitted'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee} Resignation"
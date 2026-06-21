from django.conf import settings
from django.db import models

from accounts.models import CustomUser
from core.models import Company


class Employee(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='hrm_employees',
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile',
    )
    employee_code = models.CharField(max_length=32)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
    )
    designation = models.CharField(max_length=120, blank=True)
    reporting_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports',
    )
    salary_structure = models.JSONField(default=dict, blank=True)
    leave_balance = models.JSONField(
        default=dict,
        blank=True,
        help_text='Keys: annual, sick, used_annual, used_sick',
    )
    shift = models.ForeignKey(
        'Shift',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
    )
    joined_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('company', 'employee_code')]
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class Shift(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='shifts',
    )
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_minutes = models.PositiveSmallIntegerField(default=15)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AssetAssignment(models.Model):

    ASSET_LAPTOP = 'laptop'
    ASSET_PHONE = 'phone'
    ASSET_ACCESSORY = 'accessory'

    ASSET_TYPES = (
        (ASSET_LAPTOP, 'Laptop'),
        (ASSET_PHONE, 'Phone'),
        (ASSET_ACCESSORY, 'Accessory'),
    )

    STATUS_ASSIGNED = 'assigned'
    STATUS_RETURNED = 'returned'

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='asset_assignments',
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='asset_assignments',
    )
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    asset_name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, default=STATUS_ASSIGNED)
    assigned_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.asset_name} → {self.employee}'


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

    check_in_at = models.DateTimeField(null=True, blank=True)
    check_out_at = models.DateTimeField(null=True, blank=True)
    check_in_latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True,
    )
    check_in_longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True,
    )
    check_out_latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True,
    )
    check_out_longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True,
    )
    is_late = models.BooleanField(default=False)
    shift = models.ForeignKey(
        Shift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records',
    )
    employee_profile = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records',
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

    leave_type = models.CharField(max_length=50, default='annual')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves',
    )
    reviewer_notes = models.TextField(blank=True)
    employee_profile = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_requests',
    )

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
    
class Department(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name
    
class Payroll(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE
    )

    employee = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )

    month = models.CharField(
        max_length=20
    )

    year = models.PositiveIntegerField()

    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    net_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    salary_structure = models.JSONField(default=dict, blank=True)
    payslip = models.JSONField(default=dict, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    employee_profile = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payrolls',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee} - {self.month} {self.year}"
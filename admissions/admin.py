from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'student_id',
        'destination_country',
        'preferred_university',
        'status',
        'assigned_counselor',
        'company'
    )

    search_fields = (
        'student_id',
        'passport_number',
        'preferred_university'
    )

    list_filter = (
        'status',
        'destination_country',
        'company'
    )
from django.contrib import admin
from .models import Student, Application


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


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'university_name',
        'course_name',
        'intake',
        'application_status'
    )

    search_fields = (
        'university_name',
        'course_name'
    )

    list_filter = (
        'application_status',
        'intake'
    )
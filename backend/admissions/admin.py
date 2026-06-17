from django.contrib import admin

from .models import (
    Student,
    Application,
    Document,
    VisaCase,
    University,
    Course,
    OfferLetter,
)


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


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'document_name',
        'application',
        'status',
        'uploaded_at'
    )

    search_fields = (
        'document_name',
    )

    list_filter = (
        'status',
    )


@admin.register(VisaCase)
class VisaCaseAdmin(admin.ModelAdmin):
    list_display = (
        'application',
        'status',
        'submission_date',
        'decision_date'
    )

    search_fields = (
        'application__university_name',
    )

    list_filter = (
        'status',
    )


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'country',
        'city',
        'is_active'
    )

    search_fields = (
        'name',
        'country',
        'city'
    )

    list_filter = (
        'country',
        'is_active'
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'university',
        'level',
        'tuition_fee'
    )

    search_fields = (
        'name',
        'university__name'
    )

    list_filter = (
        'level',
        'university'
    )

@admin.register(OfferLetter)
class OfferLetterAdmin(admin.ModelAdmin):
    list_display = (
        'offer_number',
        'application',
        'status',
        'issue_date',
        'acceptance_deadline'
    )

    search_fields = (
        'offer_number',
    )

    list_filter = (
        'status',
    )
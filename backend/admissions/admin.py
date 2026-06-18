from django.contrib import admin

from .models import (
    Student,
    Application,
    Document,
    VisaCase,
    University,
    Course,
    OfferLetter,
    StudentDocument,
    DocumentChecklistTemplate,
    DocumentChecklistTemplateItem,
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
        'student',
        'country',
        'visa_type',
        'status',
        'submission_date',
        'decision_date',
        'company',
    )

    search_fields = (
        'student__student_id',
        'visa_number',
        'country',
    )

    list_filter = (
        'status',
        'visa_type',
        'country',
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
        'student',
        'university',
        'offer_type',
        'status',
        'issue_date',
        'expiry_date',
        'is_deleted',
    )
    list_filter = (
        'offer_type',
        'status',
        'is_deleted',
        'company',
    )
    search_fields = (
        'offer_number',
        'student__student_id',
        'university',
    )


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'document_type',
        'original_filename',
        'company',
        'is_deleted',
        'created_at',
    )

    list_filter = (
        'document_type',
        'is_deleted',
        'company',
    )

    search_fields = (
        'original_filename',
        'student__student_id',
        'document_number',
    )


@admin.register(DocumentChecklistTemplate)
class DocumentChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'code',
        'company',
        'is_active',
    )
    list_filter = ('code', 'is_active', 'company')


@admin.register(DocumentChecklistTemplateItem)
class DocumentChecklistTemplateItemAdmin(admin.ModelAdmin):
    list_display = (
        'template',
        'document_type',
        'is_required',
        'sort_order',
    )
    list_filter = ('template', 'is_required')
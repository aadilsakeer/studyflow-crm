from rest_framework import serializers

from core.validators import (
    get_request_company,
    validate_application_in_company,
    validate_student_in_company,
    validate_ticket_in_company,
)

from .models import (
    Student,
    Application,
    Document,
    VisaCase,
    University,
    Course,
    OfferLetter,
    SupportTicket,
    TicketComment
)


class StudentSerializer(serializers.ModelSerializer):

    lead_name = serializers.SerializerMethodField(
        read_only=True,
    )
    lead_phone = serializers.SerializerMethodField(
        read_only=True,
    )
    lead_email = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Student
        fields = (
            "id",
            "lead",
            "company",
            "branch",
            "portal_access",
            "assigned_counselor",
            "student_id",
            "passport_number",
            "destination_country",
            "preferred_university",
            "intake",
            "status",
            "notes",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "created_at",
            "updated_at",
            "lead_name",
            "lead_phone",
            "lead_email",
        )
        read_only_fields = (
            "lead",
            "company",
            "student_id",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "created_at",
            "updated_at",
        )

    def get_lead_name(self, obj):
        return (
            f"{obj.lead.first_name} "
            f"{obj.lead.last_name}".strip()
        )

    def get_lead_phone(self, obj):
        return obj.lead.phone

    def get_lead_email(self, obj):
        return obj.lead.email


class ApplicationSerializer(serializers.ModelSerializer):

    student_name = serializers.SerializerMethodField(
        read_only=True,
    )
    student_code = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Application
        fields = (
            "id",
            "student",
            "university_name",
            "course_name",
            "intake",
            "application_status",
            "notes",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "created_at",
            "student_name",
            "student_code",
        )
        read_only_fields = (
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "created_at",
        )

    def get_student_name(self, obj):
        lead = obj.student.lead
        return (
            f"{lead.first_name} "
            f"{lead.last_name}".strip()
        )

    def get_student_code(self, obj):
        return obj.student.student_id

    def validate_student(self, student):
        company = get_request_company(
            self.context,
        )
        return validate_student_in_company(
            student,
            company,
        )


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = (
            "id",
            "application",
            "document_name",
            "status",
            "remarks",
            "uploaded_at",
        )
        read_only_fields = (
            "uploaded_at",
        )

    def validate_application(self, application):
        company = get_request_company(
            self.context,
        )
        return validate_application_in_company(
            application,
            company,
        )


class VisaCaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisaCase
        fields = (
            "id",
            "application",
            "submission_date",
            "biometrics_date",
            "decision_date",
            "status",
            "remarks",
            "created_at",
        )
        read_only_fields = (
            "created_at",
        )

    def validate_application(self, application):
        company = get_request_company(
            self.context,
        )
        return validate_application_in_company(
            application,
            company,
        )


class UniversitySerializer(serializers.ModelSerializer):

    class Meta:
        model = University
        fields = (
            "id",
            "name",
            "country",
            "city",
            "website",
            "is_active",
        )


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = (
            "id",
            "university",
            "name",
            "level",
            "duration",
            "tuition_fee",
        )


class OfferLetterSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferLetter
        fields = (
            "id",
            "application",
            "offer_number",
            "status",
            "issue_date",
            "acceptance_deadline",
            "notes",
            "created_at",
        )
        read_only_fields = (
            "created_at",
        )

    def validate_application(self, application):
        company = get_request_company(
            self.context,
        )
        return validate_application_in_company(
            application,
            company,
        )


class SupportTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupportTicket
        fields = (
            "id",
            "student",
            "subject",
            "description",
            "status",
            "created_at",
        )
        read_only_fields = (
            "created_at",
        )

    def validate_student(self, student):
        company = get_request_company(
            self.context,
        )
        return validate_student_in_company(
            student,
            company,
        )


class TicketCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketComment
        fields = (
            "id",
            "ticket",
            "user",
            "comment",
            "created_at",
        )
        read_only_fields = (
            "user",
            "created_at",
        )

    def validate_ticket(self, ticket):
        company = get_request_company(
            self.context,
        )
        return validate_ticket_in_company(
            ticket,
            company,
        )

from rest_framework import serializers

from core.validators import (
    get_request_company,
    validate_application_in_company,
    validate_lead_in_company,
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
        fields = "__all__"
        read_only_fields = (
            "student_id",
            "lead",
            "company",
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
        fields = "__all__"

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
        fields = "__all__"

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
        fields = "__all__"

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
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = "__all__"


class OfferLetterSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferLetter
        fields = "__all__"

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
        fields = "__all__"

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
        fields = "__all__"

    def validate_ticket(self, ticket):
        company = get_request_company(
            self.context,
        )
        return validate_ticket_in_company(
            ticket,
            company,
        )

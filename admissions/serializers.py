from rest_framework import serializers

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
        request = self.context.get("request")

        if not request:
            return student

        company = getattr(
            request.user,
            "company",
            None,
        )

        if (
            company
            and student.company_id != company.id
        ):
            raise serializers.ValidationError(
                "Student not found in your company."
            )

        return student


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = "__all__"


class VisaCaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisaCase
        fields = "__all__"


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


class SupportTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupportTicket
        fields = "__all__"


class TicketCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketComment
        fields = "__all__"
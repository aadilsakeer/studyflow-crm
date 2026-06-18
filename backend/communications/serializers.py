from django.utils import timezone
from rest_framework import serializers

from admissions.models import Student
from core.validators import (
    get_request_company,
    validate_lead_in_company,
    validate_student_in_company,
)
from leads.models import Lead

from .models import CommunicationNote, EmailLog, WhatsAppLog


class LeadStudentMixin(serializers.Serializer):

    def validate(self, attrs):
        attrs = super().validate(attrs)
        company = get_request_company(self.context)

        lead = attrs.get(
            'lead',
            getattr(self.instance, 'lead', None),
        )
        student = attrs.get(
            'student',
            getattr(self.instance, 'student', None),
        )

        if not lead and not student:
            raise serializers.ValidationError(
                {
                    'detail': (
                        'Either lead or student '
                        'is required.'
                    ),
                },
            )

        if lead:
            validate_lead_in_company(lead, company)

        if student:
            validate_student_in_company(
                student,
                company,
            )

            if lead and student.lead_id != lead.id:
                raise serializers.ValidationError(
                    {
                        'student': (
                            'Student does not belong '
                            'to this lead.'
                        ),
                    },
                )

        return attrs


class CommunicationNoteSerializer(
    LeadStudentMixin,
    serializers.ModelSerializer,
):

    author_name = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = CommunicationNote
        fields = (
            'id',
            'lead',
            'student',
            'author',
            'author_name',
            'content',
            'created_at',
        )
        read_only_fields = (
            'author',
            'created_at',
        )

    def validate_lead(self, lead):
        if not lead:
            return lead

        company = get_request_company(self.context)
        return validate_lead_in_company(lead, company)

    def validate_student(self, student):
        if not student:
            return student

        company = get_request_company(self.context)
        return validate_student_in_company(
            student,
            company,
        )

    def get_author_name(self, obj):
        if not obj.author:
            return None

        return (
            obj.author.get_full_name()
            or obj.author.username
        )


class EmailLogSerializer(
    LeadStudentMixin,
    serializers.ModelSerializer,
):

    logged_by_name = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = EmailLog
        fields = (
            'id',
            'lead',
            'student',
            'logged_by',
            'logged_by_name',
            'recipient_email',
            'subject',
            'body',
            'direction',
            'sent_at',
            'created_at',
        )
        read_only_fields = (
            'logged_by',
            'created_at',
        )

    def validate_lead(self, lead):
        if not lead:
            return lead

        company = get_request_company(self.context)
        return validate_lead_in_company(lead, company)

    def validate_student(self, student):
        if not student:
            return student

        company = get_request_company(self.context)
        return validate_student_in_company(
            student,
            company,
        )

    def get_logged_by_name(self, obj):
        if not obj.logged_by:
            return None

        return (
            obj.logged_by.get_full_name()
            or obj.logged_by.username
        )


class WhatsAppLogSerializer(
    LeadStudentMixin,
    serializers.ModelSerializer,
):

    logged_by_name = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = WhatsAppLog
        fields = (
            'id',
            'lead',
            'student',
            'logged_by',
            'logged_by_name',
            'contact_number',
            'message',
            'direction',
            'created_at',
        )
        read_only_fields = (
            'logged_by',
            'created_at',
        )

    def validate_lead(self, lead):
        if not lead:
            return lead

        company = get_request_company(self.context)
        return validate_lead_in_company(lead, company)

    def validate_student(self, student):
        if not student:
            return student

        company = get_request_company(self.context)
        return validate_student_in_company(
            student,
            company,
        )

    def get_logged_by_name(self, obj):
        if not obj.logged_by:
            return None

        return (
            obj.logged_by.get_full_name()
            or obj.logged_by.username
        )

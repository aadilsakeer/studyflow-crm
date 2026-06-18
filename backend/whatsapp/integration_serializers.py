from rest_framework import serializers

from core.validators import (
    get_request_company,
    validate_lead_in_company,
    validate_student_in_company,
)

from leads.models import Lead
from admissions.models import Student


class WhatsAppSendSerializer(serializers.Serializer):

    message = serializers.CharField()
    recipient_number = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    lead = serializers.PrimaryKeyRelatedField(
        queryset=Lead.objects.all(),
        required=False,
        allow_null=True,
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=False,
        allow_null=True,
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

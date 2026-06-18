from rest_framework import serializers

from accounts.services.permission_service import user_has_permission
from accounts.constants import PERM_VISAS_PROCESS
from core.validators import (
    get_request_company,
    validate_application_in_company,
    validate_student_in_company,
)

from .models import StudentDocument, VisaCase


class VisaCaseSerializer(serializers.ModelSerializer):

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
    )
    visa_type_display = serializers.CharField(
        source='get_visa_type_display',
        read_only=True,
    )

    class Meta:
        model = VisaCase
        fields = (
            'id',
            'company',
            'student',
            'application',
            'offer_letter',
            'student_documents',
            'country',
            'visa_type',
            'visa_type_display',
            'visa_number',
            'application_date',
            'appointment_date',
            'submission_date',
            'decision_date',
            'status',
            'status_display',
            'notes',
            'is_deleted',
            'deleted_at',
            'deleted_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'company',
            'status',
            'status_display',
            'visa_type_display',
            'is_deleted',
            'deleted_at',
            'deleted_by',
            'created_at',
            'updated_at',
        )

    def validate_student(self, student):
        company = get_request_company(self.context)
        return validate_student_in_company(student, company)

    def validate_application(self, application):
        if application is None:
            return application

        company = get_request_company(self.context)
        return validate_application_in_company(
            application,
            company,
        )

    def _validate_offer_letter(self, offer_letter, student):
        if offer_letter is None:
            return

        if offer_letter.student_id != student.id:
            raise serializers.ValidationError(
                'Offer letter does not belong to this student.'
            )

    def _validate_student_documents(self, documents, student):
        if not documents:
            return

        for document in documents:
            if document.student_id != student.id:
                raise serializers.ValidationError(
                    'All documents must belong to this student.'
                )

    def validate(self, attrs):
        instance = self.instance
        student = attrs.get(
            'student',
            instance.student if instance else None,
        )
        offer_letter = attrs.get(
            'offer_letter',
            instance.offer_letter if instance else None,
        )
        documents = attrs.get('student_documents')

        if student:
            self._validate_offer_letter(offer_letter, student)

            if documents is not None:
                self._validate_student_documents(
                    documents,
                    student,
                )

        if instance and instance.status != 'draft':
            request = self.context.get('request')

            if request and not user_has_permission(
                request.user,
                PERM_VISAS_PROCESS,
            ):
                raise serializers.ValidationError(
                    'Only draft visa cases can be edited.'
                )

        return attrs

    def create(self, validated_data):
        student = validated_data['student']
        documents = validated_data.pop(
            'student_documents',
            [],
        )

        validated_data['company'] = student.company
        validated_data['status'] = 'draft'

        visa_case = super().create(validated_data)

        if documents:
            visa_case.student_documents.set(documents)

        return visa_case

    def update(self, instance, validated_data):
        documents = validated_data.pop(
            'student_documents',
            None,
        )

        visa_case = super().update(
            instance,
            validated_data,
        )

        if documents is not None:
            visa_case.student_documents.set(documents)

        return visa_case


class VisaCaseWorkflowSerializer(serializers.Serializer):

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    appointment_date = serializers.DateField(
        required=False,
    )
    submission_date = serializers.DateField(
        required=False,
    )
    decision_date = serializers.DateField(
        required=False,
    )
    visa_number = serializers.CharField(
        required=False,
        allow_blank=True,
    )

import os

from rest_framework import serializers

from core.validators import (
    get_request_company,
    validate_application_in_company,
)

from .models import OfferLetter, StudentDocument

ALLOWED_EXTENSIONS = {
    '.pdf',
    '.jpg',
    '.jpeg',
    '.png',
    '.doc',
    '.docx',
}
MAX_FILE_SIZE = 10 * 1024 * 1024


class OfferLetterSerializer(serializers.ModelSerializer):

    offer_type_display = serializers.CharField(
        source='get_offer_type_display',
        read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
    )
    document_url = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = OfferLetter
        fields = (
            'id',
            'company',
            'student',
            'application',
            'university',
            'course',
            'offer_type',
            'offer_type_display',
            'status',
            'status_display',
            'offer_number',
            'issue_date',
            'expiry_date',
            'tuition_fee',
            'deposit_amount',
            'notes',
            'offer_document',
            'document_url',
            'original_filename',
            'file_size',
            'mime_type',
            'student_document',
            'is_deleted',
            'deleted_at',
            'deleted_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'company',
            'student',
            'university',
            'course',
            'status',
            'document_url',
            'original_filename',
            'file_size',
            'mime_type',
            'student_document',
            'offer_type_display',
            'status_display',
            'is_deleted',
            'deleted_at',
            'deleted_by',
            'created_at',
            'updated_at',
        )

    def get_document_url(self, obj):
        if not obj.offer_document:
            return None

        request = self.context.get('request')

        if request:
            return request.build_absolute_uri(
                f'/api/offer-letters/{obj.pk}/download/'
            )

        return obj.offer_document.url

    def validate_application(self, application):
        company = get_request_company(
            self.context,
        )
        return validate_application_in_company(
            application,
            company,
        )

    def validate_offer_document(self, file_obj):
        if not file_obj:
            return file_obj

        ext = os.path.splitext(
            file_obj.name,
        )[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                'Unsupported file type.'
            )

        if file_obj.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                'File size must not exceed 10 MB.'
            )

        return file_obj

    def create(self, validated_data):
        application = validated_data['application']
        file_obj = validated_data.get('offer_document')

        validated_data['company'] = (
            application.student.company
        )
        validated_data['student'] = application.student
        validated_data['university'] = (
            application.university_name
        )
        validated_data['course'] = (
            application.course_name
        )
        validated_data['status'] = 'received'

        if file_obj:
            validated_data['original_filename'] = (
                file_obj.name
            )
            validated_data['file_size'] = file_obj.size
            validated_data['mime_type'] = (
                file_obj.content_type or ''
            )

        offer = super().create(validated_data)

        if file_obj:
            self._sync_student_document(offer)

        return offer

    def update(self, instance, validated_data):
        file_obj = validated_data.get('offer_document')

        if file_obj:
            validated_data['original_filename'] = (
                file_obj.name
            )
            validated_data['file_size'] = file_obj.size
            validated_data['mime_type'] = (
                file_obj.content_type or ''
            )

        offer = super().update(
            instance,
            validated_data,
        )

        if file_obj:
            self._sync_student_document(offer)

        return offer

    def _sync_student_document(self, offer):
        request = self.context.get('request')

        if not request or not offer.offer_document:
            return

        if offer.student_document_id:
            doc = offer.student_document
            doc.file = offer.offer_document
            doc.original_filename = (
                offer.original_filename
            )
            doc.file_size = offer.file_size
            doc.mime_type = offer.mime_type
            doc.status = 'uploaded'
            doc.version += 1
            doc.save()
            return

        doc = StudentDocument.objects.create(
            student=offer.student,
            company=offer.company,
            document_type='university_offer_letter',
            status='uploaded',
            file=offer.offer_document,
            original_filename=offer.original_filename,
            file_size=offer.file_size,
            mime_type=offer.mime_type,
            notes=(
                f'Linked to offer {offer.offer_number}'
            ),
            uploaded_by=request.user,
        )
        offer.student_document = doc
        offer.save(
            update_fields=['student_document'],
        )


class OfferLetterReviewSerializer(
    serializers.Serializer,
):
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )

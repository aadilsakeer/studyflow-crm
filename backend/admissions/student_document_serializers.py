import os

from rest_framework import serializers

from core.validators import (
    get_request_company,
    validate_student_in_company,
)

from .models import StudentDocument

ALLOWED_EXTENSIONS = {
    '.pdf',
    '.jpg',
    '.jpeg',
    '.png',
    '.doc',
    '.docx',
}
MAX_FILE_SIZE = 10 * 1024 * 1024


class StudentDocumentSerializer(serializers.ModelSerializer):

    file_url = serializers.SerializerMethodField(
        read_only=True,
    )
    preview_url = serializers.SerializerMethodField(
        read_only=True,
    )
    uploaded_by_name = serializers.SerializerMethodField(
        read_only=True,
    )
    approved_by_name = serializers.SerializerMethodField(
        read_only=True,
    )
    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True,
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
    )
    category = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = StudentDocument
        fields = (
            'id',
            'student',
            'company',
            'category',
            'document_type',
            'document_type_display',
            'status',
            'status_display',
            'document_number',
            'issue_date',
            'expiry_date',
            'version',
            'file',
            'file_url',
            'preview_url',
            'original_filename',
            'file_size',
            'mime_type',
            'notes',
            'rejection_remarks',
            'uploaded_by',
            'uploaded_by_name',
            'approved_by',
            'approved_by_name',
            'approved_at',
            'is_deleted',
            'deleted_at',
            'deleted_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'company',
            'category',
            'file_url',
            'preview_url',
            'original_filename',
            'file_size',
            'mime_type',
            'uploaded_by',
            'uploaded_by_name',
            'approved_by',
            'approved_by_name',
            'approved_at',
            'version',
            'status',
            'rejection_remarks',
            'document_type_display',
            'status_display',
            'is_deleted',
            'deleted_at',
            'deleted_by',
            'created_at',
            'updated_at',
        )

    def get_file_url(self, obj):
        if not obj.file:
            return None

        request = self.context.get('request')

        if request:
            return request.build_absolute_uri(
                f'/api/student-documents/{obj.pk}/download/'
            )

        return obj.file.url

    def get_preview_url(self, obj):
        if not obj.file:
            return None

        request = self.context.get('request')

        if request:
            return request.build_absolute_uri(
                f'/api/student-documents/{obj.pk}/preview/'
            )

        return None

    def get_uploaded_by_name(self, obj):
        if not obj.uploaded_by:
            return None

        return (
            obj.uploaded_by.get_full_name()
            or obj.uploaded_by.username
        )

    def get_approved_by_name(self, obj):
        if not obj.approved_by:
            return None

        return (
            obj.approved_by.get_full_name()
            or obj.approved_by.username
        )

    def validate_student(self, student):
        company = get_request_company(
            self.context,
        )
        return validate_student_in_company(
            student,
            company,
        )

    def validate_file(self, file_obj):
        if not file_obj:
            return file_obj

        ext = os.path.splitext(
            file_obj.name,
        )[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                'Unsupported file type. Allowed: '
                'pdf, jpg, jpeg, png, doc, docx.'
            )

        if file_obj.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                'File size must not exceed 10 MB.'
            )

        return file_obj

    def validate(self, attrs):
        file_obj = attrs.get('file')
        is_create = self.instance is None

        if is_create and not file_obj:
            attrs['status'] = 'requested'

        return attrs

    def create(self, validated_data):
        request = self.context['request']
        student = validated_data['student']
        file_obj = validated_data.get('file')

        validated_data['company'] = student.company
        validated_data['uploaded_by'] = request.user

        if file_obj:
            validated_data['status'] = 'uploaded'
            validated_data['original_filename'] = (
                file_obj.name
            )
            validated_data['file_size'] = file_obj.size
            validated_data['mime_type'] = (
                file_obj.content_type or ''
            )
        else:
            validated_data.setdefault(
                'status',
                'requested',
            )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        file_obj = validated_data.get('file')

        if file_obj:
            validated_data['original_filename'] = (
                file_obj.name
            )
            validated_data['file_size'] = file_obj.size
            validated_data['mime_type'] = (
                file_obj.content_type or ''
            )
            validated_data['version'] = instance.version + 1
            validated_data['status'] = 'uploaded'
            validated_data['uploaded_by'] = (
                self.context['request'].user
            )
            validated_data['approved_by'] = None
            validated_data['approved_at'] = None
            validated_data['rejection_remarks'] = ''

        return super().update(instance, validated_data)


class StudentDocumentRequestSerializer(
    serializers.ModelSerializer,
):

    class Meta:
        model = StudentDocument
        fields = (
            'id',
            'student',
            'document_type',
            'document_number',
            'issue_date',
            'expiry_date',
            'notes',
            'status',
        )
        read_only_fields = ('id', 'status')

    def validate_student(self, student):
        company = get_request_company(
            self.context,
        )
        return validate_student_in_company(
            student,
            company,
        )

    def create(self, validated_data):
        request = self.context['request']
        student = validated_data['student']

        return StudentDocument.objects.create(
            company=student.company,
            uploaded_by=request.user,
            status='requested',
            **validated_data,
        )


class StudentDocumentReviewSerializer(
    serializers.Serializer,
):
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    rejection_remarks = serializers.CharField(
        required=False,
        allow_blank=True,
    )

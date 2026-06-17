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
    uploaded_by_name = serializers.SerializerMethodField(
        read_only=True,
    )
    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True,
    )

    class Meta:
        model = StudentDocument
        fields = (
            'id',
            'student',
            'company',
            'document_type',
            'document_type_display',
            'file',
            'file_url',
            'original_filename',
            'file_size',
            'mime_type',
            'notes',
            'uploaded_by',
            'uploaded_by_name',
            'is_deleted',
            'deleted_at',
            'deleted_by',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'company',
            'file_url',
            'original_filename',
            'file_size',
            'mime_type',
            'uploaded_by',
            'uploaded_by_name',
            'document_type_display',
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
                obj.file.url,
            )

        return obj.file.url

    def get_uploaded_by_name(self, obj):
        if not obj.uploaded_by:
            return None

        return (
            obj.uploaded_by.get_full_name()
            or obj.uploaded_by.username
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

    def create(self, validated_data):
        file_obj = validated_data['file']
        request = self.context['request']
        student = validated_data['student']

        validated_data['company'] = student.company
        validated_data['uploaded_by'] = request.user
        validated_data['original_filename'] = (
            file_obj.name
        )
        validated_data['file_size'] = file_obj.size
        validated_data['mime_type'] = (
            file_obj.content_type or ''
        )

        return super().create(validated_data)

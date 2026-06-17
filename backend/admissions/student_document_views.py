import mimetypes

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auditlogs.services import AuditLogService

from accounts.access import filter_students_for_user
from accounts.constants import PERM_DOCUMENTS_RESTORE
from accounts.permissions import (
    ActionPermissionMixin,
    IsCompanyMember,
    crm_permission_map,
    permission_required,
)

from .models import Student, StudentDocument
from .student_document_serializers import (
    StudentDocumentSerializer,
)


class StudentDocumentQuerysetMixin:

    def get_company(self):
        return getattr(
            self.request.user,
            'company',
            None,
        )

    def get_document_queryset(self):
        company = self.get_company()

        if not company:
            return StudentDocument.objects.none()

        allowed_students = filter_students_for_user(
            Student.objects.filter(
                company=company,
                is_deleted=False,
            ),
            self.request.user,
        ).values_list('pk', flat=True)

        queryset = StudentDocument.objects.filter(
            student_id__in=allowed_students,
        ).select_related(
            'student',
            'uploaded_by',
            'company',
        )

        student_id = self.request.query_params.get(
            'student',
        )
        document_type = self.request.query_params.get(
            'document_type',
        )

        if student_id:
            queryset = queryset.filter(
                student_id=student_id,
            )

        if document_type:
            queryset = queryset.filter(
                document_type=document_type,
            )

        return queryset.order_by('-created_at')


class StudentDocumentListCreateAPIView(
    StudentDocumentQuerysetMixin,
    ActionPermissionMixin,
    generics.ListCreateAPIView,
):
    permission_map = crm_permission_map('documents')
    serializer_class = StudentDocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return self.get_document_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        document = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Student Documents',
            action='create',
            object_id=document.id,
            description=(
                f'Uploaded {document.get_document_type_display()} '
                f'for student {document.student.student_id}'
            ),
        )


class StudentDocumentDetailAPIView(
    StudentDocumentQuerysetMixin,
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    permission_map = crm_permission_map('documents')
    serializer_class = StudentDocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return self.get_document_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_update(self, serializer):
        document = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Student Documents',
            action='update',
            object_id=document.id,
            description=(
                f'Updated document #{document.id} '
                f'for student {document.student.student_id}'
            ),
        )

    def perform_destroy(self, instance):
        user = self.request.user
        instance.soft_delete(user)

        AuditLogService.log(
            company=user.company,
            user=user,
            module='Student Documents',
            action='delete',
            object_id=instance.id,
            description=(
                f'Moved document #{instance.id} to trash '
                f'for student {instance.student.student_id}'
            ),
        )


class StudentDocumentDownloadAPIView(
    StudentDocumentQuerysetMixin,
    ActionPermissionMixin,
    APIView,
):
    permission_map = {'GET': 'documents.view'}

    def get(self, request, pk):
        document = get_object_or_404(
            self.get_document_queryset(),
            pk=pk,
        )

        if not document.file:
            raise Http404

        disposition = request.query_params.get(
            'disposition',
            'attachment',
        )

        if disposition not in ('inline', 'attachment'):
            raise ValidationError(
                {'disposition': 'Use inline or attachment.'},
            )

        content_type = (
            document.mime_type
            or mimetypes.guess_type(
                document.original_filename,
            )[0]
            or 'application/octet-stream'
        )

        response = FileResponse(
            document.file.open('rb'),
            content_type=content_type,
            as_attachment=(disposition == 'attachment'),
            filename=document.original_filename,
        )

        return response


class StudentDocumentTrashListAPIView(
    StudentDocumentQuerysetMixin,
    ActionPermissionMixin,
    generics.ListAPIView,
):
    permission_map = {'GET': 'documents.restore'}
    serializer_class = StudentDocumentSerializer

    def get_queryset(self):
        company = self.get_company()

        if not company:
            return StudentDocument.all_objects.none()

        allowed_students = filter_students_for_user(
            Student.all_objects.filter(
                company=company,
                is_deleted=False,
            ),
            self.request.user,
        ).values_list('pk', flat=True)

        return StudentDocument.all_objects.dead().filter(
            student_id__in=allowed_students,
        ).select_related(
            'student',
            'uploaded_by',
        ).order_by('-deleted_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class StudentDocumentRestoreAPIView(
    StudentDocumentQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_DOCUMENTS_RESTORE),
    ]

    def post(self, request, pk):
        company = self.get_company()

        if not company:
            return Response(
                {'detail': 'Company not found.'},
                status=400,
            )

        allowed_students = filter_students_for_user(
            Student.objects.filter(
                company=company,
                is_deleted=False,
            ),
            request.user,
        ).values_list('pk', flat=True)

        document = get_object_or_404(
            StudentDocument.all_objects.dead().filter(
                student_id__in=allowed_students,
            ),
            pk=pk,
        )

        document.restore()

        AuditLogService.log(
            company=company,
            user=request.user,
            module='Student Documents',
            action='restore',
            object_id=document.id,
            description=(
                f'Restored document #{document.id} '
                f'for student {document.student.student_id}'
            ),
        )

        serializer = StudentDocumentSerializer(
            document,
            context={'request': request},
        )

        return Response(serializer.data)

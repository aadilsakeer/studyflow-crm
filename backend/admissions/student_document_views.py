import mimetypes

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
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
    StudentDocumentRequestSerializer,
    StudentDocumentReviewSerializer,
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
            'approved_by',
            'company',
        )

        for param, field in (
            ('student', 'student_id'),
            ('document_type', 'document_type'),
            ('status', 'status'),
            ('category', None),
        ):
            value = self.request.query_params.get(param)

            if not value:
                continue

            if param == 'category':
                types = [
                    key
                    for key, cat in (
                        StudentDocument.CATEGORY_MAP.items()
                    )
                    if cat == value
                ]
                queryset = queryset.filter(
                    document_type__in=types,
                )
            else:
                queryset = queryset.filter(
                    **{field: value},
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


class StudentDocumentRequestAPIView(
    StudentDocumentQuerysetMixin,
    ActionPermissionMixin,
    generics.CreateAPIView,
):
    permission_map = {'POST': 'documents.add'}
    serializer_class = StudentDocumentRequestSerializer

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
            action='request',
            object_id=document.id,
            description=(
                f'Requested {document.get_document_type_display()} '
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


class StudentDocumentFileResponseMixin(
    StudentDocumentQuerysetMixin,
):

    def build_file_response(
        self,
        document,
        as_attachment,
    ):
        if not document.file:
            raise Http404

        content_type = (
            document.mime_type
            or mimetypes.guess_type(
                document.original_filename,
            )[0]
            or 'application/octet-stream'
        )

        return FileResponse(
            document.file.open('rb'),
            content_type=content_type,
            as_attachment=as_attachment,
            filename=document.original_filename,
        )


class StudentDocumentDownloadAPIView(
    StudentDocumentFileResponseMixin,
    ActionPermissionMixin,
    APIView,
):
    permission_map = {'GET': 'documents.view'}

    def get(self, request, pk):
        document = get_object_or_404(
            self.get_document_queryset(),
            pk=pk,
        )

        disposition = request.query_params.get(
            'disposition',
            'attachment',
        )

        if disposition not in ('inline', 'attachment'):
            raise ValidationError(
                {'disposition': 'Use inline or attachment.'},
            )

        return self.build_file_response(
            document,
            disposition == 'attachment',
        )


class StudentDocumentPreviewAPIView(
    StudentDocumentFileResponseMixin,
    ActionPermissionMixin,
    APIView,
):
    permission_map = {'GET': 'documents.view'}

    def get(self, request, pk):
        document = get_object_or_404(
            self.get_document_queryset(),
            pk=pk,
        )

        return self.build_file_response(
            document,
            False,
        )


class StudentDocumentReviewAPIView(
    StudentDocumentQuerysetMixin,
    ActionPermissionMixin,
    APIView,
):
    permission_map = {'POST': 'documents.change'}

    def post(self, request, pk, *args, **kwargs):
        action = kwargs.get('action')
        document = get_object_or_404(
            self.get_document_queryset(),
            pk=pk,
        )

        serializer = StudentDocumentReviewSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if action == 'review':
            document.status = 'under_review'
            if data.get('notes'):
                document.notes = data['notes']
            document.save(
                update_fields=['status', 'notes', 'updated_at'],
            )
            log_action = 'review'
            description = (
                f'Marked document #{document.id} under review'
            )
        elif action == 'approve':
            if not document.file:
                raise ValidationError(
                    {'detail': 'Cannot approve without a file.'},
                )
            document.status = 'approved'
            document.approved_by = request.user
            document.approved_at = timezone.now()
            document.rejection_remarks = ''
            if data.get('notes'):
                document.notes = data['notes']
            document.save()
            log_action = 'approve'
            description = (
                f'Approved {document.get_document_type_display()} '
                f'for student {document.student.student_id}'
            )
        elif action == 'reject':
            document.status = 'rejected'
            document.approved_by = None
            document.approved_at = None
            document.rejection_remarks = data.get(
                'rejection_remarks',
                '',
            )
            if data.get('notes'):
                document.notes = data['notes']
            document.save()
            log_action = 'reject'
            description = (
                f'Rejected {document.get_document_type_display()} '
                f'for student {document.student.student_id}'
            )
        else:
            raise ValidationError(
                {'detail': 'Invalid review action.'},
            )

        AuditLogService.log(
            company=request.user.company,
            user=request.user,
            module='Student Documents',
            action=log_action,
            object_id=document.id,
            description=description,
        )

        return Response(
            StudentDocumentSerializer(
                document,
                context={'request': request},
            ).data,
        )


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
            'approved_by',
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
                status=status.HTTP_400_BAD_REQUEST,
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

        return Response(
            StudentDocumentSerializer(
                document,
                context={'request': request},
            ).data,
        )

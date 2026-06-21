from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.constants import PERM_LEADS_IMPORT
from accounts.models import CustomUser
from accounts.permissions import (
    IsCompanyMember,
    permission_required,
)

from .import_engine import (
    TARGET_FIELDS,
    execute_import,
    parse_upload_file,
    validate_import,
)
from .models import LeadImportLog


class LeadImportHistoryAPIView(ListAPIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_IMPORT),
    ]

    def get_queryset(self):
        company = getattr(
            self.request.user,
            'company',
            None,
        )

        if not company:
            return LeadImportLog.objects.none()

        return LeadImportLog.objects.filter(
            company=company,
        ).select_related(
            'imported_by',
        ).order_by('-created_at')[:50]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        data = [
            {
                'id': item.id,
                'file_name': item.file_name,
                'status': item.status,
                'total_records': item.total_records,
                'imported_records': item.imported_records,
                'duplicate_records': item.duplicate_records,
                'failed_records': item.failed_records,
                'imported_by': (
                    item.imported_by.username
                    if item.imported_by else None
                ),
                'created_at': item.created_at,
                'completed_at': item.completed_at,
            }
            for item in queryset
        ]

        return Response(data)


class LeadImportUploadAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_IMPORT),
    ]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        company = getattr(request.user, 'company', None)

        if not company:
            raise ValidationError({'detail': 'Company not found.'})

        file_obj = request.FILES.get('file')

        if not file_obj:
            raise ValidationError({'file': 'File is required.'})

        try:
            columns, preview_rows, total = parse_upload_file(
                file_obj,
                file_obj.name,
            )
        except ValueError as exc:
            raise ValidationError({'file': str(exc)}) from exc
        except Exception as exc:
            raise ValidationError(
                {'file': f'Failed to parse file: {exc}'},
            ) from exc

        file_obj.seek(0)

        import_log = LeadImportLog.objects.create(
            company=company,
            file_name=file_obj.name,
            stored_file=file_obj,
            imported_by=request.user,
            source_columns=columns,
            preview_rows=preview_rows,
            total_records=total,
            status='uploaded',
        )

        return Response(
            {
                'id': import_log.id,
                'file_name': import_log.file_name,
                'source_columns': columns,
                'preview_rows': preview_rows,
                'total_records': total,
                'target_fields': TARGET_FIELDS,
            },
            status=status.HTTP_201_CREATED,
        )


class LeadImportDetailAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_IMPORT),
    ]

    def _get_log(self, request, pk):
        company = getattr(request.user, 'company', None)

        return get_object_or_404(
            LeadImportLog.objects.filter(company=company),
            pk=pk,
        )

    def get(self, request, pk):
        import_log = self._get_log(request, pk)

        return Response({
            'id': import_log.id,
            'file_name': import_log.file_name,
            'status': import_log.status,
            'source_columns': import_log.source_columns,
            'preview_rows': import_log.preview_rows,
            'column_mapping': import_log.column_mapping,
            'duplicate_rule': import_log.duplicate_rule,
            'assignment_mode': import_log.assignment_mode,
            'total_records': import_log.total_records,
            'imported_records': import_log.imported_records,
            'duplicate_records': import_log.duplicate_records,
            'failed_records': import_log.failed_records,
            'error_report': import_log.error_report,
            'target_fields': TARGET_FIELDS,
        })


class LeadImportMapAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_IMPORT),
    ]

    def post(self, request, pk):
        company = getattr(request.user, 'company', None)
        import_log = get_object_or_404(
            LeadImportLog.objects.filter(company=company),
            pk=pk,
        )

        mapping = request.data.get('column_mapping', {})
        duplicate_rule = request.data.get(
            'duplicate_rule',
            'phone',
        )

        if not mapping.get('first_name') or not mapping.get('phone'):
            raise ValidationError(
                {'column_mapping': 'Map first_name and phone.'},
            )

        if duplicate_rule not in dict(
            LeadImportLog.DUPLICATE_RULE_CHOICES,
        ):
            raise ValidationError(
                {'duplicate_rule': 'Invalid duplicate rule.'},
            )

        import_log.column_mapping = mapping
        import_log.duplicate_rule = duplicate_rule
        import_log.status = 'mapped'
        import_log.save(
            update_fields=[
                'column_mapping',
                'duplicate_rule',
                'status',
            ],
        )

        return Response({
            'id': import_log.id,
            'status': import_log.status,
            'column_mapping': import_log.column_mapping,
            'duplicate_rule': import_log.duplicate_rule,
        })


class LeadImportValidateAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_IMPORT),
    ]

    def post(self, request, pk):
        company = getattr(request.user, 'company', None)
        import_log = get_object_or_404(
            LeadImportLog.objects.filter(company=company),
            pk=pk,
        )

        if import_log.status not in ('mapped', 'validated'):
            raise ValidationError(
                {'detail': 'Complete column mapping first.'},
            )

        result = validate_import(import_log)

        return Response({
            'total_records': result['total_records'],
            'valid_count': result['valid_count'],
            'duplicate_count': result['duplicate_count'],
            'error_count': result['error_count'],
            'errors': result['errors'],
            'duplicate_rows': result['duplicate_rows'],
        })


class LeadImportExecuteAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_IMPORT),
    ]

    def post(self, request, pk):
        company = getattr(request.user, 'company', None)
        import_log = get_object_or_404(
            LeadImportLog.objects.filter(company=company),
            pk=pk,
        )

        assignment_mode = request.data.get(
            'assignment_mode',
            'manual',
        )
        telecaller_id = request.data.get('telecaller_id')

        if assignment_mode not in dict(
            LeadImportLog.ASSIGNMENT_CHOICES,
        ):
            raise ValidationError(
                {'assignment_mode': 'Invalid assignment mode.'},
            )

        import_log.assignment_mode = assignment_mode
        import_log.save(update_fields=['assignment_mode'])

        telecaller = None

        if assignment_mode == 'manual':
            if not telecaller_id:
                raise ValidationError(
                    {'telecaller_id': 'Required for manual assignment.'},
                )

            telecaller = get_object_or_404(
                CustomUser.objects.filter(company=company),
                pk=telecaller_id,
            )

        try:
            summary = execute_import(
                import_log,
                request.user,
                telecaller=telecaller,
            )
        except ValueError as exc:
            import_log.status = 'failed'
            import_log.save(update_fields=['status'])
            raise ValidationError({'detail': str(exc)}) from exc

        return Response(summary)

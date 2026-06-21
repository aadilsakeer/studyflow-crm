import mimetypes

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

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

from activity.timeline_constants import (
    EVENT_OFFER_ACCEPTED,
    EVENT_OFFER_RECEIVED,
)
from activity.timeline_service import record_student_event

from accounts.access import filter_students_for_user
from accounts.constants import PERM_OFFERLETTERS_RESTORE
from accounts.permissions import (
    ActionPermissionMixin,
    IsCompanyMember,
    crm_permission_map,
    permission_required,
)

from .models import OfferLetter, Student
from .offer_letter_serializers import (
    OfferLetterReviewSerializer,
    OfferLetterSerializer,
)


class OfferLetterQuerysetMixin:

    def get_company(self):
        return getattr(
            self.request.user,
            'company',
            None,
        )

    def get_offer_queryset(self):
        company = self.get_company()

        if not company:
            return OfferLetter.objects.none()

        allowed_students = filter_students_for_user(
            Student.objects.filter(
                company=company,
                is_deleted=False,
            ),
            self.request.user,
        ).values_list('pk', flat=True)

        queryset = OfferLetter.objects.filter(
            company=company,
            student_id__in=allowed_students,
        ).select_related(
            'student',
            'application',
            'student_document',
        )

        for param in ('student', 'application', 'status'):
            value = self.request.query_params.get(param)

            if value:
                queryset = queryset.filter(
                    **{param: value},
                )

        return queryset.order_by('-created_at')


class OfferLetterListCreateAPIView(
    OfferLetterQuerysetMixin,
    ActionPermissionMixin,
    generics.ListCreateAPIView,
):
    permission_map = crm_permission_map('offerletters')
    serializer_class = OfferLetterSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return self.get_offer_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        offer = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Offer Letters',
            action='create',
            object_id=offer.id,
            description=(
                f'Created offer {offer.offer_number} '
                f'for {offer.student.student_id}'
            ),
        )

        record_student_event(
            offer.student,
            EVENT_OFFER_RECEIVED,
            description=(
                f'Offer {offer.offer_number} from '
                f'{offer.university}.'
            ),
            user=self.request.user,
        )


class OfferLetterDetailAPIView(
    OfferLetterQuerysetMixin,
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    permission_map = crm_permission_map('offerletters')
    serializer_class = OfferLetterSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return self.get_offer_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_update(self, serializer):
        offer = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Offer Letters',
            action='update',
            object_id=offer.id,
            description=(
                f'Updated offer {offer.offer_number}'
            ),
        )

    def perform_destroy(self, instance):
        user = self.request.user
        instance.soft_delete(user)

        AuditLogService.log(
            company=user.company,
            user=user,
            module='Offer Letters',
            action='delete',
            object_id=instance.id,
            description=(
                f'Moved offer {instance.offer_number} '
                f'to trash'
            ),
        )


class OfferLetterDownloadAPIView(
    OfferLetterQuerysetMixin,
    ActionPermissionMixin,
    APIView,
):
    permission_map = {'GET': 'offerletters.view'}

    def get(self, request, pk):
        offer = get_object_or_404(
            self.get_offer_queryset(),
            pk=pk,
        )

        if not offer.offer_document:
            raise Http404

        content_type = (
            offer.mime_type
            or mimetypes.guess_type(
                offer.original_filename,
            )[0]
            or 'application/octet-stream'
        )

        return FileResponse(
            offer.offer_document.open('rb'),
            content_type=content_type,
            as_attachment=True,
            filename=offer.original_filename,
        )


class OfferLetterWorkflowAPIView(
    OfferLetterQuerysetMixin,
    ActionPermissionMixin,
    APIView,
):
    permission_map = {'POST': 'offerletters.change'}

    def post(self, request, pk, *args, **kwargs):
        action = kwargs.get('action')
        offer = get_object_or_404(
            self.get_offer_queryset(),
            pk=pk,
        )

        serializer = OfferLetterReviewSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if action == 'review':
            offer.status = 'reviewed'
            log_action = 'review'
        elif action == 'accept':
            offer.status = 'accepted'
            log_action = 'accept'
        elif action == 'reject':
            offer.status = 'rejected'
            log_action = 'reject'
        else:
            raise ValidationError(
                {'detail': 'Invalid action.'},
            )

        if data.get('notes'):
            offer.notes = data['notes']

        offer.save()

        AuditLogService.log(
            company=request.user.company,
            user=request.user,
            module='Offer Letters',
            action=log_action,
            object_id=offer.id,
            description=(
                f'{log_action.title()}ed offer '
                f'{offer.offer_number}'
            ),
        )

        if action == 'accept':
            record_student_event(
                offer.student,
                EVENT_OFFER_ACCEPTED,
                description=(
                    f'Offer {offer.offer_number} accepted.'
                ),
                user=request.user,
            )

        return Response(
            OfferLetterSerializer(
                offer,
                context={'request': request},
            ).data,
        )


class OfferLetterTrashListAPIView(
    OfferLetterQuerysetMixin,
    ActionPermissionMixin,
    generics.ListAPIView,
):
    permission_map = {'GET': 'offerletters.restore'}
    serializer_class = OfferLetterSerializer

    def get_queryset(self):
        company = self.get_company()

        if not company:
            return OfferLetter.all_objects.none()

        allowed_students = filter_students_for_user(
            Student.all_objects.filter(
                company=company,
                is_deleted=False,
            ),
            self.request.user,
        ).values_list('pk', flat=True)

        return OfferLetter.all_objects.dead().filter(
            company=company,
            student_id__in=allowed_students,
        ).select_related(
            'student',
            'application',
        ).order_by('-deleted_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class OfferLetterRestoreAPIView(
    OfferLetterQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_OFFERLETTERS_RESTORE),
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

        offer = get_object_or_404(
            OfferLetter.all_objects.dead().filter(
                company=company,
                student_id__in=allowed_students,
            ),
            pk=pk,
        )

        offer.restore()

        AuditLogService.log(
            company=company,
            user=request.user,
            module='Offer Letters',
            action='restore',
            object_id=offer.id,
            description=(
                f'Restored offer {offer.offer_number}'
            ),
        )

        return Response(
            OfferLetterSerializer(
                offer,
                context={'request': request},
            ).data,
        )

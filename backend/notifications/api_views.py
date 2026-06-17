from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from licensing.decorators import module_required
from auditlogs.services import AuditLogService

from accounts.constants import PERM_NOTIFICATIONS_CHANGE
from accounts.permissions import (
    ActionPermissionMixin,
    IsCompanyMember,
    permission_required,
    crm_permission_map,
)

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):
    permission_map = crm_permission_map("notifications")

    serializer_class = NotificationSerializer

    def get_queryset(self):

        return Notification.objects.filter(
            company=self.request.user.company
        ).order_by(
            '-created_at'
        )

    def perform_create(self, serializer):

        notification = serializer.save(
            company=self.request.user.company
        )

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Notifications',
            action='create',
            object_id=notification.id,
            description=(
                f'Created notification '
                f'{notification.title}'
            )
        )

    @module_required('notifications')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('notifications')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NotificationDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    permission_map = crm_permission_map("notifications")

    serializer_class = NotificationSerializer

    def get_queryset(self):

        return Notification.objects.filter(
            company=self.request.user.company
        )

    def perform_update(self, serializer):

        notification = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Notifications',
            action='update',
            object_id=notification.id,
            description=(
                f'Updated notification '
                f'{notification.title}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Notifications',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted notification '
                f'{instance.title}'
            )
        )

        instance.delete()

    @module_required('notifications')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('notifications')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('notifications')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('notifications')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class MarkNotificationReadAPIView(
    APIView
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_NOTIFICATIONS_CHANGE),
    ]

    @module_required('notifications')
    def post(self, request, pk):

        notification = Notification.objects.get(
            pk=pk,
            company=request.user.company
        )

        notification.is_read = True
        notification.save()

        return Response({
            'message': 'Notification marked as read'
        })
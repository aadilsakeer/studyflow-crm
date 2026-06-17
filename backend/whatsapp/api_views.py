from rest_framework import generics

from licensing.decorators import module_required
from auditlogs.services import AuditLogService

from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)

from .models import (
    WhatsAppAccount,
    WhatsAppMessage,
    WhatsAppServer
)

from .serializers import (
    WhatsAppAccountSerializer,
    WhatsAppMessageSerializer,
    WhatsAppServerSerializer
)


class WhatsAppAccountListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):
    permission_map = crm_permission_map("whatsapp")

    serializer_class = WhatsAppAccountSerializer

    def get_queryset(self):

        return WhatsAppAccount.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):

        account = serializer.save(
            company=self.request.user.company
        )

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='WhatsApp',
            action='create',
            object_id=account.id,
            description=(
                f'Created WhatsApp account '
                f'{account.phone_number}'
            )
        )

    @module_required('whatsapp')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('whatsapp')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WhatsAppAccountDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    permission_map = crm_permission_map("whatsapp")

    serializer_class = WhatsAppAccountSerializer

    def get_queryset(self):

        return WhatsAppAccount.objects.filter(
            company=self.request.user.company
        )

    @module_required('whatsapp')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('whatsapp')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('whatsapp')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('whatsapp')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class WhatsAppMessageListAPIView(
    ActionPermissionMixin,
    generics.ListAPIView
):
    permission_map = crm_permission_map("whatsapp")

    serializer_class = WhatsAppMessageSerializer

    def get_queryset(self):

        return WhatsAppMessage.objects.filter(
            company=self.request.user.company
        ).order_by('-created_at')

    @module_required('whatsapp')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class WhatsAppServerAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateAPIView
):
    permission_map = crm_permission_map("whatsapp")

    serializer_class = WhatsAppServerSerializer

    def get_object(self):

        server, created = (
            WhatsAppServer.objects.get_or_create(
                company=self.request.user.company,
                defaults={
                    'base_url': '',
                    'api_key': ''
                }
            )
        )

        return server

    @module_required('whatsapp')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('whatsapp')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('whatsapp')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
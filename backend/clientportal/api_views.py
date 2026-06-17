from rest_framework import generics

from licensing.decorators import module_required
from auditlogs.services import AuditLogService

from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)

from .models import ClientPortalAccess
from .serializers import ClientPortalAccessSerializer
from .services import ClientPortalAuthService


class ClientPortalAccessListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):
    permission_map = crm_permission_map("clientportal")

    serializer_class = ClientPortalAccessSerializer

    def get_queryset(self):

        return ClientPortalAccess.objects.filter(
            student__company=self.request.user.company
        )

    def perform_create(self, serializer):

        portal = serializer.save(
            password=ClientPortalAuthService.hash_password(
                serializer.validated_data['password']
            )
        )

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Client Portal',
            action='create',
            object_id=portal.id,
            description=(
                f'Created portal access '
                f'{portal.username}'
            )
        )

    @module_required('clientportal')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('clientportal')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ClientPortalAccessDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    permission_map = crm_permission_map("clientportal")

    serializer_class = ClientPortalAccessSerializer

    def get_queryset(self):

        return ClientPortalAccess.objects.filter(
            student__company=self.request.user.company
        )

    def perform_update(self, serializer):

        password = serializer.validated_data.get(
            'password'
        )

        if password:

            portal = serializer.save(
                password=ClientPortalAuthService.hash_password(
                    password
                )
            )

        else:

            portal = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Client Portal',
            action='update',
            object_id=portal.id,
            description=(
                f'Updated portal access '
                f'{portal.username}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Client Portal',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted portal access '
                f'{instance.username}'
            )
        )

        instance.delete()

    @module_required('clientportal')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('clientportal')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('clientportal')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('clientportal')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
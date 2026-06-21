from rest_framework import generics
from rest_framework.exceptions import ValidationError

from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)

from auditlogs.helpers import log_audit
from licensing.mixins import LicensedModuleMixin

from .models import (
    Agent,
    AgentCommission
)

from .serializers import (
    AgentSerializer,
    AgentCommissionSerializer
)


def _user_company(request):
    return getattr(request.user, "company", None)


class AgentListCreateAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    generics.ListCreateAPIView,
):
    licensed_module = 'agents'

    permission_map = crm_permission_map("agents")
    serializer_class = AgentSerializer

    def get_queryset(self):
        company = _user_company(self.request)

        if not company:
            return Agent.objects.none()

        return Agent.objects.filter(company=company)

    def perform_create(self, serializer):
        company = _user_company(self.request)

        if not company:
            raise ValidationError(
                {
                    "detail": (
                        "Your account is not linked "
                        "to a company."
                    ),
                },
            )

        agent = serializer.save(company=company)
        log_audit(
            company=company,
            user=self.request.user,
            module='Agents',
            action='create',
            object_id=agent.id,
            description=f"Agent {agent.name} created.",
        )


class AgentDetailAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    licensed_module = 'agents'

    permission_map = crm_permission_map("agents")
    serializer_class = AgentSerializer

    def get_queryset(self):
        company = _user_company(self.request)

        if not company:
            return Agent.objects.none()

        return Agent.objects.filter(company=company)

    def perform_update(self, serializer):
        agent = serializer.save()
        company = _user_company(self.request)
        log_audit(
            company=company,
            user=self.request.user,
            module='Agents',
            action='update',
            object_id=agent.id,
            description=f"Agent {agent.name} updated.",
        )

    def perform_destroy(self, instance):
        company = _user_company(self.request)
        object_id = instance.id
        name = instance.name
        instance.delete()
        log_audit(
            company=company,
            user=self.request.user,
            module='Agents',
            action='delete',
            object_id=object_id,
            description=f"Agent {name} deleted.",
        )


class AgentCommissionListCreateAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    generics.ListCreateAPIView,
):
    licensed_module = 'agents'

    permission_map = crm_permission_map("agents")
    serializer_class = AgentCommissionSerializer

    def get_queryset(self):
        company = _user_company(self.request)

        if not company:
            return AgentCommission.objects.none()

        return AgentCommission.objects.filter(
            agent__company=company,
        )

    def perform_create(self, serializer):
        company = _user_company(self.request)

        if not company:
            raise ValidationError(
                {
                    "detail": (
                        "Your account is not linked "
                        "to a company."
                    ),
                },
            )

        agent = serializer.validated_data.get("agent")

        if agent.company_id != company.pk:
            raise ValidationError(
                {
                    "detail": (
                        "Agent does not belong to "
                        "your company."
                    ),
                },
            )

        serializer.save()


class AgentCommissionDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView,
):

    permission_map = crm_permission_map("agents")
    serializer_class = AgentCommissionSerializer

    def get_queryset(self):
        company = _user_company(self.request)

        if not company:
            return AgentCommission.objects.none()

        return AgentCommission.objects.filter(
            agent__company=company,
        )

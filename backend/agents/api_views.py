from rest_framework import generics
from rest_framework.exceptions import ValidationError

from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)

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
    ActionPermissionMixin,
    generics.ListCreateAPIView,
):

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

        serializer.save(company=company)


class AgentDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView,
):

    permission_map = crm_permission_map("agents")
    serializer_class = AgentSerializer

    def get_queryset(self):
        company = _user_company(self.request)

        if not company:
            return Agent.objects.none()

        return Agent.objects.filter(company=company)


class AgentCommissionListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView,
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

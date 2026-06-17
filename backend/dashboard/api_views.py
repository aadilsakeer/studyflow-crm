from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.constants import PERM_DASHBOARD_VIEW
from accounts.permissions import (
    IsCompanyMember,
    permission_required,
)

from core.mixins import get_user_company

from .services import DashboardService


class DashboardAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_DASHBOARD_VIEW),
    ]

    def get(self, request):
        company = get_user_company(request.user)

        data = DashboardService.get_dashboard_data(
            company
        )

        return Response(data)

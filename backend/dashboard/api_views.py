from rest_framework.views import APIView
from rest_framework.response import Response

from core.mixins import get_user_company

from .services import DashboardService


class DashboardAPIView(APIView):

    def get(self, request):
        company = get_user_company(request.user)

        data = DashboardService.get_dashboard_data(
            company
        )

        return Response(data)
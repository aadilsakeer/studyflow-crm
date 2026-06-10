from rest_framework.views import APIView
from rest_framework.response import Response

from .dashboard_service import DashboardService


class DashboardAPIView(APIView):

    def get(self, request):

        data = DashboardService.get_stats()

        return Response(data)
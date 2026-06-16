from rest_framework.views import APIView
from rest_framework.response import Response

from licensing.decorators import module_required

from .services import DashboardService
from .serializers import DashboardSerializer


class DashboardAPIView(
    APIView
):

    @module_required('dashboard')
    def get(self, request):

        data = DashboardService.get_dashboard_data(
            request.user.company
        )

        serializer = DashboardSerializer(
            data
        )

        return Response(
            serializer.data
        )
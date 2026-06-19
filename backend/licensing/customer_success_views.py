from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .customer_success_service import CustomerSuccessService
from .serializers import CustomerSuccessUpdateSerializer


class OwnerCustomerSuccessDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(CustomerSuccessService.dashboard())


class OwnerCustomerSuccessAlertsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({'alerts': CustomerSuccessService.renewal_alerts()})


class OwnerCustomerSuccessCompanyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, company_id):
        data = CustomerSuccessService.company_detail(company_id)
        if not data:
            raise NotFound()
        return Response(data)

    def patch(self, request, company_id):
        ser = CustomerSuccessUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        data = CustomerSuccessService.update_company(
            company_id, actor=request.user, data=ser.validated_data,
        )
        if not data:
            raise NotFound()
        return Response(data)

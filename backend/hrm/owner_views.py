from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .owner_serializers import (
    AssetAssignSerializer,
    CheckInOutSerializer,
    EmployeeCreateSerializer,
    LeaveApplySerializer,
    LeaveReviewSerializer,
    PayrollCreateSerializer,
    PayrollStatusSerializer,
)
from .owner_service import OwnerHRMService


class OwnerHRMSDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(OwnerHRMService.dashboard())


class OwnerHRMEmployeeListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        company_id = request.query_params.get('company_id')
        return Response({
            'employees': OwnerHRMService.list_employees(
                company_id=int(company_id) if company_id else None,
            ),
        })

    def post(self, request):
        ser = EmployeeCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        emp = OwnerHRMService.create_employee(actor=request.user, data=ser.validated_data)
        if not emp:
            raise NotFound()
        return Response(emp, status=201)


class OwnerHRMEmployeeDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, employee_id):
        data = OwnerHRMService.get_employee(employee_id)
        if not data:
            raise NotFound()
        return Response(data)


class OwnerHRMAttendanceListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        date = request.query_params.get('date')
        return Response({
            'attendance': OwnerHRMService.list_attendance(date=date),
        })


class OwnerHRMAttendanceCheckInAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        ser = CheckInOutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = OwnerHRMService.check_in(
            actor=request.user,
            employee_id=ser.validated_data['employee_id'],
            latitude=ser.validated_data.get('latitude'),
            longitude=ser.validated_data.get('longitude'),
        )
        if not data:
            raise NotFound()
        return Response(data, status=201)


class OwnerHRMAttendanceCheckOutAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        ser = CheckInOutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = OwnerHRMService.check_out(
            actor=request.user,
            employee_id=ser.validated_data['employee_id'],
            latitude=ser.validated_data.get('latitude'),
            longitude=ser.validated_data.get('longitude'),
        )
        if not data:
            raise NotFound()
        return Response(data)


class OwnerHRMLeaveListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({
            'leaves': OwnerHRMService.list_leaves(
                status=request.query_params.get('status'),
            ),
        })

    def post(self, request):
        ser = LeaveApplySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        leave = OwnerHRMService.apply_leave(actor=request.user, data=ser.validated_data)
        if not leave:
            raise NotFound()
        return Response(leave, status=201)


class OwnerHRMLeaveReviewAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, leave_id):
        ser = LeaveReviewSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        leave = OwnerHRMService.review_leave(
            actor=request.user,
            leave_id=leave_id,
            status=ser.validated_data['status'],
            notes=ser.validated_data.get('reviewer_notes', ''),
        )
        if not leave:
            raise NotFound()
        return Response(leave)


class OwnerHRMPayrollListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({'payroll': OwnerHRMService.list_payroll()})

    def post(self, request):
        ser = PayrollCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        payroll = OwnerHRMService.create_payroll(
            actor=request.user, data=ser.validated_data,
        )
        if not payroll:
            raise NotFound()
        return Response(payroll, status=201)


class OwnerHRMPayrollStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, payroll_id):
        ser = PayrollStatusSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        payroll = OwnerHRMService.update_payroll_status(
            actor=request.user,
            payroll_id=payroll_id,
            payment_status=ser.validated_data['payment_status'],
        )
        if not payroll:
            raise NotFound()
        return Response(payroll)


class OwnerHRMAssetListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        employee_id = request.query_params.get('employee_id')
        serial = request.query_params.get('serial_number')
        return Response({
            'assets': OwnerHRMService.list_assets(
                employee_id=int(employee_id) if employee_id else None,
                serial_number=serial,
            ),
        })

    def post(self, request):
        ser = AssetAssignSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        asset = OwnerHRMService.assign_asset(
            actor=request.user, data=ser.validated_data,
        )
        if not asset:
            raise NotFound()
        return Response(asset, status=201)


class OwnerHRMAssetReturnAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, asset_id):
        asset = OwnerHRMService.return_asset(actor=request.user, asset_id=asset_id)
        if not asset:
            raise NotFound()
        return Response(asset)


class OwnerHRMAssetHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        serial = request.query_params.get('serial_number')
        if not serial:
            return Response({'history': []})
        return Response({'history': OwnerHRMService.asset_history(serial_number=serial)})

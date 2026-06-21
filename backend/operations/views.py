from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    EscalateSupportSerializer,
    InternalCommentCreateSerializer,
    InternalTicketCreateSerializer,
    InternalTicketUpdateSerializer,
)
from .service import InternalOperationsService


class OwnerOperationsDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(InternalOperationsService.workload_dashboard())


class OwnerOperationsBoardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(InternalOperationsService.board())


class OwnerInternalTeamAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response({'team': InternalOperationsService.list_team()})


class OwnerInternalTicketListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        assignee = request.query_params.get('assignee_id')
        return Response({
            'tickets': InternalOperationsService.list_tickets(
                status=request.query_params.get('status'),
                ticket_type=request.query_params.get('ticket_type'),
                assignee_id=int(assignee) if assignee else None,
            ),
        })

    def post(self, request):
        ser = InternalTicketCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ticket = InternalOperationsService.create_ticket(
            actor=request.user,
            data=ser.validated_data,
        )
        return Response(ticket, status=201)


class OwnerInternalTicketDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, ticket_id):
        data = InternalOperationsService.get_ticket(ticket_id)
        if not data:
            raise NotFound()
        return Response(data)

    def patch(self, request, ticket_id):
        ser = InternalTicketUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        ticket = InternalOperationsService.assign_ticket(
            ticket_id=ticket_id,
            actor=request.user,
            assignee_id=data.get('assignee_id'),
            status=data.get('status'),
        )
        if not ticket:
            raise NotFound()
        if 'priority' in data or 'due_date' in data:
            from .models import InternalTicket
            obj = InternalTicket.objects.get(pk=ticket_id)
            if 'priority' in data:
                obj.priority = data['priority']
            if 'due_date' in data:
                obj.due_date = data['due_date']
            InternalOperationsService.compute_sla(obj)
            obj.save()
            ticket = InternalOperationsService.get_ticket(ticket_id)
        return Response(ticket)


class OwnerInternalTicketCommentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, ticket_id):
        ser = InternalCommentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        comment = InternalOperationsService.add_comment(
            ticket_id=ticket_id,
            actor=request.user,
            body=ser.validated_data['body'],
        )
        if not comment:
            raise NotFound()
        return Response(comment, status=201)


class OwnerInternalTicketEscalateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        ser = EscalateSupportSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ticket = InternalOperationsService.escalate_support_ticket(
            support_ticket_id=ser.validated_data['support_ticket_id'],
            actor=request.user,
            assignee_id=ser.validated_data.get('assignee_id'),
        )
        if not ticket:
            raise NotFound()
        return Response(ticket, status=201)

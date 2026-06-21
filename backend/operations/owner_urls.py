from django.urls import path

from .views import (
    OwnerInternalTeamAPIView,
    OwnerInternalTicketCommentAPIView,
    OwnerInternalTicketDetailAPIView,
    OwnerInternalTicketEscalateAPIView,
    OwnerInternalTicketListCreateAPIView,
    OwnerOperationsBoardAPIView,
    OwnerOperationsDashboardAPIView,
)

urlpatterns = [
    path('dashboard/', OwnerOperationsDashboardAPIView.as_view()),
    path('board/', OwnerOperationsBoardAPIView.as_view()),
    path('team/', OwnerInternalTeamAPIView.as_view()),
    path('tickets/', OwnerInternalTicketListCreateAPIView.as_view()),
    path('tickets/escalate/', OwnerInternalTicketEscalateAPIView.as_view()),
    path('tickets/<int:ticket_id>/', OwnerInternalTicketDetailAPIView.as_view()),
    path('tickets/<int:ticket_id>/comments/', OwnerInternalTicketCommentAPIView.as_view()),
]

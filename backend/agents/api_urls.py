from django.urls import path

from .api_views import (
    AgentListCreateAPIView,
    AgentDetailAPIView,
    AgentCommissionListCreateAPIView,
    AgentCommissionDetailAPIView,
)

urlpatterns = [

    path(
        '',
        AgentListCreateAPIView.as_view(),
        name='agent-list'
    ),

    path(
        '<int:pk>/',
        AgentDetailAPIView.as_view(),
        name='agent-detail'
    ),

    path(
        'commissions/',
        AgentCommissionListCreateAPIView.as_view(),
        name='agent-commission-list'
    ),

    path(
        'commissions/<int:pk>/',
        AgentCommissionDetailAPIView.as_view(),
        name='agent-commission-detail'
    ),
]
from django.urls import path

from .api_views import (
    CommunicationHistoryAPIView,
    CommunicationNoteListCreateAPIView,
    EmailLogListCreateAPIView,
    WhatsAppLogListCreateAPIView,
)

urlpatterns = [
    path(
        'notes/',
        CommunicationNoteListCreateAPIView.as_view(),
        name='communication-notes',
    ),
    path(
        'emails/',
        EmailLogListCreateAPIView.as_view(),
        name='communication-emails',
    ),
    path(
        'whatsapp-logs/',
        WhatsAppLogListCreateAPIView.as_view(),
        name='communication-whatsapp-logs',
    ),
    path(
        'history/',
        CommunicationHistoryAPIView.as_view(),
        name='communication-history',
    ),
]

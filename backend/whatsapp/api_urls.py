from django.urls import path

from .api_views import (
    WhatsAppAccountListCreateAPIView,
    WhatsAppAccountDetailAPIView,
    WhatsAppMessageListAPIView,
    WhatsAppServerAPIView,
)
from .integration_views import (
    WhatsAppSendAPIView,
    WhatsAppSessionConnectAPIView,
    WhatsAppSessionQRAPIView,
    WhatsAppSessionStatusAPIView,
)

urlpatterns = [

    path(
        'accounts/',
        WhatsAppAccountListCreateAPIView.as_view(),
        name='whatsapp-account-list'
    ),

    path(
        'accounts/<int:pk>/',
        WhatsAppAccountDetailAPIView.as_view(),
        name='whatsapp-account-detail'
    ),

    path(
        'messages/',
        WhatsAppMessageListAPIView.as_view(),
        name='whatsapp-message-list'
    ),
    path(
    'server/',
    WhatsAppServerAPIView.as_view(),
    name='whatsapp-server'
    ),

    path(
        'send/',
        WhatsAppSendAPIView.as_view(),
        name='whatsapp-send',
    ),

    path(
        'session/connect/',
        WhatsAppSessionConnectAPIView.as_view(),
        name='whatsapp-session-connect',
    ),

    path(
        'session/status/',
        WhatsAppSessionStatusAPIView.as_view(),
        name='whatsapp-session-status',
    ),

    path(
        'session/qr/',
        WhatsAppSessionQRAPIView.as_view(),
        name='whatsapp-session-qr',
    ),

]
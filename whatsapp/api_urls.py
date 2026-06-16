from django.urls import path

from .api_views import (
    WhatsAppAccountListCreateAPIView,
    WhatsAppAccountDetailAPIView,
    WhatsAppMessageListAPIView,
    WhatsAppServerAPIView,
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

]
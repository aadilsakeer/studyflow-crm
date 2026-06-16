from django.urls import path

from .api_views import (
    NotificationListCreateAPIView,
    NotificationDetailAPIView,
    MarkNotificationReadAPIView,
)

urlpatterns = [

    path(
        '',
        NotificationListCreateAPIView.as_view(),
        name='notification-list'
    ),

    path(
        '<int:pk>/',
        NotificationDetailAPIView.as_view(),
        name='notification-detail'
    ),

    path(
        '<int:pk>/mark-read/',
        MarkNotificationReadAPIView.as_view(),
        name='notification-mark-read'
    ),

]
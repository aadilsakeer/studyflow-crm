from django.urls import path

from .api_views import (
    AuditLogListAPIView
)

urlpatterns = [

    path(
        '',
        AuditLogListAPIView.as_view(),
        name='audit-log-list'
    ),
]
from django.urls import path

from .api_views import (
    CallLogListAPIView,
    CallLogDetailAPIView,
)

urlpatterns = [
    path(
        "",
        CallLogListAPIView.as_view(),
        name="calllog-list",
    ),
    path(
        "<int:pk>/",
        CallLogDetailAPIView.as_view(),
        name="calllog-detail",
    ),
]

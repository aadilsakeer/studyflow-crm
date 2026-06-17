from django.urls import path

from .api_views import (
    FollowUpListAPIView,
    FollowUpDetailAPIView,
)

urlpatterns = [
    path(
        "",
        FollowUpListAPIView.as_view(),
        name="followup-list",
    ),

    path(
        "<int:pk>/",
        FollowUpDetailAPIView.as_view(),
        name="followup-detail",
    ),
]
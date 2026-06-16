from django.urls import path

from .api_views import (
    LeadListAPIView,
    LeadDetailAPIView,
)

urlpatterns = [
    path(
        "",
        LeadListAPIView.as_view(),
        name="lead-list",
    ),

    path(
        "<int:pk>/",
        LeadDetailAPIView.as_view(),
        name="lead-detail",
    ),
]
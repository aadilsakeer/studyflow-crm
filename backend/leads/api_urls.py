from django.urls import path

from .api_views import (
    LeadListAPIView,
    LeadDetailAPIView,
    LeadTimelineListAPIView,
    LeadAuditLogListAPIView,
    LeadConvertAPIView,
    LeadTrashListAPIView,
    LeadRestoreAPIView,
)

urlpatterns = [
    path(
        "",
        LeadListAPIView.as_view(),
        name="lead-list",
    ),
    path(
        "trash/",
        LeadTrashListAPIView.as_view(),
        name="lead-trash",
    ),
    path(
        "<int:pk>/restore/",
        LeadRestoreAPIView.as_view(),
        name="lead-restore",
    ),
    path(
        "<int:pk>/convert/",
        LeadConvertAPIView.as_view(),
        name="lead-convert",
    ),
    path(
        "<int:pk>/",
        LeadDetailAPIView.as_view(),
        name="lead-detail",
    ),
    path(
        "<int:lead_pk>/timeline/",
        LeadTimelineListAPIView.as_view(),
        name="lead-timeline",
    ),
    path(
        "<int:lead_pk>/audit/",
        LeadAuditLogListAPIView.as_view(),
        name="lead-audit",
    ),
]

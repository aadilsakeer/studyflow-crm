from django.urls import path

from .timeline_views import (
    LeadActivityTimelineAPIView,
    StudentActivityTimelineAPIView,
)

urlpatterns = [
    path(
        'leads/<int:pk>/timeline/',
        LeadActivityTimelineAPIView.as_view(),
        name='activity-lead-timeline',
    ),
    path(
        'students/<int:pk>/timeline/',
        StudentActivityTimelineAPIView.as_view(),
        name='activity-student-timeline',
    ),
]

from django.urls import path

from .api_views import (
    WorkVisaCaseListCreateAPIView,
    WorkVisaCaseDetailAPIView,
    WorkVisaDocumentListCreateAPIView,
    WorkVisaDocumentDetailAPIView,
    WorkVisaTimelineListCreateAPIView,
    WorkVisaTimelineDetailAPIView,
)

urlpatterns = [

    # Cases

    path(
        'cases/',
        WorkVisaCaseListCreateAPIView.as_view(),
        name='workvisa-case-list'
    ),

    path(
        'cases/<int:pk>/',
        WorkVisaCaseDetailAPIView.as_view(),
        name='workvisa-case-detail'
    ),

    # Documents

    path(
        'documents/',
        WorkVisaDocumentListCreateAPIView.as_view(),
        name='workvisa-document-list'
    ),

    path(
        'documents/<int:pk>/',
        WorkVisaDocumentDetailAPIView.as_view(),
        name='workvisa-document-detail'
    ),

    # Timeline

    path(
        'timeline/',
        WorkVisaTimelineListCreateAPIView.as_view(),
        name='workvisa-timeline-list'
    ),

    path(
        'timeline/<int:pk>/',
        WorkVisaTimelineDetailAPIView.as_view(),
        name='workvisa-timeline-detail'
    ),
]
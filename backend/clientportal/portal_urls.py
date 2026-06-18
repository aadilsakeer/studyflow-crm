from django.urls import path

from .portal_views import (
    PortalApplicationsAPIView,
    PortalDocumentUploadAPIView,
    PortalDocumentsAPIView,
    PortalLoginAPIView,
    PortalOffersAPIView,
    PortalProfileAPIView,
    PortalTimelineAPIView,
    PortalVisaCasesAPIView,
)

urlpatterns = [
    path(
        'login/',
        PortalLoginAPIView.as_view(),
        name='portal-login',
    ),
    path(
        'me/',
        PortalProfileAPIView.as_view(),
        name='portal-profile',
    ),
    path(
        'documents/',
        PortalDocumentsAPIView.as_view(),
        name='portal-documents',
    ),
    path(
        'documents/<int:pk>/upload/',
        PortalDocumentUploadAPIView.as_view(),
        name='portal-document-upload',
    ),
    path(
        'applications/',
        PortalApplicationsAPIView.as_view(),
        name='portal-applications',
    ),
    path(
        'offers/',
        PortalOffersAPIView.as_view(),
        name='portal-offers',
    ),
    path(
        'visa-cases/',
        PortalVisaCasesAPIView.as_view(),
        name='portal-visa-cases',
    ),
    path(
        'timeline/',
        PortalTimelineAPIView.as_view(),
        name='portal-timeline',
    ),
]

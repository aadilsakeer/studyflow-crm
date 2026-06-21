from django.urls import path

from .api_views import (
    DashboardAPIView,
    TelecallerDashboardAPIView,
    CounsellorDashboardAPIView,
)

urlpatterns = [

    path(
        'counsellor/',
        CounsellorDashboardAPIView.as_view(),
        name='counsellor-dashboard',
    ),

    path(
        'telecaller/',
        TelecallerDashboardAPIView.as_view(),
        name='telecaller-dashboard',
    ),

    path(
        '',
        DashboardAPIView.as_view(),
        name='dashboard'
    ),

]
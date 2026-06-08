from django.urls import path

from .api_views import (
    StudentListAPIView,
    ApplicationListAPIView,
)

urlpatterns = [
    path(
        'students/',
        StudentListAPIView.as_view(),
        name='student-list'
    ),

    path(
        'applications/',
        ApplicationListAPIView.as_view(),
        name='application-list'
    ),
]
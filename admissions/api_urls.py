from django.urls import path

from .api_views import (
    StudentListCreateAPIView,
    StudentDetailAPIView,
    ApplicationListCreateAPIView,
    ApplicationDetailAPIView,
    UniversityListCreateAPIView,
    UniversityDetailAPIView,
)

urlpatterns = [

    path(
        'students/',
        StudentListCreateAPIView.as_view(),
        name='student-list'
    ),

    path(
        'students/<int:pk>/',
        StudentDetailAPIView.as_view(),
        name='student-detail'
    ),

    path(
        'applications/',
        ApplicationListCreateAPIView.as_view(),
        name='application-list'
    ),

    path(
        'applications/<int:pk>/',
        ApplicationDetailAPIView.as_view(),
        name='application-detail'
    ),

    path(
        'universities/',
        UniversityListCreateAPIView.as_view(),
        name='university-list'
    ),

    path(
        'universities/<int:pk>/',
        UniversityDetailAPIView.as_view(),
        name='university-detail'
    ),

]
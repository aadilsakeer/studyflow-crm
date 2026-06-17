from django.urls import path

from .api_views import (
    EmployerListCreateAPIView,
    EmployerDetailAPIView,
    JobOpeningListCreateAPIView,
    JobOpeningDetailAPIView,
    CandidateListCreateAPIView,
    CandidateDetailAPIView,
    InterviewListCreateAPIView,
    InterviewDetailAPIView,
    DeploymentListCreateAPIView,
    DeploymentDetailAPIView,
)

urlpatterns = [

    # Employers

    path(
        'employers/',
        EmployerListCreateAPIView.as_view(),
        name='employer-list'
    ),

    path(
        'employers/<int:pk>/',
        EmployerDetailAPIView.as_view(),
        name='employer-detail'
    ),

    # Jobs

    path(
        'jobs/',
        JobOpeningListCreateAPIView.as_view(),
        name='job-list'
    ),

    path(
        'jobs/<int:pk>/',
        JobOpeningDetailAPIView.as_view(),
        name='job-detail'
    ),

    # Candidates

    path(
        'candidates/',
        CandidateListCreateAPIView.as_view(),
        name='candidate-list'
    ),

    path(
        'candidates/<int:pk>/',
        CandidateDetailAPIView.as_view(),
        name='candidate-detail'
    ),

    # Interviews

    path(
        'interviews/',
        InterviewListCreateAPIView.as_view(),
        name='interview-list'
    ),

    path(
        'interviews/<int:pk>/',
        InterviewDetailAPIView.as_view(),
        name='interview-detail'
    ),

    # Deployments

    path(
        'deployments/',
        DeploymentListCreateAPIView.as_view(),
        name='deployment-list'
    ),

    path(
        'deployments/<int:pk>/',
        DeploymentDetailAPIView.as_view(),
        name='deployment-detail'
    ),
]
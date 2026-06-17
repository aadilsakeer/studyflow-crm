from django.urls import path

from .api_views import (
    StudentListCreateAPIView,
    StudentDetailAPIView,
    ApplicationListCreateAPIView,
    ApplicationDetailAPIView,
    UniversityListCreateAPIView,
    UniversityDetailAPIView,
    DocumentListCreateAPIView,
    DocumentDetailAPIView,
    VisaCaseListCreateAPIView,
    VisaCaseDetailAPIView,
    CourseListCreateAPIView,
    CourseDetailAPIView,
    OfferLetterListCreateAPIView,
    OfferLetterDetailAPIView,
    SupportTicketListCreateAPIView,
    SupportTicketDetailAPIView,
    TicketCommentListCreateAPIView,
    TicketCommentDetailAPIView,
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

    path(
        'documents/',
        DocumentListCreateAPIView.as_view(),
        name='document-list'
    ),

    path(
        'documents/<int:pk>/',
        DocumentDetailAPIView.as_view(),
        name='document-detail'
    ),

    path(
        'visa-cases/',
        VisaCaseListCreateAPIView.as_view(),
        name='visa-case-list'
    ),

    path(
        'visa-cases/<int:pk>/',
        VisaCaseDetailAPIView.as_view(),
        name='visa-case-detail'
    ),

    path(
        'courses/',
        CourseListCreateAPIView.as_view(),
        name='course-list'
    ),

    path(
        'courses/<int:pk>/',
        CourseDetailAPIView.as_view(),
        name='course-detail'
    ),

    path(
        'offer-letters/',
        OfferLetterListCreateAPIView.as_view(),
        name='offer-letter-list'
    ),

    path(
        'offer-letters/<int:pk>/',
        OfferLetterDetailAPIView.as_view(),
        name='offer-letter-detail'
    ),

    path(
        'support-tickets/',
        SupportTicketListCreateAPIView.as_view(),
        name='support-ticket-list'
    ),

    path(
        'support-tickets/<int:pk>/',
        SupportTicketDetailAPIView.as_view(),
        name='support-ticket-detail'
    ),

    path(
        'ticket-comments/',
        TicketCommentListCreateAPIView.as_view(),
        name='ticket-comment-list'
    ),

    path(
        'ticket-comments/<int:pk>/',
        TicketCommentDetailAPIView.as_view(),
        name='ticket-comment-detail'
    ),

]

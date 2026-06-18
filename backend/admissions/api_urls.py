from django.urls import path

from .api_views import (
    StudentListCreateAPIView,
    StudentDetailAPIView,
    StudentTrashListAPIView,
    StudentRestoreAPIView,
    ApplicationListCreateAPIView,
    ApplicationDetailAPIView,
    ApplicationTrashListAPIView,
    ApplicationRestoreAPIView,
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

from .student_document_views import (
    StudentDocumentListCreateAPIView,
    StudentDocumentRequestAPIView,
    StudentDocumentDetailAPIView,
    StudentDocumentDownloadAPIView,
    StudentDocumentPreviewAPIView,
    StudentDocumentReviewAPIView,
    StudentDocumentTrashListAPIView,
    StudentDocumentRestoreAPIView,
)

urlpatterns = [

    path(
        'students/',
        StudentListCreateAPIView.as_view(),
        name='student-list'
    ),

    path(
        'students/trash/',
        StudentTrashListAPIView.as_view(),
        name='student-trash'
    ),

    path(
        'students/<int:pk>/restore/',
        StudentRestoreAPIView.as_view(),
        name='student-restore'
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
        'applications/trash/',
        ApplicationTrashListAPIView.as_view(),
        name='application-trash'
    ),

    path(
        'applications/<int:pk>/restore/',
        ApplicationRestoreAPIView.as_view(),
        name='application-restore'
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
        'student-documents/request/',
        StudentDocumentRequestAPIView.as_view(),
        name='student-document-request',
    ),

    path(
        'student-documents/trash/',
        StudentDocumentTrashListAPIView.as_view(),
        name='student-document-trash',
    ),

    path(
        'student-documents/<int:pk>/restore/',
        StudentDocumentRestoreAPIView.as_view(),
        name='student-document-restore',
    ),

    path(
        'student-documents/<int:pk>/download/',
        StudentDocumentDownloadAPIView.as_view(),
        name='student-document-download',
    ),

    path(
        'student-documents/<int:pk>/preview/',
        StudentDocumentPreviewAPIView.as_view(),
        name='student-document-preview',
    ),

    path(
        'student-documents/<int:pk>/review/',
        StudentDocumentReviewAPIView.as_view(),
        kwargs={'action': 'review'},
        name='student-document-review',
    ),

    path(
        'student-documents/<int:pk>/approve/',
        StudentDocumentReviewAPIView.as_view(),
        kwargs={'action': 'approve'},
        name='student-document-approve',
    ),

    path(
        'student-documents/<int:pk>/reject/',
        StudentDocumentReviewAPIView.as_view(),
        kwargs={'action': 'reject'},
        name='student-document-reject',
    ),

    path(
        'student-documents/<int:pk>/',
        StudentDocumentDetailAPIView.as_view(),
        name='student-document-detail',
    ),

    path(
        'student-documents/',
        StudentDocumentListCreateAPIView.as_view(),
        name='student-document-list',
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

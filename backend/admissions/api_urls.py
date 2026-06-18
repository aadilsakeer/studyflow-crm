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
    CourseListCreateAPIView,
    CourseDetailAPIView,
    SupportTicketListCreateAPIView,
    SupportTicketDetailAPIView,
    TicketCommentListCreateAPIView,
    TicketCommentDetailAPIView,
)

from .offer_letter_views import (
    OfferLetterListCreateAPIView,
    OfferLetterDetailAPIView,
    OfferLetterDownloadAPIView,
    OfferLetterWorkflowAPIView,
    OfferLetterTrashListAPIView,
    OfferLetterRestoreAPIView,
)

from .visa_case_views import (
    VisaCaseListCreateAPIView,
    VisaCaseDetailAPIView,
    VisaCaseWorkflowAPIView,
    VisaCaseTrashListAPIView,
    VisaCaseRestoreAPIView,
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
        'visa-cases/trash/',
        VisaCaseTrashListAPIView.as_view(),
        name='visa-case-trash',
    ),

    path(
        'visa-cases/<int:pk>/restore/',
        VisaCaseRestoreAPIView.as_view(),
        name='visa-case-restore',
    ),

    path(
        'visa-cases/<int:pk>/submit/',
        VisaCaseWorkflowAPIView.as_view(),
        kwargs={'action': 'submit'},
        name='visa-case-submit',
    ),

    path(
        'visa-cases/<int:pk>/process/',
        VisaCaseWorkflowAPIView.as_view(),
        kwargs={'action': 'process'},
        name='visa-case-process',
    ),

    path(
        'visa-cases/<int:pk>/approve/',
        VisaCaseWorkflowAPIView.as_view(),
        kwargs={'action': 'approve'},
        name='visa-case-approve',
    ),

    path(
        'visa-cases/<int:pk>/reject/',
        VisaCaseWorkflowAPIView.as_view(),
        kwargs={'action': 'reject'},
        name='visa-case-reject',
    ),

    path(
        'visa-cases/<int:pk>/',
        VisaCaseDetailAPIView.as_view(),
        name='visa-case-detail',
    ),

    path(
        'visa-cases/',
        VisaCaseListCreateAPIView.as_view(),
        name='visa-case-list',
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
        'offer-letters/trash/',
        OfferLetterTrashListAPIView.as_view(),
        name='offer-letter-trash',
    ),

    path(
        'offer-letters/<int:pk>/restore/',
        OfferLetterRestoreAPIView.as_view(),
        name='offer-letter-restore',
    ),

    path(
        'offer-letters/<int:pk>/download/',
        OfferLetterDownloadAPIView.as_view(),
        name='offer-letter-download',
    ),

    path(
        'offer-letters/<int:pk>/review/',
        OfferLetterWorkflowAPIView.as_view(),
        kwargs={'action': 'review'},
        name='offer-letter-review',
    ),

    path(
        'offer-letters/<int:pk>/accept/',
        OfferLetterWorkflowAPIView.as_view(),
        kwargs={'action': 'accept'},
        name='offer-letter-accept',
    ),

    path(
        'offer-letters/<int:pk>/reject/',
        OfferLetterWorkflowAPIView.as_view(),
        kwargs={'action': 'reject'},
        name='offer-letter-reject',
    ),

    path(
        'offer-letters/<int:pk>/',
        OfferLetterDetailAPIView.as_view(),
        name='offer-letter-detail',
    ),

    path(
        'offer-letters/',
        OfferLetterListCreateAPIView.as_view(),
        name='offer-letter-list',
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

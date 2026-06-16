from rest_framework import generics

from licensing.decorators import module_required
from auditlogs.services import AuditLogService

from .models import (
    Student,
    Application,
    Document,
    VisaCase,
    University,
    Course,
    OfferLetter,
    SupportTicket,
    TicketComment
)

from .serializers import (
    StudentSerializer,
    ApplicationSerializer,
    DocumentSerializer,
    VisaCaseSerializer,
    UniversitySerializer,
    CourseSerializer,
    OfferLetterSerializer,
    SupportTicketSerializer,
    TicketCommentSerializer
)


# Student

class StudentListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = StudentSerializer

    def get_queryset(self):

        return Student.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):

        student = serializer.save(
            company=self.request.user.company
        )

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='create',
            object_id=student.id,
            description=(
                f'Created student '
                f'{student.student_id}'
            )
        )

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('admissions')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class StudentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = StudentSerializer

    def get_queryset(self):

        return Student.objects.filter(
            company=self.request.user.company
        )

    def perform_update(self, serializer):

        student = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='update',
            object_id=student.id,
            description=(
                f'Updated student '
                f'{student.student_id}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted student '
                f'{instance.student_id}'
            )
        )

        instance.delete()

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('admissions')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('admissions')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('admissions')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# Application

class ApplicationListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = ApplicationSerializer

    def get_queryset(self):

        return Application.objects.filter(
            student__company=self.request.user.company
        )

    def perform_create(self, serializer):

        application = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='create',
            object_id=application.id,
            description=(
                f'Created application '
                f'{application.id}'
            )
        )

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('admissions')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ApplicationDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = ApplicationSerializer

    def get_queryset(self):

        return Application.objects.filter(
            student__company=self.request.user.company
        )

    def perform_update(self, serializer):

        application = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='update',
            object_id=application.id,
            description=(
                f'Updated application '
                f'{application.id}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted application '
                f'{instance.id}'
            )
        )

        instance.delete()

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('admissions')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('admissions')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('admissions')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# University

class UniversityListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = UniversitySerializer

    def get_queryset(self):

        return University.objects.all()

    def perform_create(self, serializer):

        university = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='create',
            object_id=university.id,
            description=(
                f'Created university '
                f'{university.name}'
            )
        )

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('admissions')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class UniversityDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = UniversitySerializer

    queryset = University.objects.all()

    def perform_update(self, serializer):

        university = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='update',
            object_id=university.id,
            description=(
                f'Updated university '
                f'{university.name}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted university '
                f'{instance.name}'
            )
        )

        instance.delete()

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('admissions')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('admissions')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('admissions')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    

# Document

class DocumentListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = DocumentSerializer

    def get_queryset(self):

        return Document.objects.filter(
            application__student__company=self.request.user.company
        )

    def perform_create(self, serializer):

        document = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='create',
            object_id=document.id,
            description=(
                f'Created document '
                f'{document.id}'
            )
        )

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('admissions')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class DocumentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = DocumentSerializer

    def get_queryset(self):

        return Document.objects.filter(
            application__student__company=self.request.user.company
        )

    def perform_update(self, serializer):

        document = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='update',
            object_id=document.id,
            description=(
                f'Updated document '
                f'{document.id}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted document '
                f'{instance.id}'
            )
        )

        instance.delete()

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('admissions')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('admissions')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('admissions')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Visa Case

class VisaCaseListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = VisaCaseSerializer

    def get_queryset(self):

        return VisaCase.objects.filter(
            application__student__company=self.request.user.company
        )

    def perform_create(self, serializer):

        visa_case = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='create',
            object_id=visa_case.id,
            description=(
                f'Created visa case '
                f'{visa_case.id}'
            )
        )

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('admissions')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class VisaCaseDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = VisaCaseSerializer

    def get_queryset(self):

        return VisaCase.objects.filter(
            application__student__company=self.request.user.company
        )

    def perform_update(self, serializer):

        visa_case = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='update',
            object_id=visa_case.id,
            description=(
                f'Updated visa case '
                f'{visa_case.id}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted visa case '
                f'{instance.id}'
            )
        )

        instance.delete()

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('admissions')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('admissions')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('admissions')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Course

class CourseListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = CourseSerializer

    queryset = Course.objects.all()

    def perform_create(self, serializer):

        course = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='create',
            object_id=course.id,
            description=(
                f'Created course '
                f'{course.name}'
            )
        )

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('admissions')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    

class CourseDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = CourseSerializer

    queryset = Course.objects.all()

    def perform_update(self, serializer):

        course = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='update',
            object_id=course.id,
            description=(
                f'Updated course '
                f'{course.name}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted course '
                f'{instance.name}'
            )
        )

        instance.delete()

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('admissions')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('admissions')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('admissions')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Offer Letter

class OfferLetterListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = OfferLetterSerializer

    def get_queryset(self):

        return OfferLetter.objects.filter(
            application__student__company=self.request.user.company
        )

    def perform_create(self, serializer):

        offer_letter = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='create',
            object_id=offer_letter.id,
            description=(
                f'Created offer letter '
                f'{offer_letter.id}'
            )
        )

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('admissions')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    

class OfferLetterDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = OfferLetterSerializer

    def get_queryset(self):

        return OfferLetter.objects.filter(
            application__student__company=self.request.user.company
        )

    def perform_update(self, serializer):

        offer_letter = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='update',
            object_id=offer_letter.id,
            description=(
                f'Updated offer letter '
                f'{offer_letter.id}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted offer letter '
                f'{instance.id}'
            )
        )

        instance.delete()

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('admissions')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('admissions')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('admissions')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class SupportTicketListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = SupportTicketSerializer

    def get_queryset(self):

        return SupportTicket.objects.filter(
            student__company=self.request.user.company
        )

    def perform_create(self, serializer):

        ticket = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='create',
            object_id=ticket.id,
            description=(
                f'Created support ticket '
                f'{ticket.id}'
            )
        )

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('admissions')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class SupportTicketDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = SupportTicketSerializer

    def get_queryset(self):

        return SupportTicket.objects.filter(
            student__company=self.request.user.company
        )

    def perform_update(self, serializer):

        ticket = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='update',
            object_id=ticket.id,
            description=(
                f'Updated support ticket '
                f'{ticket.id}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted support ticket '
                f'{instance.id}'
            )
        )

        instance.delete()

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('admissions')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('admissions')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('admissions')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Ticket Comment

class TicketCommentListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = TicketCommentSerializer

    def get_queryset(self):

        return TicketComment.objects.filter(
            ticket__student__company=self.request.user.company
        )

    def perform_create(self, serializer):

        comment = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='create',
            object_id=comment.id,
            description=(
                f'Created ticket comment '
                f'{comment.id}'
            )
        )

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('admissions')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    

class TicketCommentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = TicketCommentSerializer

    def get_queryset(self):

        return TicketComment.objects.filter(
            ticket__student__company=self.request.user.company
        )

    def perform_update(self, serializer):

        comment = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='update',
            object_id=comment.id,
            description=(
                f'Updated ticket comment '
                f'{comment.id}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Admissions',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted ticket comment '
                f'{instance.id}'
            )
        )

        instance.delete()

    @module_required('admissions')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('admissions')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('admissions')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('admissions')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
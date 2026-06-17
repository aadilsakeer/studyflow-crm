from django.db.models import Q

from rest_framework import generics

from auditlogs.services import AuditLogService

from accounts.access import filter_students_for_user
from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)

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
    ActionPermissionMixin,
    generics.ListCreateAPIView
):

    permission_map = crm_permission_map("students")

    serializer_class = StudentSerializer

    def get_queryset(self):
        company = self.request.user.company
        queryset = Student.objects.filter(
            company=company,
        )
        return filter_students_for_user(
            queryset,
            self.request.user,
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




class StudentDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):

    permission_map = crm_permission_map("students")

    serializer_class = StudentSerializer

    def get_queryset(self):
        company = self.request.user.company
        queryset = Student.objects.filter(
            company=company,
        )
        return filter_students_for_user(
            queryset,
            self.request.user,
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






# Application

class ApplicationListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):

    permission_map = crm_permission_map("applications")

    serializer_class = ApplicationSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        queryset = Application.objects.filter(
            student__company=(
                self.request.user.company
            )
        )

        student_id = self.request.query_params.get(
            "student",
        )
        status = self.request.query_params.get(
            "status",
        )
        search = self.request.query_params.get(
            "search",
        )

        if student_id:
            queryset = queryset.filter(
                student_id=student_id,
            )

        if status:
            queryset = queryset.filter(
                application_status=status,
            )

        if search:
            queryset = queryset.filter(
                Q(
                    university_name__icontains=search,
                )
                | Q(
                    course_name__icontains=search,
                )
                | Q(
                    student__student_id__icontains=search,
                )
                | Q(
                    student__lead__first_name__icontains=search,
                )
                | Q(
                    student__lead__last_name__icontains=search,
                )
            )

        return queryset.order_by("-created_at")

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




class ApplicationDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):

    permission_map = crm_permission_map("applications")

    serializer_class = ApplicationSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

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





# University

class UniversityListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):

    permission_map = crm_permission_map("universities")

    serializer_class = UniversitySerializer

    def get_queryset(self):
        queryset = University.objects.filter(
            is_active=True,
        )

        country = self.request.query_params.get(
            "country",
        )
        search = self.request.query_params.get(
            "search",
        )

        if country:
            queryset = queryset.filter(
                country__iexact=country,
            )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(city__icontains=search)
            )

        return queryset.order_by("name")

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



class UniversityDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):

    permission_map = crm_permission_map("universities")

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




    

# Document

class DocumentListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):

    permission_map = crm_permission_map("documents")

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



class DocumentDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):

    permission_map = crm_permission_map("documents")

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





# Visa Case

class VisaCaseListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):

    permission_map = crm_permission_map("documents")

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




class VisaCaseDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):

    permission_map = crm_permission_map("documents")

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





# Course

class CourseListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):

    permission_map = crm_permission_map("universities")

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


    

class CourseDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):

    permission_map = crm_permission_map("universities")

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





# Offer Letter

class OfferLetterListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):

    permission_map = crm_permission_map("applications")

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


    

class OfferLetterDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):

    permission_map = crm_permission_map("applications")

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




    
class SupportTicketListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):

    permission_map = crm_permission_map("applications")

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



class SupportTicketDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):

    permission_map = crm_permission_map("applications")

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





# Ticket Comment

class TicketCommentListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):

    permission_map = crm_permission_map("applications")

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


    

class TicketCommentDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):

    permission_map = crm_permission_map("applications")

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

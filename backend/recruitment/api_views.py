from rest_framework import generics

from licensing.decorators import module_required
from auditlogs.services import AuditLogService

from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)

from .models import (
    Employer,
    JobOpening,
    Candidate,
    Interview,
    Deployment
)

from .serializers import (
    EmployerSerializer,
    JobOpeningSerializer,
    CandidateSerializer,
    InterviewSerializer,
    DeploymentSerializer
)


# Employer

class EmployerListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):
    permission_map = crm_permission_map("recruitment")

    serializer_class = EmployerSerializer

    def get_queryset(self):
        return Employer.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):
        serializer.save(
            company=self.request.user.company
        )
        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='recruitment',
            action='create',
            object_id=serializer.instance.id,
            description=f'Employer created: {serializer.instance.name}'
        )

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('recruitment')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class EmployerDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    permission_map = crm_permission_map("recruitment")

    serializer_class = EmployerSerializer

    def get_queryset(self):
        return Employer.objects.filter(
            company=self.request.user.company
        )

    def perform_update(self, serializer):

        employer = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='update',
            object_id=employer.id,
            description=(
                f'Updated employer '
                f'{employer.name}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted employer '
                f'{instance.name}'
            )
        )

        instance.delete()

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('recruitment')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('recruitment')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('recruitment')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Job Opening
class JobOpeningListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):
    permission_map = crm_permission_map("recruitment")

    serializer_class = JobOpeningSerializer

    def get_queryset(self):
        return JobOpening.objects.filter(
            employer__company=self.request.user.company
        )

    def perform_create(self, serializer):

        job = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='create',
            object_id=job.id,
            description=(
                f'Created job opening '
                f'{job.title}'
            )
        )

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('recruitment')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class JobOpeningDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    permission_map = crm_permission_map("recruitment")

    serializer_class = JobOpeningSerializer

    def get_queryset(self):
        return JobOpening.objects.filter(
            employer__company=self.request.user.company
        )

    def perform_update(self, serializer):

        job = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='update',
            object_id=job.id,
            description=(
                f'Updated job opening '
                f'{job.title}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted job opening '
                f'{instance.title}'
            )
        )

        instance.delete()

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('recruitment')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('recruitment')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('recruitment')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
# Candidate

class CandidateListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):
    permission_map = crm_permission_map("recruitment")

    serializer_class = CandidateSerializer

    def get_queryset(self):
        return Candidate.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):

        candidate = serializer.save(
            company=self.request.user.company
        )

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='create',
            object_id=candidate.id,
            description=(
                f'Created candidate '
                f'{candidate.full_name}'
            )
        )

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('recruitment')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CandidateDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    permission_map = crm_permission_map("recruitment")

    serializer_class = CandidateSerializer

    def get_queryset(self):
        return Candidate.objects.filter(
            company=self.request.user.company
        )

    def perform_update(self, serializer):

        candidate = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='update',
            object_id=candidate.id,
            description=(
                f'Updated candidate '
                f'{candidate.full_name}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted candidate '
                f'{instance.full_name}'
            )
        )

        instance.delete()

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('recruitment')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('recruitment')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('recruitment')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Interview
class InterviewListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):
    permission_map = crm_permission_map("recruitment")

    serializer_class = InterviewSerializer

    def get_queryset(self):
        return Interview.objects.filter(
            candidate__company=self.request.user.company
        )

    def perform_create(self, serializer):

        interview = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='create',
            object_id=interview.id,
            description=(
                f'Created interview for '
                f'{interview.candidate.full_name}'
            )
        )

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('recruitment')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
class InterviewDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    permission_map = crm_permission_map("recruitment")

    serializer_class = InterviewSerializer

    def get_queryset(self):
        return Interview.objects.filter(
            candidate__company=self.request.user.company
        )

    def perform_update(self, serializer):

        interview = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='update',
            object_id=interview.id,
            description=(
                f'Updated interview for '
                f'{interview.candidate.full_name}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted interview for '
                f'{instance.candidate.full_name}'
            )
        )

        instance.delete()

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('recruitment')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('recruitment')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('recruitment')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Deployment

class DeploymentListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView
):
    permission_map = crm_permission_map("recruitment")

    serializer_class = DeploymentSerializer

    def get_queryset(self):
        return Deployment.objects.filter(
            candidate__company=self.request.user.company
        )

    def perform_create(self, serializer):

        deployment = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='create',
            object_id=deployment.id,
            description=(
                f'Deployed candidate '
                f'{deployment.candidate.full_name}'
            )
        )

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('recruitment')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DeploymentDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView
):
    permission_map = crm_permission_map("recruitment")

    serializer_class = DeploymentSerializer

    def get_queryset(self):
        return Deployment.objects.filter(
            candidate__company=self.request.user.company
        )

    def perform_update(self, serializer):

        deployment = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='update',
            object_id=deployment.id,
            description=(
                f'Updated deployment for '
                f'{deployment.candidate.full_name}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Recruitment',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted deployment for '
                f'{instance.candidate.full_name}'
            )
        )

        instance.delete()

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('recruitment')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('recruitment')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('recruitment')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
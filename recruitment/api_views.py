from rest_framework import generics

from licensing.decorators import module_required
from auditlogs.services import AuditLogService

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
    generics.ListCreateAPIView
):

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
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = EmployerSerializer

    def get_queryset(self):
        return Employer.objects.filter(
            company=self.request.user.company
        )

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
    generics.ListCreateAPIView
):

    serializer_class = JobOpeningSerializer

    def get_queryset(self):
        return JobOpening.objects.filter(
            employer__company=self.request.user.company
        )

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('recruitment')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class JobOpeningDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = JobOpeningSerializer

    def get_queryset(self):
        return JobOpening.objects.filter(
            employer__company=self.request.user.company
        )

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
    generics.ListCreateAPIView
):

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
    generics.RetrieveUpdateDestroyAPIView
):

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
    generics.ListCreateAPIView
):

    serializer_class = InterviewSerializer

    def get_queryset(self):
        return Interview.objects.filter(
            candidate__company=self.request.user.company
        )

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('recruitment')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class InterviewDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = InterviewSerializer

    def get_queryset(self):
        return Interview.objects.filter(
            candidate__company=self.request.user.company
        )

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
    generics.ListCreateAPIView
):

    serializer_class = DeploymentSerializer

    def get_queryset(self):
        return Deployment.objects.filter(
            candidate__company=self.request.user.company
        )

    @module_required('recruitment')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('recruitment')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DeploymentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = DeploymentSerializer

    def get_queryset(self):
        return Deployment.objects.filter(
            candidate__company=self.request.user.company
        )

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
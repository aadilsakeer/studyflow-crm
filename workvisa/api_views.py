from rest_framework import generics

from licensing.decorators import module_required

from .models import (
    WorkVisaCase,
    WorkVisaDocument,
    WorkVisaTimeline
)

from .serializers import (
    WorkVisaCaseSerializer,
    WorkVisaDocumentSerializer,
    WorkVisaTimelineSerializer
)


# Work Visa Cases

class WorkVisaCaseListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = WorkVisaCaseSerializer

    def get_queryset(self):

        return WorkVisaCase.objects.filter(
            company=self.request.user.company
        )

    def perform_create(
        self,
        serializer
    ):

        serializer.save(
            company=self.request.user.company
        )

    @module_required('workvisa')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('workvisa')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WorkVisaCaseDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = WorkVisaCaseSerializer

    def get_queryset(self):

        return WorkVisaCase.objects.filter(
            company=self.request.user.company
        )

    @module_required('workvisa')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('workvisa')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('workvisa')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('workvisa')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# Documents

class WorkVisaDocumentListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = WorkVisaDocumentSerializer

    def get_queryset(self):

        return WorkVisaDocument.objects.filter(
            visa_case__company=self.request.user.company
        )

    @module_required('workvisa')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('workvisa')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WorkVisaDocumentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = WorkVisaDocumentSerializer

    def get_queryset(self):

        return WorkVisaDocument.objects.filter(
            visa_case__company=self.request.user.company
        )

    @module_required('workvisa')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('workvisa')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('workvisa')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('workvisa')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# Timeline

class WorkVisaTimelineListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = WorkVisaTimelineSerializer

    def get_queryset(self):

        return WorkVisaTimeline.objects.filter(
            visa_case__company=self.request.user.company
        )

    @module_required('workvisa')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('workvisa')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WorkVisaTimelineDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = WorkVisaTimelineSerializer

    def get_queryset(self):

        return WorkVisaTimeline.objects.filter(
            visa_case__company=self.request.user.company
        )

    @module_required('workvisa')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('workvisa')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('workvisa')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('workvisa')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
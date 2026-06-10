from rest_framework import generics
from licensing.decorators import module_required

from .models import (
    PartnerUniversity,
    PartnerContact,
    PartnerAgreement,
    PartnerCommission
)

from .serializers import (
    PartnerUniversitySerializer,
    PartnerContactSerializer,
    PartnerAgreementSerializer,
    PartnerCommissionSerializer
)


# Universities

class PartnerUniversityListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = PartnerUniversitySerializer

    def get_queryset(self):

        return PartnerUniversity.objects.filter(
            company=self.request.user.company
        )

    def perform_create(
        self,
        serializer
    ):

        serializer.save(
            company=self.request.user.company
        )
@module_required('partners')
def get(self, request, *args, **kwargs):
    return self.list(request, *args, **kwargs)


@module_required('partners')
def post(self, request, *args, **kwargs):
    return self.create(request, *args, **kwargs)


class PartnerUniversityDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = PartnerUniversitySerializer

    def get_queryset(self):

        return PartnerUniversity.objects.filter(
            company=self.request.user.company
        )
    @module_required('partners')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('partners')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('partners')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('partners')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Contacts

class PartnerContactListCreateAPIView(
    generics.ListCreateAPIView
):

    queryset = PartnerContact.objects.all()
    serializer_class = PartnerContactSerializer

    @module_required('partners')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('partners')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PartnerContactDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = PartnerContact.objects.all()
    serializer_class = PartnerContactSerializer

    @module_required('partners')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('partners')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('partners')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('partners')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# Agreements

class PartnerAgreementListCreateAPIView(
    generics.ListCreateAPIView
):

    queryset = PartnerAgreement.objects.all()
    serializer_class = PartnerAgreementSerializer

    @module_required('partners')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('partners')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class PartnerAgreementDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = PartnerAgreement.objects.all()
    serializer_class = PartnerAgreementSerializer

    @module_required('partners')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('partners')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('partners')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('partners')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
# Commissions

class PartnerCommissionListCreateAPIView(
    generics.ListCreateAPIView
):

    queryset = PartnerCommission.objects.all()
    serializer_class = PartnerCommissionSerializer

    @module_required('partners')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('partners')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
class PartnerCommissionDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = PartnerCommission.objects.all()
    serializer_class = PartnerCommissionSerializer

    @module_required('partners')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('partners')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('partners')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('partners')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)

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


def _user_company(request):
    return getattr(request.user, "company", None)


def _partner_queryset(model, company):
    if not company:
        return model.objects.none()

    return model.objects.filter(
        university__company=company,
    )


def _validate_partner_university(university, company):
    if university.company_id != company.pk:
        raise ValidationError(
            {
                "detail": (
                    "University does not belong to "
                    "your company."
                ),
            },
        )


class PartnerUniversityListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView,
):

    permission_map = crm_permission_map("partners")
    serializer_class = PartnerUniversitySerializer

    def get_queryset(self):
        company = _user_company(self.request)

        if not company:
            return PartnerUniversity.objects.none()

        return PartnerUniversity.objects.filter(
            company=company,
        )

    def perform_create(self, serializer):
        company = _user_company(self.request)

        if not company:
            raise ValidationError(
                {
                    "detail": (
                        "Your account is not linked "
                        "to a company."
                    ),
                },
            )

        serializer.save(company=company)


class PartnerUniversityDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView,
):

    permission_map = crm_permission_map("partners")
    serializer_class = PartnerUniversitySerializer

    def get_queryset(self):
        company = _user_company(self.request)

        if not company:
            return PartnerUniversity.objects.none()

        return PartnerUniversity.objects.filter(
            company=company,
        )


class PartnerContactListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView,
):

    permission_map = crm_permission_map("partners")
    serializer_class = PartnerContactSerializer

    def get_queryset(self):
        return _partner_queryset(
            PartnerContact,
            _user_company(self.request),
        )

    def perform_create(self, serializer):
        company = _user_company(self.request)

        if not company:
            raise ValidationError(
                {
                    "detail": (
                        "Your account is not linked "
                        "to a company."
                    ),
                },
            )

        university = serializer.validated_data["university"]
        _validate_partner_university(university, company)
        serializer.save()


class PartnerContactDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView,
):

    permission_map = crm_permission_map("partners")
    serializer_class = PartnerContactSerializer

    def get_queryset(self):
        return _partner_queryset(
            PartnerContact,
            _user_company(self.request),
        )


class PartnerAgreementListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView,
):

    permission_map = crm_permission_map("partners")
    serializer_class = PartnerAgreementSerializer

    def get_queryset(self):
        return _partner_queryset(
            PartnerAgreement,
            _user_company(self.request),
        )

    def perform_create(self, serializer):
        company = _user_company(self.request)

        if not company:
            raise ValidationError(
                {
                    "detail": (
                        "Your account is not linked "
                        "to a company."
                    ),
                },
            )

        university = serializer.validated_data["university"]
        _validate_partner_university(university, company)
        serializer.save()


class PartnerAgreementDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView,
):

    permission_map = crm_permission_map("partners")
    serializer_class = PartnerAgreementSerializer

    def get_queryset(self):
        return _partner_queryset(
            PartnerAgreement,
            _user_company(self.request),
        )


class PartnerCommissionListCreateAPIView(
    ActionPermissionMixin,
    generics.ListCreateAPIView,
):

    permission_map = crm_permission_map("partners")
    serializer_class = PartnerCommissionSerializer

    def get_queryset(self):
        return _partner_queryset(
            PartnerCommission,
            _user_company(self.request),
        )

    def perform_create(self, serializer):
        company = _user_company(self.request)

        if not company:
            raise ValidationError(
                {
                    "detail": (
                        "Your account is not linked "
                        "to a company."
                    ),
                },
            )

        university = serializer.validated_data["university"]
        _validate_partner_university(university, company)
        serializer.save()


class PartnerCommissionDetailAPIView(
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView,
):

    permission_map = crm_permission_map("partners")
    serializer_class = PartnerCommissionSerializer

    def get_queryset(self):
        return _partner_queryset(
            PartnerCommission,
            _user_company(self.request),
        )

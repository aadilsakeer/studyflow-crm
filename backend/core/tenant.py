from rest_framework.exceptions import ValidationError

from core.mixins import get_user_company


def require_tenant_company(user):
    company = get_user_company(user)

    if not company:
        raise ValidationError(
            {
                "detail": (
                    "Your account is not linked "
                    "to a company."
                ),
            }
        )

    return company


class TenantCompanyQuerysetMixin:
    company_field = "company"

    def get_tenant_company(self):
        return get_user_company(self.request.user)

    def filter_by_tenant(self, queryset):
        company = self.get_tenant_company()

        if not company:
            return queryset.none()

        return queryset.filter(
            **{self.company_field: company},
        )


class TenantLeadQuerysetMixin:
    def get_tenant_company(self):
        return get_user_company(self.request.user)

    def filter_leads_by_tenant(self, queryset):
        company = self.get_tenant_company()

        if not company:
            return queryset.none()

        return queryset.filter(
            lead__company=company,
        )


class TenantStudentQuerysetMixin:
    def get_tenant_company(self):
        return get_user_company(self.request.user)

    def filter_by_student_company(self, queryset):
        company = self.get_tenant_company()

        if not company:
            return queryset.none()

        return queryset.filter(
            student__company=company,
        )

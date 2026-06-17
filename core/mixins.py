from rest_framework.exceptions import ValidationError


def get_user_company(user):
    return getattr(user, "company", None)


def require_company(user):
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


class CompanyFilteredMixin:

    company_field = "company"

    def get_queryset(self):
        queryset = super().get_queryset()
        company = getattr(
            self.request.user,
            "company",
            None,
        )

        if not company:
            return queryset.none()

        return queryset.filter(
            **{
                self.company_field: company,
            }
        )


class LeadCompanyFilteredMixin:

    def get_queryset(self):
        queryset = super().get_queryset()
        company = getattr(
            self.request.user,
            "company",
            None,
        )

        if not company:
            return queryset.none()

        return queryset.filter(
            lead__company=company,
        )


class CompanyCreateMixin:

    company_field = "company"

    def get_company(self):
        return getattr(
            self.request.user,
            "company",
            None,
        )

    def perform_create(self, serializer):
        company = self.get_company()

        if not company:
            raise ValidationError(
                {
                    "detail": (
                        "Your account is not linked "
                        "to a company."
                    ),
                }
            )

        serializer.save(
            **{
                self.company_field: company,
            }
        )

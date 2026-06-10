class CompanyFilteredMixin:

    company_field = "company"

    def get_queryset(self):

        queryset = super().get_queryset()

        return queryset.filter(
            **{
                self.company_field:
                self.request.user.company
            }
        )
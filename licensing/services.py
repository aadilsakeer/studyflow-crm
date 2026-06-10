from licensing.models import CompanyModule


class ModuleAccessService:

    @staticmethod
    def has_access(company, module_code):

        return CompanyModule.objects.filter(
            company=company,
            module__code=module_code,
            is_enabled=True
        ).exists()
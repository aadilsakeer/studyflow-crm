from licensing.models import CompanyModule


CORE_MODULE_CODES = frozenset({
    "crm",
    "dashboard",
    "admissions",
})


class ModuleAccessService:

    @staticmethod
    def has_access(company, module_code):

        if module_code in CORE_MODULE_CODES:
            return True

        company_modules = CompanyModule.objects.filter(
            company=company,
        )

        if not company_modules.exists():
            return True

        return company_modules.filter(
            module__code=module_code,
            is_enabled=True,
        ).exists()
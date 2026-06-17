from licensing.models import CompanyModule


CORE_MODULE_CODES = frozenset({
    "crm",
    "dashboard",
    "admissions",
})


class ModuleAccessService:

    @staticmethod
    def has_access(company, module_code):

        if not company:
            return False

        if module_code in CORE_MODULE_CODES:
            return True

        return CompanyModule.objects.filter(
            company=company,
            module__code=module_code,
            is_enabled=True,
        ).exists()
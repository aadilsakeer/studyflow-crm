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

        from .usage_service import UsageLimitService

        subscription = UsageLimitService.get_subscription(company)
        if subscription and not subscription.is_usable():
            return False

        if module_code in CORE_MODULE_CODES:
            return True

        cm = CompanyModule.objects.filter(
            company=company,
            module__code=module_code,
            module__is_active=True,
        ).select_related('module').first()

        if not cm:
            return False

        return cm.is_accessible()

from rest_framework.exceptions import PermissionDenied

from .services import ModuleAccessService


class LicensedModuleMixin:

    licensed_module = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        module_code = self.licensed_module

        if not module_code:
            return

        company = getattr(request.user, 'company', None)

        if not company:
            raise PermissionDenied('Company not found.')

        if not ModuleAccessService.has_access(
            company,
            module_code,
        ):
            raise PermissionDenied(
                'Module not available in your subscription.',
            )

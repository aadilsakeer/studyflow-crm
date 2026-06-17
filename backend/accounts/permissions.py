from rest_framework.permissions import BasePermission

from accounts.constants import PERM_UNIVERSITIES_VIEW
from accounts.services.permission_service import (
    user_has_permission,
    user_has_any_permission,
)


class IsCompanyMember(BasePermission):
    message = "Your account is not linked to a company."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return getattr(user, "company_id", None) is not None


class HasPermission(BasePermission):
    message = "You do not have permission to perform this action."

    def __init__(self, code):
        self.code = code

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user_has_permission(user, self.code)


class HasAnyPermission(BasePermission):
    message = "You do not have permission to perform this action."

    def __init__(self, *codes):
        self.codes = codes

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return user_has_any_permission(user, self.codes)


def permission_required(code):
    """Return a permission class for DRF permission_classes."""

    class _Permission(HasPermission):
        def __init__(self):
            super().__init__(code)

    return _Permission


class IsPlatformAdmin(BasePermission):
    message = (
        "Only platform administrators can modify "
        "the shared catalog."
    )

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.is_superuser


class ActionPermissionMixin:
    permission_map = {}

    def get_permissions(self):
        from rest_framework.permissions import (
            IsAuthenticated,
        )

        method = self.request.method.upper()
        code = self.permission_map.get(method)

        if not code:
            return [IsAuthenticated()]

        return [
            IsAuthenticated(),
            IsCompanyMember(),
            permission_required(code)(),
        ]


class CatalogPermissionMixin(ActionPermissionMixin):
    catalog_view_permission = PERM_UNIVERSITIES_VIEW

    def get_permissions(self):
        from rest_framework.permissions import (
            IsAuthenticated,
        )

        if self.request.method.upper() == "GET":
            return [
                IsAuthenticated(),
                IsCompanyMember(),
                permission_required(
                    self.catalog_view_permission,
                )(),
            ]

        return [
            IsAuthenticated(),
            IsPlatformAdmin(),
        ]


def crm_permission_map(module):
    return {
        "GET": f"{module}.view",
        "POST": f"{module}.add",
        "PUT": f"{module}.change",
        "PATCH": f"{module}.change",
        "DELETE": f"{module}.delete",
    }

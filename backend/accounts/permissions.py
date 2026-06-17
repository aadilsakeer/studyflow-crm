from rest_framework.permissions import BasePermission

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
            HasPermission(code),
        ]


def crm_permission_map(module):
    return {
        "GET": f"{module}.view",
        "POST": f"{module}.add",
        "PUT": f"{module}.change",
        "PATCH": f"{module}.change",
        "DELETE": f"{module}.delete",
    }

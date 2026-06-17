from django.core.cache import cache

from accounts.models import RolePermission


CACHE_TTL = 300


def _cache_key(user_id):
    return f"user_permissions:{user_id}"


def invalidate_user_permissions(user_id):
    cache.delete(_cache_key(user_id))


def get_user_permission_codes(user):
    if not user or not user.is_authenticated:
        return frozenset()

    if user.is_superuser:
        from accounts.constants import ALL_PERMISSIONS

        return frozenset(
            code for code, _ in ALL_PERMISSIONS
        )

    key = _cache_key(user.pk)
    cached = cache.get(key)

    if cached is not None:
        return frozenset(cached)

    if not user.role_id:
        return frozenset()

    codes = RolePermission.objects.filter(
        role_id=user.role_id,
    ).values_list(
        "permission__code",
        flat=True,
    )

    code_list = list(codes)
    cache.set(key, code_list, CACHE_TTL)

    return frozenset(code_list)


def user_has_permission(user, code):
    return code in get_user_permission_codes(user)


def user_has_any_permission(user, codes):
    permissions = get_user_permission_codes(user)
    return any(code in permissions for code in codes)

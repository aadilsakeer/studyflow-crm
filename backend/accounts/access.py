from django.db.models import Q

from accounts.constants import (
    ROLE_MANAGER,
    ROLE_COUNSELLOR,
)
from accounts.models import StaffProfile


def filter_leads_for_user(queryset, user):
    if user.is_superuser:
        return queryset

    role = getattr(user, "role", None)

    if not role:
        return queryset

    role_name = role.name

    if role_name == ROLE_MANAGER:
        team_ids = list(
            StaffProfile.objects.filter(
                reporting_manager=user,
            ).values_list(
                "user_id",
                flat=True,
            )
        )
        team_ids.append(user.pk)

        return queryset.filter(
            Q(assigned_to_id__in=team_ids)
            | Q(assigned_to__isnull=True)
        )

    if role_name == ROLE_COUNSELLOR:
        return queryset.filter(
            Q(assigned_to=user)
            | Q(assigned_to__isnull=True)
        )

    return queryset


def filter_students_for_user(queryset, user):
    if user.is_superuser:
        return queryset

    role = getattr(user, "role", None)

    if not role:
        return queryset

    role_name = role.name

    if role_name == ROLE_MANAGER:
        team_ids = list(
            StaffProfile.objects.filter(
                reporting_manager=user,
            ).values_list(
                "user_id",
                flat=True,
            )
        )
        team_ids.append(user.pk)

        return queryset.filter(
            Q(assigned_counselor_id__in=team_ids)
            | Q(assigned_counselor__isnull=True)
        )

    if role_name == ROLE_COUNSELLOR:
        return queryset.filter(
            Q(assigned_counselor=user)
            | Q(assigned_counselor__isnull=True)
        )

    return queryset

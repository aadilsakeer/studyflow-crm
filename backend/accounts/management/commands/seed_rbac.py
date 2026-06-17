from django.core.management.base import BaseCommand

from accounts.constants import (
    ALL_PERMISSIONS,
    ROLE_PERMISSIONS,
    ROLE_ADMIN,
    ROLE_VIEWER,
)
from accounts.models import (
    Role,
    Permission,
    RolePermission,
    CustomUser,
)


class Command(BaseCommand):
    help = (
        "Seed RBAC roles and permissions. "
        "Use --assign-users to set default roles."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--assign-users",
            action="store_true",
            help=(
                "Assign Admin to superusers and "
                "Viewer to users without a role."
            ),
        )

    def handle(self, *args, **options):
        permission_map = {}

        for code, name in ALL_PERMISSIONS:
            perm, _ = Permission.objects.update_or_create(
                code=code,
                defaults={"name": name},
            )
            permission_map[code] = perm

        self.stdout.write(
            f"Permissions: {len(permission_map)}"
        )

        for role_name, codes in (
            ROLE_PERMISSIONS.items()
        ):
            role, _ = Role.objects.update_or_create(
                name=role_name,
            )

            RolePermission.objects.filter(
                role=role,
            ).exclude(
                permission__code__in=codes,
            ).delete()

            for code in codes:
                RolePermission.objects.get_or_create(
                    role=role,
                    permission=permission_map[code],
                )

            self.stdout.write(
                f"Role {role_name}: "
                f"{len(codes)} permissions"
            )

        if options["assign_users"]:
            admin_role = Role.objects.get(
                name=ROLE_ADMIN,
            )
            viewer_role = Role.objects.get(
                name=ROLE_VIEWER,
            )

            for user in CustomUser.objects.filter(
                is_superuser=True,
            ):
                if user.role_id != admin_role.pk:
                    user.role = admin_role
                    user.save(
                        update_fields=["role"],
                    )

            updated = CustomUser.objects.filter(
                role__isnull=True,
                is_superuser=False,
            ).update(role=viewer_role)

            self.stdout.write(
                f"Assigned Viewer to {updated} users"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "RBAC seed complete."
            )
        )

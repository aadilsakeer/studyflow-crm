"""Phase 1 smoke test — run via: python scripts/phase1_smoke_test.py"""
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings

settings.ALLOWED_HOSTS = [
    *settings.ALLOWED_HOSTS,
    "testserver",
    "localhost",
    "127.0.0.1",
]

from django.test import RequestFactory
from rest_framework.test import APIClient

from accounts.constants import (
    ROLE_ADMIN,
    ROLE_COUNSELLOR,
    ROLE_FINANCE,
    ROLE_MANAGER,
    ROLE_PERMISSIONS,
    ROLE_TELECALLER,
    ROLE_VIEWER,
    ALL_PERMISSIONS,
    PERM_LEADS_VIEW,
    PERM_STUDENTS_VIEW,
    PERM_PAYMENTS_VIEW,
)
from accounts.models import CustomUser, Role
from accounts.permissions import permission_required
from accounts.services.permission_service import (
    get_user_permission_codes,
    invalidate_user_permissions,
)
from core.models import Company
from dashboard.api_views import DashboardAPIView
from leads.models import Lead


ROLE_EXPECTED_COUNTS = {
    ROLE_ADMIN: len(ALL_PERMISSIONS),
    **{
        role: len(codes)
        for role, codes in ROLE_PERMISSIONS.items()
        if role != ROLE_ADMIN
    },
}

ENDPOINTS = [
    ("Login (token)", "POST", "/api/token/", None),
    ("Current user", "GET", "/api/me/", None),
    ("Dashboard", "GET", "/api/dashboard/", None),
    ("Leads", "GET", "/api/leads/", None),
    ("Follow Ups", "GET", "/api/followups/", None),
    ("Call Logs", "GET", "/api/calllogs/", None),
    ("Students", "GET", "/api/students/", None),
    ("Applications", "GET", "/api/applications/", None),
    ("Universities", "GET", "/api/universities/", None),
]

ROLE_ENDPOINT_EXPECTED = {
    ROLE_ADMIN: {name: 200 for name, *_ in ENDPOINTS},
    ROLE_MANAGER: {name: 200 for name, *_ in ENDPOINTS},
    ROLE_COUNSELLOR: {name: 200 for name, *_ in ENDPOINTS},
    ROLE_TELECALLER: {
        "Login (token)": 200,
        "Current user": 200,
        "Dashboard": 200,
        "Leads": 200,
        "Follow Ups": 200,
        "Call Logs": 200,
        "Students": 403,
        "Applications": 403,
        "Universities": 200,
    },
    ROLE_FINANCE: {
        "Login (token)": 200,
        "Current user": 200,
        "Dashboard": 200,
        "Leads": 403,
        "Follow Ups": 403,
        "Call Logs": 403,
        "Students": 200,
        "Applications": 200,
        "Universities": 403,
    },
    ROLE_VIEWER: {name: 200 for name, *_ in ENDPOINTS},
}


def section(title):
    print(f"\n{'=' * 60}")
    print(title)
    print("=" * 60)


def verify_permission_factory():
    section("1. permission_required() factory")
    perm_class = permission_required("dashboard.view")
    instance = perm_class()
    factory = RequestFactory()
    request = factory.get("/api/dashboard/")
    request.user = CustomUser(is_superuser=True)
    view = DashboardAPIView()
    result = instance.has_permission(request, view)
    assert result is True, "Superuser should pass permission check"
    print("PASS: permission_required() instantiates and checks correctly")


def verify_role_matrix():
    section("2. Role permission matrix")
    all_pass = True

    for role_name, expected_count in ROLE_EXPECTED_COUNTS.items():
        role = Role.objects.get(name=role_name)
        db_codes = set(
            role.rolepermission_set.values_list(
                "permission__code",
                flat=True,
            )
        )
        expected_codes = set(ROLE_PERMISSIONS[role_name])

        if db_codes != expected_codes:
            all_pass = False
            missing = expected_codes - db_codes
            extra = db_codes - expected_codes
            print(f"FAIL {role_name}: mismatch")
            if missing:
                print(f"  missing: {missing}")
            if extra:
                print(f"  extra: {extra}")
        elif len(db_codes) != expected_count:
            all_pass = False
            print(
                f"FAIL {role_name}: "
                f"count {len(db_codes)} != {expected_count}"
            )
        else:
            print(
                f"PASS {role_name}: "
                f"{len(db_codes)} permissions"
            )

    finance_codes = get_user_permission_codes(
        CustomUser(role=Role.objects.get(name=ROLE_FINANCE))
    )
    if PERM_LEADS_VIEW in finance_codes:
        print("FAIL Finance: has leads.view (should not)")
        all_pass = False
    else:
        print("PASS Finance: no lead permissions")

    if PERM_PAYMENTS_VIEW not in finance_codes:
        role = Role.objects.get(name=ROLE_FINANCE)
        perms = get_user_permission_codes(
            CustomUser(role=role, role_id=role.pk)
        )
        if PERM_PAYMENTS_VIEW not in perms:
            print("FAIL Finance: missing payments.view")
            all_pass = False
    else:
        print("PASS Finance: has payments.view")

    return all_pass


def verify_user_assignments():
    section("3. User role assignments")
    users = CustomUser.objects.select_related(
        "role", "company"
    ).filter(is_active=True)

    for user in users:
        role_name = user.role.name if user.role else "None"
        company = user.company.name if user.company else "None"
        print(f"  {user.username}: role={role_name}, company={company}")

    superusers = CustomUser.objects.filter(is_superuser=True)
    for user in superusers:
        if user.role and user.role.name == ROLE_ADMIN:
            print(f"PASS Superuser {user.username} -> Admin")
        elif user.is_superuser:
            print(
                f"INFO Superuser {user.username} "
                f"(role={user.role}) — superuser bypasses RBAC"
            )


def get_or_create_role_user(role_name, company):
    username = f"smoke_{role_name.lower()}"
    role = Role.objects.get(name=role_name)
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            "company": company,
            "role": role,
            "is_active": True,
        },
    )
    if not created:
        user.company = company
        user.role = role
        user.is_active = True
        user.save(update_fields=["company", "role", "is_active"])
    user.set_password("smoke_test_pass")
    user.save(update_fields=["password"])
    invalidate_user_permissions(user.pk)
    return user


def smoke_test_endpoints():
    section("4. API smoke test by role")
    company = Company.objects.order_by("id").first()
    if not company:
        print("SKIP: No company in database")
        return False

    all_pass = True
    client = APIClient()

    for role_name in ROLE_EXPECTED_COUNTS:
        user = get_or_create_role_user(role_name, company)
        client.force_authenticate(user=user)
        expected = ROLE_ENDPOINT_EXPECTED[role_name]
        print(f"\n--- Role: {role_name} ({user.username}) ---")

        for name, method, path, _ in ENDPOINTS:
            if name == "Login (token)":
                continue

            if method == "GET":
                response = client.get(path)
            else:
                response = client.post(path, {}, format="json")

            exp = expected.get(name, 200)
            status = response.status_code
            ok = status == exp
            mark = "PASS" if ok else "FAIL"
            print(f"  {mark} {name}: {status} (expected {exp})")
            if not ok:
                all_pass = False
                if hasattr(response, "data"):
                    print(f"       detail: {response.data}")

    return all_pass


def smoke_test_login_and_admin():
    section("5. Login + Admin full smoke")
    client = APIClient()
    admin = CustomUser.objects.filter(
        is_superuser=True,
        is_active=True,
    ).first()

    if not admin:
        admin = CustomUser.objects.filter(
            username="admin",
            is_active=True,
        ).first()

    if not admin:
        print("SKIP: No admin user found")
        return False

    all_pass = True

    response = client.post(
        "/api/token/",
        {"username": admin.username, "password": "admin"},
        format="json",
    )
    if response.status_code == 200:
        print(f"PASS Login: token obtained for {admin.username}")
        token = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    else:
        print(
            f"INFO Login with default password failed ({response.status_code}), "
            f"using force_authenticate for {admin.username}"
        )
        client.force_authenticate(user=admin)

    for name, method, path, _ in ENDPOINTS:
        if name == "Login (token)":
            continue
        if method == "GET":
            response = client.get(path)
        else:
            response = client.post(path, {}, format="json")

        ok = response.status_code == 200
        mark = "PASS" if ok else "FAIL"
        print(f"  {mark} {name}: {response.status_code}")
        if not ok:
            all_pass = False

    return all_pass


def smoke_test_lead_conversion():
    section("6. Lead conversion")
    company = Company.objects.order_by("id").first()
    admin = CustomUser.objects.filter(
        is_superuser=True,
        company=company,
    ).first() or CustomUser.objects.filter(
        role__name=ROLE_ADMIN,
        company=company,
    ).first()

    if not admin:
        admin = CustomUser.objects.filter(is_superuser=True).first()

    if not company or not admin:
        print("SKIP: Need company and admin user")
        return True

    client = APIClient()
    client.force_authenticate(user=admin)

    lead = Lead.objects.filter(
        company=company,
        status__in=["new", "contacted", "qualified"],
    ).exclude(
        student__isnull=False,
    ).first()

    if not lead:
        import uuid

        lead = Lead.objects.create(
            company=company,
            first_name="Smoke",
            last_name="Test",
            phone=f"9999{uuid.uuid4().hex[:6]}",
            status="qualified",
            assigned_to=admin,
        )
        print(f"Created test lead #{lead.pk}")

    response = client.post(f"/api/leads/{lead.pk}/convert/")
    if response.status_code in (200, 201):
        print(f"PASS Lead conversion: lead #{lead.pk} -> student")
        return True

    detail = getattr(response, "data", response.content)
    if response.status_code == 400 and "already" in str(detail).lower():
        print(f"PASS Lead conversion: lead #{lead.pk} already converted")
        return True

    print(f"FAIL Lead conversion: {response.status_code} {detail}")
    return False


def main():
    print("Platform Hardening Phase 1 — Smoke Test")
    results = []

    try:
        verify_permission_factory()
        results.append(("permission_required", True))
    except Exception as exc:
        print(f"FAIL: {exc}")
        results.append(("permission_required", False))

    results.append(("role_matrix", verify_role_matrix()))
    verify_user_assignments()
    results.append(("endpoint_smoke", smoke_test_endpoints()))
    results.append(("admin_smoke", smoke_test_login_and_admin()))
    results.append(("lead_conversion", smoke_test_lead_conversion()))

    section("SUMMARY")
    all_ok = True
    for name, ok in results:
        mark = "PASS" if ok else "FAIL"
        print(f"  {mark}: {name}")
        if not ok:
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

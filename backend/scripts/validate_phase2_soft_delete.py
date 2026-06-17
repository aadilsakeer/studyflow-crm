"""Phase 2 soft delete validation — run: python scripts/validate_phase2_soft_delete.py"""
import os
import sys
import uuid

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

from rest_framework.test import APIClient

from accounts.constants import (
    ROLE_ADMIN,
    ROLE_FINANCE,
    ROLE_MANAGER,
    ROLE_VIEWER,
    PERM_LEADS_RESTORE,
    PERM_LEADS_VIEW,
    PERM_STUDENTS_RESTORE,
)
from accounts.models import CustomUser, Role
from accounts.services.permission_service import get_user_permission_codes
from admissions.models import Application, Student
from core.models import Company
from dashboard.services import DashboardService
from leads.models import Lead, LeadAuditLog, LeadTimeline


results = []
bugs = []


def test(name, fn):
    try:
        fn()
        results.append((name, "PASS", None))
        print(f"PASS  {name}")
    except AssertionError as exc:
        results.append((name, "FAIL", str(exc)))
        bugs.append({"test": name, "error": str(exc)})
        print(f"FAIL  {name}: {exc}")
    except Exception as exc:
        results.append((name, "FAIL", f"{type(exc).__name__}: {exc}"))
        bugs.append({"test": name, "error": str(exc)})
        print(f"FAIL  {name}: {type(exc).__name__}: {exc}")


def uid(prefix="9"):
    return f"{prefix}{uuid.uuid4().hex[:8]}"


def get_company(name=None):
    if name:
        return Company.objects.filter(name=name).first()
    return Company.objects.order_by("id").first()


def role_user(role_name, company):
    username = f"val_{role_name.lower()}"
    role = Role.objects.get(name=role_name)
    user, _ = CustomUser.objects.get_or_create(
        username=username,
        defaults={"company": company, "role": role, "is_active": True},
    )
    user.company = company
    user.role = role
    user.is_active = True
    user.save(update_fields=["company", "role", "is_active"])
    user.set_password("val_test_pass")
    user.save(update_fields=["password"])
    return user


def admin_client(company):
    user = CustomUser.objects.filter(
        is_superuser=True,
        company=company,
    ).first()
    if not user:
        user = role_user(ROLE_ADMIN, company)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def create_lead(client, phone=None, **extra):
    phone = phone or uid("7")
    payload = {
        "first_name": "Val",
        "last_name": "Test",
        "phone": phone,
        "status": "new",
        **extra,
    }
    r = client.post("/api/leads/", payload, format="json")
    assert r.status_code == 201, r.data
    return r.data["id"], phone


def create_student_via_convert(client, admin_user, phone=None):
    lid, phone = create_lead(client, phone=phone)
    r = client.post(f"/api/leads/{lid}/convert/")
    assert r.status_code == 201, r.data
    student = Student.objects.get(lead_id=lid)
    return lid, student.id, student.student_id, phone


def create_application(client, student_id):
    r = client.post(
        "/api/applications/",
        {
            "student": student_id,
            "university_name": "Test Uni",
            "course_name": "Test Course",
            "intake": "Jan 2026",
            "application_status": "draft",
        },
        format="json",
    )
    assert r.status_code == 201, r.data
    return r.data["id"]


def main():
    company = get_company()
    assert company, "Need at least one company"
    client, admin = admin_client(company)

    other_company = Company.objects.exclude(pk=company.pk).first()
    if not other_company:
        other_company = Company.objects.create(name=f"Other Co {uid()[:6]}")
    other_client, other_admin = admin_client(other_company)

    # --- Lead delete/restore ---
    def t_lead_delete_restore():
        lid, phone = create_lead(client)
        assert client.get(f"/api/leads/{lid}/").status_code == 200
        assert client.delete(f"/api/leads/{lid}/").status_code == 204
        assert client.get(f"/api/leads/{lid}/").status_code == 404
        trash = client.get("/api/leads/trash/")
        assert trash.status_code == 200
        assert any(x["id"] == lid for x in trash.data["results"])
        assert LeadTimeline.objects.filter(lead_id=lid, action="deleted").exists()
        assert LeadAuditLog.objects.filter(
            lead_id=lid, field_changed="is_deleted"
        ).exists()
        assert client.post(f"/api/leads/{lid}/restore/").status_code == 200
        assert client.get(f"/api/leads/{lid}/").status_code == 200

    test("Lead delete/restore", t_lead_delete_restore)

    # --- Lead with student blocked ---
    def t_lead_delete_blocked_with_student():
        lid, sid, _, _ = create_student_via_convert(client, admin)
        r = client.delete(f"/api/leads/{lid}/")
        assert r.status_code == 400, r.data

    test("Lead delete blocked when student exists", t_lead_delete_blocked_with_student)

    # --- Phone uniqueness after delete ---
    def t_phone_uniqueness_after_delete():
        phone = uid("7")
        lid1, _ = create_lead(client, phone=phone)
        assert client.delete(f"/api/leads/{lid1}/").status_code == 204
        lid2, _ = create_lead(client, phone=phone)
        assert lid2 != lid1
        assert client.get(f"/api/leads/{lid2}/").status_code == 200

    test("Phone uniqueness after delete", t_phone_uniqueness_after_delete)

    # --- Restore conflict (duplicate phone) ---
    def t_restore_conflict_phone():
        phone = uid("7")
        lid1, _ = create_lead(client, phone=phone)
        assert client.delete(f"/api/leads/{lid1}/").status_code == 204
        lid2, _ = create_lead(client, phone=phone)
        r = client.post(f"/api/leads/{lid1}/restore/")
        assert r.status_code == 400, r.data

    test("Restore conflict handling (phone)", t_restore_conflict_phone)

    # --- Student delete/restore ---
    def t_student_delete_restore():
        lid, sid, stu_id, _ = create_student_via_convert(client, admin)
        timeline_before = LeadTimeline.objects.filter(lead_id=lid).count()
        audit_before = LeadAuditLog.objects.filter(lead_id=lid).count()
        assert client.delete(f"/api/students/{sid}/").status_code == 204
        assert client.get(f"/api/students/{sid}/").status_code == 404
        trash = client.get("/api/students/trash/")
        assert trash.status_code == 200
        assert any(x["id"] == sid for x in trash.data["results"])
        assert LeadTimeline.objects.filter(lead_id=lid).count() == timeline_before
        assert LeadAuditLog.objects.filter(lead_id=lid).count() >= audit_before
        r = client.post(f"/api/students/{sid}/restore/")
        assert r.status_code == 200, r.data
        assert client.get(f"/api/students/{sid}/").status_code == 200

    test("Student delete/restore", t_student_delete_restore)

    # --- Student ID uniqueness after delete ---
    def t_student_id_uniqueness():
        lid, sid, stu_id, _ = create_student_via_convert(client, admin)
        assert client.delete(f"/api/students/{sid}/").status_code == 204
        lid2, phone = create_lead(client)
        r = client.post(f"/api/leads/{lid2}/convert/")
        assert r.status_code == 201, r.data
        new_student = Student.objects.get(lead_id=lid2)
        assert new_student.student_id != stu_id

    test("Student ID reuse after delete (new student)", t_student_id_uniqueness)

    # --- Application delete/restore ---
    def t_application_delete_restore():
        lid, sid, _, _ = create_student_via_convert(client, admin)
        app_id = create_application(client, sid)
        assert client.delete(f"/api/applications/{app_id}/").status_code == 204
        assert client.get(f"/api/applications/{app_id}/").status_code == 404
        trash = client.get("/api/applications/trash/")
        assert trash.status_code == 200
        assert any(x["id"] == app_id for x in trash.data["results"])
        assert client.post(f"/api/applications/{app_id}/restore/").status_code == 200
        assert client.get(f"/api/applications/{app_id}/").status_code == 200

    test("Application delete/restore", t_application_delete_restore)

    # --- Student delete cascades applications ---
    def t_student_cascade_apps():
        lid, sid, _, _ = create_student_via_convert(client, admin)
        app_id = create_application(client, sid)
        assert client.delete(f"/api/students/{sid}/").status_code == 204
        assert Application.objects.filter(pk=app_id).count() == 0
        assert Application.all_objects.dead().filter(pk=app_id).exists()

    test("Student delete cascades applications", t_student_cascade_apps)

    # --- RBAC permissions ---
    def t_rbac():
        admin_role = Role.objects.get(name=ROLE_ADMIN)
        perms = get_user_permission_codes(
            CustomUser(role=admin_role, role_id=admin_role.pk)
        )
        assert PERM_LEADS_RESTORE in perms
        assert PERM_STUDENTS_RESTORE in perms
        finance = role_user(ROLE_FINANCE, company)
        fp = get_user_permission_codes(finance)
        assert PERM_LEADS_VIEW not in fp
        assert PERM_LEADS_RESTORE not in fp
        viewer = role_user(ROLE_VIEWER, company)
        vc = APIClient()
        vc.force_authenticate(user=viewer)
        assert vc.get("/api/leads/trash/").status_code == 403
        manager = role_user(ROLE_MANAGER, company)
        mc = APIClient()
        mc.force_authenticate(user=manager)
        assert mc.get("/api/leads/trash/").status_code == 403

    test("RBAC permissions (restore Admin-only)", t_rbac)

    # --- Cross-tenant restore ---
    def t_cross_tenant():
        lid, _ = create_lead(client)
        assert client.delete(f"/api/leads/{lid}/").status_code == 204
        r = other_client.post(f"/api/leads/{lid}/restore/")
        assert r.status_code == 404, r.data

    test("Cross-tenant restore protection", t_cross_tenant)

    # --- Tenant isolation trash list ---
    def t_trash_tenant_isolation():
        lid, _ = create_lead(client)
        assert client.delete(f"/api/leads/{lid}/").status_code == 204
        trash = other_client.get("/api/leads/trash/")
        assert trash.status_code in (200, 403)
        if trash.status_code == 200:
            assert not any(x["id"] == lid for x in trash.data["results"])

    test("Trash list tenant isolation", t_trash_tenant_isolation)

    # --- Dashboard counts ---
    def t_dashboard():
        before = DashboardService.get_dashboard_data(company)
        phone = uid("7")
        lid, _ = create_lead(client, phone=phone)
        after_create = DashboardService.get_dashboard_data(company)
        assert after_create["total_leads"] == before["total_leads"] + 1
        assert client.delete(f"/api/leads/{lid}/").status_code == 204
        after_delete = DashboardService.get_dashboard_data(company)
        assert after_delete["total_leads"] == before["total_leads"]
        r = client.get("/api/dashboard/")
        assert r.status_code == 200

    test("Dashboard counts exclude deleted", t_dashboard)

    # --- Search ---
    def t_search():
        phone = uid("7")
        lid, _ = create_lead(client, phone=phone, first_name="SearchableXYZ")
        r = client.get("/api/leads/?search=SearchableXYZ")
        assert r.status_code == 200
        assert any(x["id"] == lid for x in r.data["results"])
        assert client.delete(f"/api/leads/{lid}/").status_code == 204
        r = client.get("/api/leads/?search=SearchableXYZ")
        assert not any(x["id"] == lid for x in r.data["results"])

    test("Search excludes deleted", t_search)

    # --- Filters ---
    def t_filters():
        phone = uid("7")
        lid, _ = create_lead(client, phone=phone, status="new")
        r = client.get("/api/leads/?status=new")
        assert any(x["id"] == lid for x in r.data["results"])
        assert client.delete(f"/api/leads/{lid}/").status_code == 204
        r = client.get("/api/leads/?status=new")
        assert not any(x["id"] == lid for x in r.data["results"])

    test("Filters exclude deleted", t_filters)

    # --- Pagination ---
    def t_pagination():
        r = client.get("/api/leads/?page=1")
        assert r.status_code == 200
        assert "count" in r.data and "results" in r.data
        r = client.get("/api/leads/trash/?page=1")
        assert r.status_code == 200
        assert "count" in r.data and "results" in r.data

    test("Pagination on list and trash", t_pagination)

    # --- Follow-ups hidden for deleted lead ---
    def t_followups_hidden():
        phone = uid("7")
        lid, _ = create_lead(client, phone=phone)
        from django.utils import timezone
        r = client.post(
            "/api/followups/",
            {
                "lead": lid,
                "follow_up_date": timezone.now().isoformat(),
                "notes": "test",
            },
            format="json",
        )
        assert r.status_code == 201, r.data
        fu_id = r.data["id"]
        assert any(x["id"] == fu_id for x in client.get("/api/followups/").data["results"])
        assert client.delete(f"/api/leads/{lid}/").status_code == 204
        assert not any(
            x["id"] == fu_id
            for x in client.get("/api/followups/").data["results"]
        )

    test("Follow-ups hidden when lead deleted", t_followups_hidden)

    # --- Recycle Bin UI ---
    def t_recycle_bin_ui():
        import pathlib
        root = pathlib.Path(__file__).resolve().parents[2] / "frontend" / "src"
        matches = list(root.rglob("*Recycle*"))
        assert matches, "No Recycle Bin frontend component found"

    test("Recycle Bin UI", t_recycle_bin_ui)

    # --- Summary ---
    print("\n" + "=" * 60)
    passed = sum(1 for _, s, _ in results if s == "PASS")
    failed = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"TOTAL: {len(results)} | PASS: {passed} | FAIL: {failed}")
    print("=" * 60)
    for name, status, err in results:
        mark = status
        suffix = f" — {err}" if err else ""
        print(f"  [{mark}] {name}{suffix}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

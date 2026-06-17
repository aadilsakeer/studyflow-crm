# Platform Hardening Phase 1 — Completion Report

**Branch:** `platform-hardening-phase-1`  
**Date:** 2026-06-18  
**Status:** Complete

---

## Commits (8 total)

| # | Commit | Description |
|---|--------|-------------|
| 1 | `b8d86f7` | RBAC — roles, permissions, seed command, API + UI wiring |
| 2 | `87d0c96` | Tenant isolation — strict company scoping, orphan lead access removed |
| 3 | `9e29651` | IDOR fixes — FK ownership validators on nested serializers |
| 4 | `96b6fcb` | Global pagination — backend default + frontend page controls |
| 5 | `df611d1` | Database indexes on hot query paths |
| 6 | `03560c8` | Query optimization — select_related on list APIs |
| 7 | `36df1ce` | permission_required() factory fix for DRF permission_classes |
| 8 | *(this commit)* | Phase 1 completion docs + smoke test script |

---

## Milestone Deliverables

### 1. RBAC
- 6 roles: Admin, Manager, Counsellor, Telecaller, Finance, Viewer
- 39 permission codes with `ROLE_PERMISSIONS` matrix
- `seed_rbac` management command
- Backend: `HasPermission`, `ActionPermissionMixin`, `permission_required()`
- Frontend: `PermissionsProvider`, `usePermissions`, nav/action gating

### 2. Tenant Isolation
- Leads scoped strictly to `user.company` (no orphan `company__isnull=True`)
- `company` and `score` read-only on lead serializer
- Follow-ups/call logs reject leads without company

### 3. IDOR Prevention
- `core/validators.py` — cross-tenant FK validation
- Wired into admissions, followups, calllogs serializers

### 4. Pagination
- `StandardPagination` (20/page, max 100) globally configured
- Frontend: Follow Ups, Students, Applications paginated

### 5. Query Optimization
- `select_related` / `prefetch_related` on leads, followups, calllogs, admissions list views

### 6. Database Indexes
- Lead, FollowUp, LeadTimeline, LeadAuditLog
- Student, Application
- Migrations: `leads.0009`, `admissions.0009` — applied

---

## Verification Results

### seed_rbac --assign-users
```
Permissions: 39
Role Admin: 39 | Manager: 27 | Counsellor: 20
Role Telecaller: 10 | Finance: 5 | Viewer: 8
Assigned Viewer to 0 users
RBAC seed complete.
```

### Role Matrix — All PASS
| Role | Permissions | Key checks |
|------|-------------|------------|
| Admin | 39 | Full access |
| Manager | 27 | CRM + admissions, no finance write |
| Counsellor | 20 | Own-scope leads/students |
| Telecaller | 10 | Leads/followups/calllogs only |
| Finance | 5 | Dashboard, students, applications, payments, invoices — **no leads** |
| Viewer | 8 | Read-only CRM |

### User Assignments
| User | Role | Company |
|------|------|---------|
| crmadmin | Admin | StudyFlow ERP |
| admin | Admin | StudyFlow ERP |

Smoke test users created: `smoke_admin`, `smoke_manager`, `smoke_counsellor`, `smoke_telecaller`, `smoke_finance`, `smoke_viewer` (password: `smoke_test_pass`)

### Orphan Lead Audit
| Metric | Count |
|--------|-------|
| Orphan leads found | **0** |
| Orphan leads fixed | **0** |

Command: `python manage.py fix_orphan_leads` → Assigned 0 orphan lead(s) to StudyFlow ERP.

### Smoke Test — All PASS
Run: `python scripts/phase1_smoke_test.py`

| Area | Result |
|------|--------|
| permission_required() factory | PASS |
| Role permission matrix | PASS |
| API endpoints by role (6 roles) | PASS |
| Login (JWT token) | PASS |
| Dashboard | PASS |
| Leads | PASS |
| Follow Ups | PASS |
| Call Logs | PASS |
| Students | PASS |
| Applications | PASS |
| Universities | PASS |
| Lead conversion | PASS |

**Role-specific denials verified:**
- Telecaller → Students/Applications: 403
- Finance → Leads/Follow Ups/Call Logs/Universities: 403

---

## Approved Scope Boundaries (held)

- Universities/courses remain **global catalog**; admin-only CUD
- No `company` FK on universities (Phase 1)
- Soft delete documented in roadmap — **not implemented**
- Phase 3 modules (Visa UI, WhatsApp, Finance UI, HRM, etc.) **not started**

---

## Known Gaps (deferred)

1. Finance sidebar — no dedicated payments/invoices nav entries yet
2. Lead drawer timeline/audit — not paginated
3. Legacy `@module_required` on HRM, WhatsApp, Reports, Notifications, etc.
4. Commit `df611d1` message says select_related but contains index work (cosmetic)

---

## Next: Phase 2

Soft delete for Leads, Students, Applications — see `docs/roadmap.md`.

Do not start Phase 3 until Phase 2 soft-delete foundation is complete.

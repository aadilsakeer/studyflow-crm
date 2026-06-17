# Globvio CRM — Product Roadmap

## Phase 1 — Platform Hardening (in progress)

- RBAC with six roles
- Tenant isolation fixes
- IDOR prevention on nested creates
- Global API pagination
- Query optimization (N+1)
- Database indexes on hot paths

## Phase 2 — Soft Delete (planned, not in Phase 1)

Add soft-delete support for core CRM entities:

| Model | Fields (proposed) |
|-------|-------------------|
| **Lead** | `is_deleted`, `deleted_at`, `deleted_by` |
| **Student** | `is_deleted`, `deleted_at`, `deleted_by` |
| **Application** | `is_deleted`, `deleted_at`, `deleted_by` |

Requirements when implemented:

- Default querysets exclude soft-deleted records
- Admin-only restore endpoint or admin action
- Cascade rules documented (e.g. soft-delete lead → hide related follow-ups)
- Audit log entry on delete/restore

## Phase 3 — Deferred modules

- Visa Cases UI
- WhatsApp integration
- Finance UI
- HRM UI
- Recruitment UI
- Client Portal
- Reporting / analytics

Do not start Phase 3 until Phase 1 and soft-delete foundation are complete.

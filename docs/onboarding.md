# Globvio Onboarding & Recovery Guide

## Owner login

### Bootstrap owner account

```bash
cd backend
python manage.py bootstrap_owner
```

Default credentials:

| Field | Value |
|-------|-------|
| Username | `owner` |
| Email | `owner@globvio.local` |
| Password | `Owner@123` |

### Sign in

1. Open the app login page.
2. Enter username **owner** and password **Owner@123**.
3. Go to **/owner** for the platform owner console.
4. Or use **Owner login help** at `/owner/login-help`.

---

## Create a company (tenant onboarding)

From the owner console (**/owner/companies** → **Onboard Tenant**):

1. Enter company name and email.
2. Enter tenant admin email and name.
3. Select a **plan**: `starter`, `growth`, `enterprise`, or `custom`.
4. Select **modules** to enable.
5. Submit — a **temporary password** is generated and shown **once**.

API alternative:

```http
POST /api/owner/onboard/
Authorization: Bearer <owner-token>

{
  "name": "Acme Consultancy",
  "email": "info@acme.com",
  "admin_email": "admin@acme.com",
  "plan_code": "growth",
  "module_codes": ["crm", "whatsapp", "admissions"]
}
```

Response includes `temporary_password`, `admin_username`, and `company_id`.

---

## Tenant admin creation

Tenant admins are created automatically during onboarding with the **Admin** role. They sign in at the main login page using:

- **Username**: their admin email
- **Password**: the temporary password from onboarding

Admins should change their password after first login (Settings when available).

---

## Password reset

### Owner — reset tenant admin password

**UI:** Company detail → **Reset Admin Password**

**API:**

```http
POST /api/owner/users/{user_id}/
{ "action": "reset_password" }
```

Returns a new `temporary_password`.

### Owner — disable / unlock user

```http
POST /api/owner/users/{user_id}/
{ "action": "disable" }

POST /api/owner/users/{user_id}/
{ "action": "unlock" }
```

### Tenant admin — reset staff password / disable staff

Requires **settings.manage** permission.

```http
POST /api/staff/{user_id}/
{ "action": "reset_password" }

POST /api/staff/{user_id}/
{ "action": "disable" }
```

---

## Module assignment

### During onboarding

Select modules in the onboard dialog or pass `module_codes` in the onboard API.

### After creation

**Owner console → Modules** for bulk assignment, or company detail → **Modules** tab:

```http
POST /api/owner/companies/{company_id}/modules/
{ "action": "enable", "module_code": "whatsapp" }

POST /api/owner/companies/{company_id}/modules/
{ "action": "trial", "module_code": "ai", "trial_days": 14 }
```

---

## Plan assignment

During onboarding, set `plan_code`. To change later:

**UI:** Company detail → change plan action

**API:**

```http
PATCH /api/owner/companies/{company_id}/
{ "action": "change_plan", "plan_code": "enterprise" }
```

Plans: **starter**, **growth**, **enterprise**, **custom**

Seed plans and module catalog:

```bash
python manage.py seed_licensing
```

---

## Recovery checklist

1. `python manage.py bootstrap_owner` — restore owner access
2. `python manage.py seed_rbac` — restore roles/permissions
3. `python manage.py seed_licensing` — restore plans/modules
4. Log in as owner → onboard or repair tenants

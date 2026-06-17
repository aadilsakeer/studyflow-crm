# Globvio CRM — Architecture

## Overview

Globvio CRM is a monorepo for a study-abroad consultancy platform.

| Layer | Stack |
|-------|-------|
| API | Django 5 + Django REST Framework |
| Auth | JWT (Simple JWT) |
| Frontend | React 19 + Vite + Material UI |
| Database | SQLite (dev) → PostgreSQL (production) |

## Repository layout

```
studyflowcrm/
├── backend/     Django project (API, admin, business logic)
├── frontend/    React SPA (CRM UI)
├── docs/        Documentation
└── scripts/     Setup helpers
```

## Backend apps (core)

| App | Purpose |
|-----|---------|
| `accounts` | Users, roles, `/api/me/` |
| `core` | Company, branch, tenant mixins |
| `leads` | Lead CRUD, timeline, audit, conversion |
| `followups` | Follow-up scheduling |
| `calllogs` | Call logging per lead |
| `dashboard` | KPIs, lead trend, recent activity |
| `admissions` | Students, applications, universities |
| `licensing` | Module access per company |

## Multi-tenancy

All CRM data is scoped by `company` on the authenticated user. Users without a company cannot create leads or view tenant data.

## API base URL

- Development: `http://127.0.0.1:8000/api`
- Frontend dev server: `http://localhost:5173`

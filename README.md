# Globvio CRM

Study abroad / immigration consultancy CRM — Django REST API + React dashboard.

## Monorepo structure

```
studyflowcrm/
├── backend/          Django + DRF API
├── frontend/         React + Vite + Material UI
├── docs/             Architecture & deployment guides
├── scripts/          Setup scripts (Windows)
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11+
- Node.js 18+

## Quick start

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_licensing
python manage.py runserver
```

Or run: `.\scripts\setup-backend.ps1`

API: `http://127.0.0.1:8000/api`

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Or run: `.\scripts\setup-frontend.ps1`

App: `http://localhost:5173`

## Auth

| Endpoint | Purpose |
|----------|---------|
| `POST /api/token/` | Login (JWT) |
| `POST /api/token/refresh/` | Refresh token |
| `GET /api/me/` | Current user profile |

## Modules

| Module | Status |
|--------|--------|
| Dashboard (KPIs, lead trend, activity) | Working |
| Leads (CRUD, timeline, audit, convert) | Working |
| Follow-ups | Working |
| Call logs | Working |
| Students / Applications / Universities | Working |
| Visa cases | Planned |

## Important: company scoping

Leads and dashboard data are scoped by company. In Django admin:

1. Create a **Company** (core app)
2. Assign your user to that company

Without a company, lists will be empty and creates will fail.

## Documentation

- [Architecture](docs/architecture.md)
- [Deployment](docs/deployment.md)

## License

Private — All rights reserved.

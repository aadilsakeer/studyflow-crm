# AGENTS.md

## Cursor Cloud specific instructions

Globvio CRM is a single product split into two dev services: a Django REST API
(`backend/`, Python) and a React + Vite SPA (`frontend/`, JavaScript). PostgreSQL
is required — `backend/config/settings.py` only configures the Postgres engine
(the README's mention of SQLite does not apply).

The update script only refreshes dependencies (creates `backend/venv`, installs
`backend/requirements.txt`, runs `npm install` in `frontend/`). Everything below
is NOT handled automatically and must be done in-session.

### Start services (in this order)

1. PostgreSQL is not started on boot. Start it before the backend:
   `sudo pg_ctlcluster 16 main start`
2. Backend (from `backend/`): `./venv/bin/python manage.py runserver 0.0.0.0:8000`
   — serves the API + Django admin at `http://127.0.0.1:8000`.
3. Frontend (from `frontend/`): `npm run dev` — Vite serves at
   `http://localhost:5173`.

### Non-obvious gotchas

- The frontend MUST run on port 5173. The backend's `CORS_ALLOWED_ORIGINS` only
  allows `localhost:5173` / `127.0.0.1:5173`, and `frontend/src/services/api.js`
  hardcodes the API base URL to `http://127.0.0.1:8000/api`. If port 5173 is
  already taken, Vite silently falls back to 5174 and browser API calls will
  fail CORS — free up 5173 instead.
- Vite binds to `localhost` (IPv6), so `curl http://127.0.0.1:5173` fails while
  `curl http://localhost:5173` returns 200. Use `localhost` (or `npm run dev --
  --host`) for the frontend.
- `backend/.env` is gitignored (persists via the VM snapshot, not git). It needs
  `SECRET_KEY` (no default — backend won't start without it), `DEBUG=True`, and
  Postgres creds matching the local cluster (`DB_USER=postgres`,
  `DB_PASSWORD=postgres`, `DB_NAME=studyflowcrm`, `DB_HOST=localhost`,
  `DB_PORT=5432`). If it is missing, recreate it from `backend/.env.example` and
  fix the DB password.
- Company scoping: CRM lists are empty and record creation fails unless the
  logged-in user is linked to a `Company`. A demo superuser `admin` /
  `admin12345` linked to a company already exists in the snapshot DB; if recreating,
  set `user.company` (and `is_staff`/`is_superuser`) via the Django admin or shell.

### After changing the schema

Migrations are not part of the update script. Run them manually when models
change: `./venv/bin/python manage.py migrate` (and
`./venv/bin/python manage.py seed_licensing` to seed licensing plans).

### Lint / test / build

- Frontend lint: `npm run lint` (currently reports pre-existing errors in the
  committed source — not caused by setup).
- Backend check: `./venv/bin/python manage.py check`.
- Tests: no automated test suite exists. `manage.py test` runs but finds 0 tests;
  the frontend has no test runner configured.
- Frontend production build: `npm run build` (dev uses `npm run dev`).

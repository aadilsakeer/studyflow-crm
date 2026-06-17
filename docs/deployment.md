# Globvio CRM — Deployment

## Environment variables (backend)

Copy `backend/.env.example` to `backend/.env` and configure:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` in dev, `False` in production |
| `DATABASE_URL` | PostgreSQL connection string (production) |

## SQLite → PostgreSQL

1. Install `psycopg2-binary` (already in `requirements.txt`).
2. Update `DATABASES` in `backend/config/settings.py` for production.
3. Run `python manage.py migrate` against the new database.

## Backend (production checklist)

```bash
cd backend
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn config.wsgi:application
```

## Frontend (production build)

```bash
cd frontend
npm ci
npm run build
```

Serve `frontend/dist/` via nginx or a CDN. Point API requests to your backend URL.

## Post-deploy

1. Create superuser: `python manage.py createsuperuser`
2. Seed licensing: `python manage.py seed_licensing`
3. Link users to a company in Django admin

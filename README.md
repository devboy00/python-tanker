# Tanker

FastAPI + SQLAlchemy + Alembic scaffold for single-customer deployments.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
```

Update `.env` values, then run:

```powershell
alembic upgrade head
tanker-seed-base
uvicorn app.main:app --reload
```

Health check:
- `GET /healthz`

## Auth + Admin API (MVP)

Authenticate with:
- `POST /auth/login` (body: `email`, `password`)
- Use returned bearer token: `Authorization: Bearer <access_token>`

Admin endpoints require authenticated users with `super_admin` role.

Available endpoints:
- `POST /auth/login`
- `GET /admin/site-settings`
- `PUT /admin/site-settings`
- `GET /admin/roles`
- `GET /admin/users`
- `POST /admin/users`
- `PATCH /admin/users/{user_id}/status`
- `PUT /admin/users/{user_id}/roles`

## Deployment

See `deploy/DEPLOYMENT.md` for ready-to-run Linux and Windows deployment plans and scripts.

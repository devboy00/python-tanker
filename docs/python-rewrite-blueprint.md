# Python Rewrite Blueprint (Single-Customer Deployment)

## Scope Clarification
This plan assumes **single-tenant per deployment** (one customer per server/site/database), not shared multi-tenant hosting.

Goal:
- Rebuild current project functionality in Python.
- Add a Super Admin area for customer/site personalization.
- Make new-customer deployments repeatable on a modern DBMS (PostgreSQL).

## Feasibility And Effort
Replicating functionality is feasible and practical, but it is still a moderate rewrite.

Estimated effort (one experienced engineer):
- MVP functional parity: 6-10 weeks
- Production-ready parity + hardened deployment/admin workflows: 10-16 weeks

## Recommended Stack
- Python 3.12+
- FastAPI
- SQLAlchemy 2.x
- Alembic for migrations
- PostgreSQL
- Jinja2 templates (or React frontend)
- passlib/bcrypt for password hashing

## Architecture Pattern
Use one codebase for all customers. Each customer gets:
- independent app deployment
- independent PostgreSQL database
- independent environment configuration

No per-customer code fork required.

## Core Data Model (Initial)

### users
- id (uuid pk)
- email (unique)
- password_hash
- is_active (bool)
- created_at
- updated_at

### roles
- id (pk)
- name (unique), e.g. super_admin, admin

### user_roles
- user_id fk -> users
- role_id fk -> roles
- unique (user_id, role_id)

### site_settings
Single-row table used by Super Admin for site personalization.
- id (pk; can use fixed single row)
- site_name
- customer_name
- logo_url
- support_email
- timezone
- theme_json (jsonb)
- updated_at

### business tables
Port existing business entities (products, receipts, organizations, etc.) from current app into normalized PostgreSQL schema.

## Super Admin Responsibilities
- Update site/customer branding and behavior in site_settings.
- Manage users (create, disable, password reset flow if added).
- Assign and revoke roles.
- Access admin maintenance actions (optionally with audit logging).

## Migration Strategy
Use Alembic migrations for all schema changes.

Standard workflow:
1. alembic upgrade head
2. Run a seed/bootstrap command to create base data.

## Seed/Bootstrap Strategy (Per Install)
Create an idempotent script (example: app/scripts/seed_base.py) that:
- Inserts default roles if missing.
- Creates/updates initial site_settings row.
- Creates initial super_admin user from environment variables.

Expected env vars:
- DATABASE_URL
- APP_ENV
- SECRET_KEY
- INITIAL_SUPERADMIN_EMAIL
- INITIAL_SUPERADMIN_PASSWORD
- SITE_NAME (optional default)

## Per-Customer Deployment Runbook
1. Provision server and PostgreSQL database/user.
2. Deploy application code.
3. Configure environment variables.
4. Run Alembic migrations.
5. Run bootstrap seed script (once per installation).
6. Start app service.
7. Validate:
   - Super Admin login
   - site settings update and persistence
   - core business workflows

## Why This Works Well
- Keeps one maintainable codebase.
- Makes customer personalization data-driven.
- Enables repeatable, scriptable deployment for each new customer.
- Avoids hardcoded per-customer behavior in source.

## Next Implementation Deliverables
1. Initial Alembic migration set (users/roles/user_roles/site_settings + first business tables).
2. Idempotent seed script template.
3. Super Admin UI/API endpoints for site settings + user/role management.
4. Deployment scripts for local, staging, and production profiles.

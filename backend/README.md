# BhoomiSetu Backend

FastAPI backend for the existing React/Vite prototype. The frontend is intentionally unchanged.

## Initial implementation scope

This branch establishes the backend foundation for the first District/Field Officer vertical slice. The shared data model and authorization system will be designed to support additional roles later.

Planned first workflow:

1. Officer authentication and permission checks
2. Officer's assigned projects
3. Project and land parcel records
4. Survey assignments and field evidence
5. Parcel verification and workflow transitions
6. Compensation assessment and award review
7. Audit trail

## Stack

- FastAPI + Pydantic Settings
- SQLAlchemy 2 async + asyncpg
- PostgreSQL (PostGIS will be enabled for parcel geometry)
- Alembic migrations
- JWT access tokens and Argon2 password hashing (auth implementation follows)

## Local setup

From the repository root:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install and configure:

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open the API docs at http://127.0.0.1:8000/docs and health check at http://127.0.0.1:8000/api/v1/health.

The initial health route does not require a database connection. Database-backed endpoints will be added after PostgreSQL/PostGIS and Alembic setup.

## Security notes

- Never commit a real `.env`, production secret, password, access token, or personal landowner data.
- The default secret is for local development only and must be replaced before authentication is enabled.
- All role-specific access will be enforced server-side using permissions and geographic/assignment scope, not frontend visibility alone.

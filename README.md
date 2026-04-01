# DocVault

A production-grade Document Management System REST API built with FastAPI, PostgreSQL, and S3. Supports JWT authentication, nested folder organization, file uploads, and is deployed to AWS Lambda via SAM.

---

## Features

- **JWT Authentication** — Register and login with secure Argon2 password hashing
- **Folder Management** — Create nested folder hierarchies; deletion blocked if subfolders exist
- **File Storage** — Upload, download, and delete files stored in S3 (LocalStack locally, real S3 on AWS)
- **Async throughout** — FastAPI + async SQLAlchemy + asyncpg for non-blocking I/O
- **Automated Tests** — 25 tests covering auth, folders, and files with real PostgreSQL and LocalStack
- **CI/CD** — GitHub Actions pipeline with lint (ruff) and test jobs
- **AWS Deployment** — Serverless via AWS Lambda + API Gateway + RDS + S3, managed by SAM

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| Database | PostgreSQL 17 (async SQLAlchemy 2.0 + asyncpg) |
| Migrations | Alembic |
| Auth | JWT (python-jose) + Argon2 (argon2-cffi) |
| File Storage | AWS S3 (boto3) / LocalStack for local dev |
| Settings | pydantic-settings |
| Lambda Adapter | Mangum |
| AWS Deployment | SAM (Serverless Application Model) |
| AWS Infra | Lambda, API Gateway, RDS, S3, VPC, Secrets Manager |
| Testing | pytest + pytest-asyncio + httpx |
| Linting | Ruff |
| Containers | Podman Compose |

---

## Project Structure

```
src/docvault/
├── main.py              # FastAPI app + Mangum handler
├── config.py            # Settings (pydantic-settings, env vars)
├── database.py          # Async engine, session factory, Base
├── migrate.py           # Lambda handler for DB migrations
├── models/
│   ├── user.py
│   ├── folder.py        # Self-referential FK for nested folders
│   └── file.py
├── schemas/
│   ├── user.py
│   ├── folder.py
│   └── file.py
├── services/
│   ├── auth.py          # Argon2 hashing, JWT creation, get_current_user
│   ├── user.py          # create_user, get_user_by_email
│   ├── folder.py        # CRUD + check_if_parent
│   ├── storage.py       # S3 upload/download/delete (LocalStack vs AWS)
│   └── file.py          # CRUD functions
└── routers/
    ├── auth.py          # /auth/register, /auth/login
    ├── folder.py        # /folders CRUD
    └── file.py          # /files CRUD + download
```

---

## API Endpoints

### Auth

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and receive JWT token | No |

### Folders

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/folders/` | Create a folder | Yes |
| GET | `/folders/` | List folders (optional `?parent_id=`) | Yes |
| GET | `/folders/{id}` | Get folder by ID | Yes |
| DELETE | `/folders/{id}` | Delete folder (blocked if has subfolders) | Yes |

### Files

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/files/` | Upload a file (optional `?folder_id=`) | Yes |
| GET | `/files/` | List files (optional `?folder_id=`) | Yes |
| GET | `/files/{id}` | Get file metadata by ID | Yes |
| GET | `/files/{id}/download` | Download file content from S3 | Yes |
| DELETE | `/files/{id}` | Delete file from S3 and database | Yes |

> All protected endpoints require `Authorization: Bearer <token>` header.

---

## Local Development Setup

### Prerequisites

- Python 3.13
- Podman + podman-compose (or Docker + docker-compose)
- AWS CLI (for LocalStack bucket setup)

### 1. Clone and install dependencies

```bash
git clone git@github.com:giorgi-123/docvault.git
cd docvault
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Create `.env` file

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=docvaultDB
```

> App settings (bucket name, JWT secret, etc.) use defaults from `config.py` for local dev.

### 3. Start containers

```bash
podman-compose up -d
```

This starts:
- `docvault-db` — PostgreSQL on port `5433`
- `docvault-db-test` — PostgreSQL test DB on port `5435`
- `docvault-localstack` — LocalStack S3 on port `4566`

### 4. Create S3 bucket in LocalStack

> Required after every container restart — LocalStack does not persist state.

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://demo-bucket
```

### 5. Run migrations

```bash
alembic upgrade head
```

### 6. Start the server

```bash
uvicorn docvault.main:app --reload --port 8001
```

API is available at `http://localhost:8001`
Swagger UI at `http://localhost:8001/docs`

---

## Testing

```bash
pytest tests/
```

Tests use a real PostgreSQL test database and real LocalStack S3. Make sure all containers are running and the S3 bucket exists before running file tests.

### Test structure

| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_auth.py` | 8 | Registration (5) + Login (3) |
| `tests/test_folder.py` | 9 | CRUD + subfolder + blocked delete + auth checks |
| `tests/test_file.py` | 8 | Upload, upload to folder, list, get, download, delete, unauthenticated |

Each test runs against a fresh database — tables are created and dropped per test function.

---

## AWS Deployment

### Prerequisites

- AWS CLI configured (`aws configure`)
- SAM CLI installed (`pip install aws-sam-cli`)
- An AWS account

### 1. Create the JWT secret in Secrets Manager

```bash
aws secretsmanager create-secret \
  --name docvault-secret-dev \
  --secret-string '{"secret_key": "your-secret-key-here"}'
```

### 2. Build

```bash
sam build
```

### 3. Deploy

```bash
sam deploy --guided
```

You will be prompted for:
- **Stack name** — e.g. `docvault-dev`
- **AWS Region**
- **DBPassword** — minimum 8 characters
- **Environment** — `dev` or `prod`

Subsequent deploys:

```bash
sam deploy
```

### 4. Run migrations

After the first deploy, invoke the migration Lambda to create database tables:

```bash
aws lambda invoke \
  --function-name docvault-migrate-dev \
  --payload '{}' \
  response.json
```

### 5. Cleanup

```bash
sam delete
```

---

## Architecture

### Local Development

```
┌─────────────────────────────────────┐
│           Local Machine             │
│                                     │
│  ┌──────────┐     ┌──────────────┐  │
│  │  FastAPI  │────▶│  PostgreSQL  │  │
│  │ :8001    │     │  :5433       │  │
│  └──────────┘     └──────────────┘  │
│       │                             │
│       ▼                             │
│  ┌──────────┐                       │
│  │LocalStack│  (S3 emulator)        │
│  │  :4566   │                       │
│  └──────────┘                       │
└─────────────────────────────────────┘
```

### AWS Architecture

```
                    ┌─────────────────────────────────────────┐
                    │                  VPC                     │
                    │                                          │
Internet ──▶ API Gateway ──▶ ┌─────────────┐                 │
                    │        │   Lambda    │                  │
                    │        │  (FastAPI + │                  │
                    │        │   Mangum)   │                  │
                    │        └──────┬──────┘                  │
                    │               │                          │
                    │        ┌──────┴──────┐                  │
                    │        │             │                   │
                    │   ┌────▼────┐  ┌─────▼──────┐          │
                    │   │   RDS   │  │  S3 Bucket │◀─────────┤
                    │   │Postgres │  │  (via VPC  │  Gateway  │
                    │   │   17    │  │  Endpoint) │  Endpoint │
                    │   └─────────┘  └────────────┘          │
                    │                                          │
                    │        ┌─────────────┐                  │
                    │        │  Migration  │                  │
                    │        │   Lambda    │                  │
                    │        └─────────────┘                  │
                    └─────────────────────────────────────────┘

         Secrets Manager ──▶ Lambda (JWT secret at runtime)
```

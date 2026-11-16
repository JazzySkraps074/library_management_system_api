# Library Management System API

This repository contains the Library API for managing Books and Members. Assignment 3 adds automated tests, OpenAPI conformance checks, and classroom Bearer-token access control while keeping the PostgreSQL and in-memory storage options.

## Assignment 3 scope

Both classroom roles can read Books and Members. Only the administrator role can create, replace, or delete records. The root, health, and API documentation endpoints remain public. The fixed classroom tokens demonstrate authentication and authorization; this project does not add a user database, password login, OAuth, JWT issuance, or migrations.

The application follows a layered structure:

- **Routers** handle HTTP requests, response codes, and client-visible errors.
- **Services** apply Library rules and define transaction boundaries.
- **Repositories** perform database operations.
- **ORM models** map Books and Members to PostgreSQL tables.
- **Pydantic schemas** validate API input and describe responses.

The Book and Member services each have database-backed and in-memory implementations behind a shared service contract. Startup chooses a pair of implementations, and FastAPI dependencies provide them to the routers. For details, see [Software Development Principles](docs/software-development-principles.md).

## Setup

### Prerequisites

- Python 3.11 or newer
- `uv`
- Docker Desktop or another Docker-compatible engine for Testcontainers
- PostgreSQL for the database-backed application

Clone the repository and switch to the required branch:

```bash
git clone https://github.com/JazzySkraps074/library_management_system_api.git
cd library_management_system_api
git switch assignment-3
```

Install the dependencies recorded in `uv.lock`:

```bash
uv sync --dev
```

`uv` reads `.python-version`, creates the project environment, and installs the application and development dependencies.

## Configuration

Copy the sample environment file before running the API:

```bash
cp .env.example .env
```

In PowerShell, use `Copy-Item .env.example .env`.

The example file includes these settings:

| Setting | Purpose | Example |
|---|---|---|
| `STORAGE_BACKEND` | Select `database` or `memory` | `database` |
| `DATABASE_URL` | PostgreSQL connection URL; required for database storage | `postgresql+psycopg://postgres:postgres@localhost:5432/library` |
| `DATABASE_ECHO_SQL` | Print SQL statements to the server terminal | `false` |
| `DEMO_MEMBER_TOKEN` | Classroom token for read access | `member-demo-token` |
| `DEMO_ADMIN_TOKEN` | Classroom token for read and write access | `admin-demo-token` |

The demonstration tokens and database credentials are for local coursework only. `.env` is excluded by `.gitignore`; do not commit it or put passwords in the repository.

`database` is the default backend and persists data in PostgreSQL. Create a local database named `library` and set its connection details in `.env`. The application creates the `members` and `books` tables at startup. Set `STORAGE_BACKEND=memory` to try the API without PostgreSQL; memory data is cleared when the application stops.

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

The development server is available at `http://localhost:8000`:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- OpenAPI JSON: <http://localhost:8000/openapi.json>
- Health check: <http://localhost:8000/health>

The documentation endpoints are public. In Swagger UI, choose **Authorize** and enter one of the classroom tokens. The member token can call protected `GET` operations. The administrator token can call all protected operations.

Example requests:

```bash
curl -H "Authorization: Bearer member-demo-token" http://localhost:8000/books
```

```bash
curl -X POST http://localhost:8000/members \
  -H "Authorization: Bearer admin-demo-token" \
  -H "Content-Type: application/json" \
  -d '{"name":"Pat Example","email":"pat@example.com","membership_id":"1","phone":"1234567890"}'
```

## Explore the API

| Method | Path | Operation | Successful status |
|---|---|---|---|
| `GET` | `/` | API introduction (public) | `200` |
| `GET` | `/health` | Health check (public) | `200` |
| `GET` | `/books` | List Books | `200` |
| `GET` | `/books/{book_id}` | Get one Book | `200` |
| `POST` | `/books` | Create a Book (admin) | `201` |
| `PUT` | `/books/{book_id}` | Replace a Book (admin) | `200` |
| `DELETE` | `/books/{book_id}` | Delete a Book (admin) | `204` |
| `GET` | `/members` | List Members | `200` |
| `GET` | `/members/{member_id}` | Get one Member | `200` |
| `POST` | `/members` | Create a Member (admin) | `201` |
| `PUT` | `/members/{member_id}` | Replace a Member (admin) | `200` |
| `DELETE` | `/members/{member_id}` | Delete a Member (admin) | `204` |
| `GET` | `/members/{member_id}/books` | List a Member's Books | `200` |

Book requests require a title (1–200 characters), author (1–120), ISBN (1–13), published year (1450–2026), and positive `member_id`. Member requests require a name (1–120), a valid email, a one-character membership ID, and a ten-digit phone number. Surrounding whitespace is removed; unknown JSON fields are rejected.

An invalid or missing token returns `401 Unauthorized` with a Bearer challenge. A member token on a write returns `403 Forbidden`. Validation errors return `422`, missing records return `404`, and duplicate identifiers, nonexistent Member references, or blocked Member deletion return `409` where documented.

## Request flow

```text
HTTP request
    ↓
Authentication and role check
    ↓
Router and Pydantic schema
    ↓
Book or Member service contract
    ├── Database service → Repository → PostgreSQL
    └── In-memory service → Shared InMemoryStore
```

The router receives the selected service through FastAPI dependency injection. Database services receive a session factory, create one SQLAlchemy Session for each operation, and use a transaction context for writes. In-memory services share one application-scoped store protected by a lock. See [Authentication and Authorization](docs/authentication-and-authorization.md) and [Unit and Integration Testing](docs/testing-unit-integration.md).

## Run automated tests

Start Docker before running database integration or conformance tests. Testcontainers starts disposable PostgreSQL for the test run. The tests never use the developer's local Library database. Unit tests and in-memory route tests do not need Docker.

```bash
uv run pytest
```

Run one test level at a time:

```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest tests/conformance
```

The fixture organization keeps the boundaries clear:

- Unit tests check schemas, authentication dependencies, and service rules. Database service tests use repository and session test doubles.
- Repository integration tests use real SQLAlchemy mappings and temporary PostgreSQL.
- Router integration tests use FastAPI `TestClient` with both PostgreSQL and in-memory services.
- Conformance tests validate `/openapi.json`, exercise safe operations with Schemathesis, and check invalid and rejected HTTP requests.

For details, read [Unit and Integration Testing](docs/testing-unit-integration.md) and [Conformance and Contract Testing](docs/testing-conformance-contract.md).

## Project structure

```text
library_management_system_api/
├── app/
│   ├── auth/
│   │   ├── dependencies.py
│   │   └── users.py
│   ├── database/
│   │   └── session.py
│   ├── models/
│   │   ├── base.py
│   │   ├── book.py
│   │   └── member.py
│   ├── repositories/
│   │   ├── books.py
│   │   └── members.py
│   ├── routers/
│   │   ├── books.py
│   │   ├── http_errors.py
│   │   └── members.py
│   ├── schemas/
│   │   ├── books.py
│   │   └── members.py
│   ├── services/
│   │   ├── books/
│   │   │   ├── base.py
│   │   │   ├── database.py
│   │   │   └── in_memory.py
│   │   ├── members/
│   │   │   ├── base.py
│   │   │   ├── database.py
│   │   │   └── in_memory.py
│   │   └── in_memory_store.py
│   ├── config.py
│   ├── dependencies.py
│   ├── exceptions.py
│   └── main.py
├── docs/
│   ├── authentication-and-authorization.md
│   ├── software-development-principles.md
│   ├── testing-conformance-contract.md
│   └── testing-unit-integration.md
├── tests/
│   ├── conformance/
│   │   ├── test_negative_requests.py
│   │   ├── test_openapi_contract.py
│   │   └── test_schemathesis.py
│   ├── integration/
│   │   ├── test_authentication_authorization_api.py
│   │   ├── repositories/
│   │   │   ├── test_books.py
│   │   │   └── test_members.py
│   │   └── routers/
│   │       ├── database/
│   │       │   ├── test_books.py
│   │       │   └── test_members.py
│   │       └── memory/
│   │           ├── test_books.py
│   │           └── test_members.py
│   ├── unit/
│   │   ├── auth/
│   │   │   └── test_dependencies.py
│   │   ├── schemas/
│   │   │   ├── test_books.py
│   │   │   └── test_members.py
│   │   └── services/
│   │       ├── books/
│   │       │   ├── test_database.py
│   │       │   └── test_in_memory.py
│   │       └── members/
│   │           ├── test_database.py
│   │           └── test_in_memory.py
│   └── conftest.py
├── .env.example
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

# Library Management System API
This project is an API system for managing the books and members of a library. It allows clients to create, retrieve, update, and delete book and member records.

A single member can check out multiple books, but the member cannot be deleted while they have books checked out.

## Project Scope
- Routers handle HTTP requests and responses.
- Services contain business rules and coordinate operations.
- Repositories perform database operations.
- ORM models map Python classes to PostgreSQL tables.
- Pydantic schemas validate API request and response data.

## Clone the project
```text
git clone https://github.com/JazzySkraps074/library_management_system_api.git
cd library_management_system_api
git switch assignment-2
```

## Installation
From the ```library_management_system_api``` folder, run:
```bash
uv sync
```
```uv``` installs the required Python version when necessary, creates the project's virtual environment, and installs the dependencies recorded in ```uv.lock```.

## Running the API
Before starting the API, copy the sample environment file:
```bash
cp .env.example .env
```

The local connection uses the database user account and password created by the database setup script:
```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/library
```

To see SQLAlchemy-generated SQL in the development-server terminal, set this value in .env:
```bash
DATABASE_ECHO_SQL=true
```
Leave it set to false when SQL logging is not needed.

Run the following command:
```bash
uv run uvicorn app.main:app --reload
```
- FastAPI defines routes and handles API requests.
- Uvicorn listens for HTTP connections and passes requests to FastAPI.
- uv manages the Python environment and runs the installed command.
- --reload restarts the development server after source-code changes.
- Settings reads and validates .env and environment variables when the application starts.

The development server is available at http://localhost:8000. On startup, the application creates the members and books tables when they do not exist.

After the first successful startup, confirm that the members and books tables were created in library.

From a terminal, run:
```bash
psql -h localhost -U postgres -d library -W -c '\dt'
```
On Windows PowerShell, if PostgreSQL has not yet been added to `PATH`, run:
```bash
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -U postgres -d library -W -c "\dt"
```

Enter the local password, postgres, when prompted. The result should list the projects and tasks tables in the public schema.

You can also use pgAdmin 4, a PostgreSQL GUI client (already installed by the Windows installer; macOS users may install it separately).

In pgAdmin 4:

- Host: `localhost`
- Port: `5432`
- Username: `postgres`
- Password: `postgres`
- Database: `library`

Then open Schemas → public → Tables to inspect the tables.

## Explore the API
Below are three views of the same API contract
- ```http://localhost:8000/docs``` — Swagger UI for exploring and calling endpoints
- ```http://localhost:8000/redoc``` — ReDoc for reading reference documentation
- ```http://localhost:8000/openapi.json``` — the machine-readable OpenAPI document

| Method | URL | CRUD operation | Successful status |
|---|---|---|---|
| `GET` | `/` | Read API introduction | `200 OK` |
| `GET` | `/health` | Read API health | `200 OK` |
| `GET` | `/member` | Read all Members | `200 OK` |
| `GET` | `/member/{member_id}` | Read one Member | `200 OK` |
| `POST` | `/member` | Create a Member | `201 Created` |
| `PUT` | `/member/{member_id}` | Update a Member | `200 OK` |
| `DELETE` | `/member/{member_id}` | Delete a Member | `204 No Content` |
| `GET` | `/member/{member_id}/books` | Read one Member's Books | `200 OK` |
| `GET` | `/book` | Read all Books | `200 OK` |
| `GET` | `/book/{book_id}` | Read one Book | `200 OK` |
| `POST` | `/book` | Create a Book | `201 Created` |
| `PUT` | `/book/{book_id}` | Update a Book | `200 OK` |
| `DELETE` | `/book/{book_id}` | Delete a Book | `204 No Content` |

Use this JSON body with Member ```POST``` or ```PUT``` requests:
```JSON
{
  "name": "John Smith",
  "email": "jsmith123@example.com",
  "membership_id": "1",
  "phone": "1234567890"
}
```
Member validation rules include:
- `name` is required and must contain 1-120 characters.
- `email` is required, must be unique, and it must be in a valid email format.
- `membership_id` is required and must be unique.
- `phone` is required.

Use this JSON body with Book ```POST``` or ```PUT``` requests:
```JSON
{
  "title": "Example Book",
  "author": "Jane Smith",
  "isbn": "1234567890123",
  "published_year": 1990,
  "member_id": 1
}
```
Book validation rules include:
- `title` is required and must contain 1-200 characters.
- `author` is required and must contain 1-120 characters.
- `isbn` is required and must be unique.
- `published_year` is required and must be between 1450 and 2026.
- `member_id` is required, and identifies the existing Member who borrowed the Book.

## Current project structure
```text
library_management_system_api/
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── book.py
│   │   └── member.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── __init__.py
│   ├── config.py
│   ├── exceptions.py
│   ├── main.py
│   └── storage.py
└── .env
└── .env.example
└── .gitignore
└── pyproject.toml
└── README.md
└── uv.lock
```

# Library Management System API
This project is an API system for managing the books and members of a library. It allows clients to create, retrieve, update, and delete book and member records.

A single member can check out multiple books, but the member cannot be deleted while they have books checked out.

## Clone the project
```text
git clone https://github.com/JazzySkraps074/library_management_system_api.git
cd library_management_system_api
git switch assignment-1
```

## Installation
From the ```library_management_system_api``` folder, run:
```bash
uv sync
```
```uv``` installs the required Python version when necessary, creates the project's virtual environment, and installs the dependencies recorded in ```uv.lock```.

## Running the API
Run the following command:
```bash
uv run uvicorn app.main:app --reload
```

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
  "name": "John Smith"
  "email": "jsmith123@example.com"
  "membership_id": "1"
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
  "title": "Example Book"
  "author": "Jane Smith"
  "isbn": "1234567890123"
  "published_year": "1990"
  "member-id": 1
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
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── books.py
│   │   └── members.py
│   ├── __init__.py
│   ├── main.py
│   ├── pyproject.toml
│   ├── schemas.py
│   └── storage.py
└── .gitignore
└── README.md
```

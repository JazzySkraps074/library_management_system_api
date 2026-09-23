# Library Management System API
This project is an API system for managing the books and members of a library. It allows clients to create, retrieve, update, and delete book and member records.

A single Member can check out multiple books, but the member cannot be deleted while they have books checked out.

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
Below are three views 
- ```http://localhost/docs``` — Swagger UI for exploring and calling endpoints
- ```http://localhost/redoc``` — ReDoc for reading reference documentation
- ```http://localhost/openapi.json``` — the machine-readable OpenAPI document

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
| `GET` | `/member/{member_id}` | Read one Book | `200 OK` |
| `POST` | `/member` | Create a Book | `201 Created` |
| `PUT` | `/member/{member_id}` | Update a Book | `200 OK` |
| `DELETE` | `/member/{member_id}` | Delete a Book | `204 No Content` |

## Current project structure

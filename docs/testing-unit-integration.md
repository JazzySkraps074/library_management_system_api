# Unit and Integration Testing

## Unit tests

Unit tests live under `tests/unit`, organized by the application layer they exercise. Schema tests validate Pydantic rules directly. Authentication tests call the identity and role dependencies. Service tests exercise both in-memory implementations and database service decisions.

Database service unit tests replace repositories and the session factory with test doubles. They can check business decisions and transaction outcomes without PostgreSQL.

## Integration tests

Integration tests live under `tests/integration`:

- `repositories` exercises real SQLAlchemy mappings, generated identifiers, unique constraints, and the Member foreign key.
- `routers/database` sends HTTP requests through FastAPI and the database services.
- `routers/memory` sends HTTP requests through the same routers and the in-memory services.
- `test_authentication_authorization_api.py` checks public endpoints, token failures, protected reads, denied writes, and administrator writes.

Repository and database API tests share the `database_client`, `db_session`, and `reset_database` fixtures from `tests/conftest.py`. Testcontainers starts a disposable PostgreSQL container for the pytest session. Each test resets the tables, and the fixture removes the container when the suite finishes. These tests do not use the developer's local Library database.

## Run commands

```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest
```

Docker must be running for repository and PostgreSQL API integration tests. Unit tests and in-memory API tests do not require Docker.

# Software Development Principles

## Application layers

- **Routers** define HTTP paths, status codes, request and response schemas, and map application errors to HTTP responses.
- **Services** implement Book and Member use cases, including relationship checks and transaction boundaries.
- **Repositories** issue SQLAlchemy queries and persistence operations.
- **Models** map Books and Members to PostgreSQL tables.
- **Schemas** validate incoming JSON and describe the public response contract.
- **Dependencies** expose the settings and startup-selected services to the routers.

The service contracts keep route behavior independent of storage. `DatabaseBookService` and `InMemoryBookService` implement the same Book contract; the Member services follow the same pattern. Application startup selects one implementation for each resource, so route handlers do not create repositories or choose a backend.

## Database transactions

Database services receive a SQLAlchemy session factory rather than a shared Session. Each read opens and closes its own Session. Each write uses `session_factory.begin()`, which commits when the operation succeeds and rolls back when an exception escapes. Repositories remain focused on SQL operations, while services decide which operations belong in one transaction.

## In-memory state

One application-scoped `InMemoryStore` is shared by both in-memory services. An `RLock` protects compound changes such as ID generation, relationship checks, and list updates. The memory backend is process-local and loses its data when the API stops.

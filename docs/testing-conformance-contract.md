# Conformance and Contract Testing

## OpenAPI validation

`tests/conformance/test_openapi_contract.py` requests the generated `/openapi.json`, validates it with `openapi-spec-validator`, and checks representative paths, methods, schemas, security requirements, and response statuses.

## Generated safe-operation checks

`tests/conformance/test_schemathesis.py` loads the FastAPI application as an ASGI application and filters Schemathesis generation to the protected `GET /books` and `GET /members` collection operations. It supplies the configured member token and validates responses against the published schema. The generated checks use in-memory storage and never target the developer's database.

## Negative requests

`tests/conformance/test_negative_requests.py` uses the database-backed API fixture to check invalid request bodies, unknown fields, field boundaries, invalid path identifiers, missing resources, nonexistent Member references, duplicate values, and blocked Member deletion. It checks validation response shape and verifies rejected writes leave existing data available.

Run the conformance suite with:

```bash
uv run pytest tests/conformance
```

The API fixture uses Testcontainers PostgreSQL. Start Docker before running it.

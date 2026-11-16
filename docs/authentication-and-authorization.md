# Authentication and Authorization

## Classroom identities

The API has two predefined request identities: `member` and `admin`. Their Bearer tokens come from `DEMO_MEMBER_TOKEN` and `DEMO_ADMIN_TOKEN`. These request identities are separate from Member records stored in the Library.

Both roles can read Books and Members. Only `admin` can create, replace, or delete resources. The root, health, Swagger UI, ReDoc, and OpenAPI document remain public.

## Request flow

```text
Authorization header
  -> HTTPBearer parses the scheme and credentials
  -> get_current_user maps a configured token to a demo identity
  -> require_admin checks the role for write operations
  -> route calls the injected Book or Member service
```

A missing, malformed, or unknown token receives `401 Unauthorized` with `WWW-Authenticate: Bearer`. A valid member token on a write operation receives `403 Forbidden`. Authentication and role checks stay in reusable FastAPI dependencies; services do not receive HTTP credentials.

## OpenAPI

`HTTPBearer` publishes the `BearerAuthentication` security scheme. Every Book and Member operation declares that security requirement and documents its `401` response. Write operations also document `403`, so Swagger UI displays its Authorize control and the role boundary is visible to API clients.

## Scope

The tokens are fixed, configurable classroom values. This milestone does not implement a user database, password login, OAuth, JWT issuance, refresh tokens, or token revocation. Replace the demonstration values and add a production identity provider before deploying outside a classroom environment.

"""Schemathesis response-contract checks for safe collection operations."""

import os

import pytest
import schemathesis

from app.main import app


@pytest.fixture(scope="module")
def safe_api_schema():
    previous_backend = os.environ.get("STORAGE_BACKEND")
    previous_url = os.environ.pop("DATABASE_URL", None)
    previous_member_token = os.environ.get("DEMO_MEMBER_TOKEN")
    previous_admin_token = os.environ.get("DEMO_ADMIN_TOKEN")
    os.environ["STORAGE_BACKEND"] = "memory"
    os.environ["DEMO_MEMBER_TOKEN"] = "member-demo-token"
    os.environ["DEMO_ADMIN_TOKEN"] = "admin-demo-token"
    schema = schemathesis.openapi.from_asgi("/openapi.json", app).include(
        method="GET", path_regex=r"^/(books|members)$"
    )
    yield schema
    if previous_backend is None:
        os.environ.pop("STORAGE_BACKEND", None)
    else:
        os.environ["STORAGE_BACKEND"] = previous_backend
    if previous_url is not None:
        os.environ["DATABASE_URL"] = previous_url
    if previous_member_token is None:
        os.environ.pop("DEMO_MEMBER_TOKEN", None)
    else:
        os.environ["DEMO_MEMBER_TOKEN"] = previous_member_token
    if previous_admin_token is None:
        os.environ.pop("DEMO_ADMIN_TOKEN", None)
    else:
        os.environ["DEMO_ADMIN_TOKEN"] = previous_admin_token


schema = schemathesis.pytest.from_fixture("safe_api_schema")


@schema.parametrize()
def test_safe_list_operations_follow_openapi(case):
    case.call_and_validate(headers={"Authorization": "Bearer member-demo-token"})

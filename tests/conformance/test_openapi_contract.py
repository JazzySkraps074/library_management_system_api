from openapi_spec_validator import validate_spec
from starlette.testclient import TestClient


def test_generated_openapi_document_is_valid_and_describes_operations_and_security(
    database_client: TestClient,
):
    spec = database_client.get("/openapi.json").json()
    validate_spec(spec)
    security = spec["components"]["securitySchemes"]["BearerAuthentication"]
    assert security["type"] == "http"
    assert security["scheme"] == "bearer"
    expected_methods = {
        "/books": {"get", "post"},
        "/books/{book_id}": {"get", "put", "delete"},
        "/members": {"get", "post"},
        "/members/{member_id}": {"get", "put", "delete"},
        "/members/{member_id}/books": {"get"},
    }
    for path, methods in expected_methods.items():
        assert set(spec["paths"][path]) == methods
        for method, operation in spec["paths"][path].items():
            assert operation.get("security") == [{"BearerAuthentication": []}]
            assert "401" in operation["responses"]
    book_create = spec["paths"]["/books"]["post"]
    assert book_create["requestBody"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("/BookCreate")
    assert (
        "BookResponse"
        in book_create["responses"]["201"]["content"]["application/json"]["schema"][
            "$ref"
        ]
    )
    assert {"201", "401", "403", "404", "409", "422"} <= set(book_create["responses"])
    member_create = spec["paths"]["/members"]["post"]
    assert member_create["requestBody"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("/MemberCreate")
    assert {"201", "401", "403", "409", "422"} <= set(member_create["responses"])
    member_response = spec["paths"]["/members"]["get"]["responses"]["200"]
    assert (
        "MemberResponse"
        in member_response["content"]["application/json"]["schema"]["items"]["$ref"]
    )
    book_response = spec["paths"]["/books"]["get"]["responses"]["200"]
    assert (
        "BookResponse"
        in book_response["content"]["application/json"]["schema"]["items"]["$ref"]
    )
    assert "409" in spec["paths"]["/members/{member_id}"]["delete"]["responses"]
    assert "HTTPValidationError" in spec["components"]["schemas"]


def test_public_routes_have_no_security_requirement(database_client: TestClient):
    spec = database_client.get("/openapi.json").json()
    assert "security" not in spec["paths"]["/"]["get"]
    assert "security" not in spec["paths"]["/health"]["get"]

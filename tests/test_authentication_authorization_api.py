"""HTTP integration tests for classroom authentication and authorization."""

import pytest
from starlette.testclient import TestClient


def test_root_health_and_api_documentation_remain_public(
    database_client: TestClient,
) -> None:
    for path in ("/", "/health", "/docs", "/redoc", "/openapi.json"):
        assert database_client.get(path).status_code == 200


@pytest.mark.parametrize(
    "authorization", [None, "Bearer unknown-token", "Basic member-demo-token"]
)
def test_protected_reads_reject_missing_malformed_and_unknown_tokens(
    database_client: TestClient, authorization: str | None
) -> None:
    headers = {} if authorization is None else {"Authorization": authorization}
    response = database_client.get("/books", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid Bearer token"}
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("path", ["/books", "/members"])
def test_member_role_can_read_protected_collections(
    database_client: TestClient, member_headers: dict[str, str], path: str
) -> None:
    response = database_client.get(path, headers=member_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        (
            "POST",
            "/members",
            {
                "name": "Other",
                "email": "other@example.com",
                "membership_id": "2",
                "phone": "1234567890",
            },
        ),
        (
            "PUT",
            "/members/1",
            {
                "name": "Changed",
                "email": "pat@example.com",
                "membership_id": "1",
                "phone": "1234567890",
            },
        ),
        ("DELETE", "/members/1", None),
        (
            "POST",
            "/books",
            {
                "title": "Other",
                "author": "Writer",
                "isbn": "2",
                "published_year": 2000,
                "member_id": 1,
            },
        ),
        (
            "PUT",
            "/books/1",
            {
                "title": "Changed",
                "author": "Writer",
                "isbn": "1",
                "published_year": 2000,
                "member_id": 1,
            },
        ),
        ("DELETE", "/books/1", None),
    ],
)
def test_member_write_denial_does_not_change_library_data(
    database_client: TestClient,
    member_headers: dict[str, str],
    admin_headers: dict[str, str],
    method: str,
    path: str,
    payload: dict | None,
) -> None:
    member = database_client.post(
        "/members",
        json={
            "name": "Pat",
            "email": "pat@example.com",
            "membership_id": "1",
            "phone": "1234567890",
        },
        headers=admin_headers,
    ).json()
    book = database_client.post(
        "/books",
        json={
            "title": "Book",
            "author": "Writer",
            "isbn": "1",
            "published_year": 2000,
            "member_id": member["id"],
        },
        headers=admin_headers,
    ).json()
    response = database_client.request(
        method, path, json=payload, headers=member_headers
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Administrator role required"}
    assert database_client.get("/members", headers=admin_headers).json() == [member]
    assert database_client.get("/books", headers=admin_headers).json() == [book]


def test_administrator_token_can_create_and_remove_a_member(
    database_client: TestClient, admin_headers: dict[str, str]
) -> None:
    response = database_client.post(
        "/members",
        json={
            "name": "Pat",
            "email": "pat@example.com",
            "membership_id": "1",
            "phone": "1234567890",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    assert (
        database_client.delete(
            f"/members/{response.json()['id']}", headers=admin_headers
        ).status_code
        == 204
    )

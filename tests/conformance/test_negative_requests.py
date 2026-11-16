"""Client-visible validation and business-rule rejection tests."""

import pytest
from starlette.testclient import TestClient


def assert_validation_error(response) -> None:
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
    assert response.json()["detail"]


def member_payload(**updates):
    return {
        "name": "Pat",
        "email": "pat@example.com",
        "membership_id": "1",
        "phone": "1234567890",
        **updates,
    }


def book_payload(**updates):
    return {
        "title": "Book",
        "author": "Writer",
        "isbn": "12345",
        "published_year": 2000,
        "member_id": 1,
        **updates,
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Pat"},
        {**member_payload(), "unexpected": True},
        member_payload(email="bad-email"),
        member_payload(phone="123456789x"),
        member_payload(name=" "),
    ],
)
def test_member_body_validation_returns_documented_422(
    database_client: TestClient, admin_headers: dict[str, str], payload: dict
) -> None:
    assert_validation_error(
        database_client.post("/members", json=payload, headers=admin_headers)
    )


def test_book_body_validation_rejects_unknown_fields_and_year_boundaries(
    database_client: TestClient, admin_headers: dict[str, str]
) -> None:
    assert_validation_error(
        database_client.post(
            "/books", json={**book_payload(), "unknown": 1}, headers=admin_headers
        )
    )
    assert_validation_error(
        database_client.post(
            "/books", json=book_payload(published_year=1449), headers=admin_headers
        )
    )
    assert_validation_error(
        database_client.post(
            "/books", json=book_payload(published_year=2027), headers=admin_headers
        )
    )


def test_path_id_type_returns_documented_validation_error(
    database_client: TestClient, member_headers: dict[str, str]
) -> None:
    response = database_client.get("/books/not-an-integer", headers=member_headers)
    assert_validation_error(response)
    assert response.json()["detail"][0]["type"] == "int_parsing"


def test_missing_book_and_member_return_404(
    database_client: TestClient, member_headers: dict[str, str]
) -> None:
    assert database_client.get("/books/999", headers=member_headers).status_code == 404
    assert (
        database_client.get("/members/999", headers=member_headers).status_code == 404
    )


def test_book_referencing_missing_member_returns_404_without_inserting(
    database_client: TestClient,
    admin_headers: dict[str, str],
    member_headers: dict[str, str],
) -> None:
    response = database_client.post(
        "/books", json=book_payload(member_id=999), headers=admin_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"
    assert database_client.get("/books", headers=member_headers).json() == []


def test_duplicate_email_membership_id_and_isbn_return_409_without_corrupting_data(
    database_client: TestClient,
    admin_headers: dict[str, str],
    member_headers: dict[str, str],
) -> None:
    created_member = database_client.post(
        "/members", json=member_payload(), headers=admin_headers
    )
    assert created_member.status_code == 201

    duplicate_email = database_client.post(
        "/members", json=member_payload(membership_id="2"), headers=admin_headers
    )
    duplicate_membership = database_client.post(
        "/members",
        json=member_payload(email="other@example.com"),
        headers=admin_headers,
    )
    assert duplicate_email.status_code == 409
    assert duplicate_membership.status_code == 409
    assert len(database_client.get("/members", headers=member_headers).json()) == 1

    created_book = database_client.post(
        "/books", json=book_payload(), headers=admin_headers
    )
    duplicate_book = database_client.post(
        "/books", json=book_payload(title="Copy"), headers=admin_headers
    )
    assert created_book.status_code == 201
    assert duplicate_book.status_code == 409
    assert len(database_client.get("/books", headers=member_headers).json()) == 1


def test_member_with_books_cannot_be_deleted_and_data_remains(
    database_client: TestClient,
    admin_headers: dict[str, str],
    member_headers: dict[str, str],
) -> None:
    member = database_client.post(
        "/members", json=member_payload(), headers=admin_headers
    ).json()
    book = database_client.post(
        "/books", json=book_payload(member_id=member["id"]), headers=admin_headers
    ).json()

    response = database_client.delete(f"/members/{member['id']}", headers=admin_headers)

    assert response.status_code == 409
    assert response.json()["detail"]
    assert (
        database_client.get(
            f"/members/{member['id']}", headers=member_headers
        ).status_code
        == 200
    )
    assert (
        database_client.get(f"/books/{book['id']}", headers=member_headers).status_code
        == 200
    )

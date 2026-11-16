"""PostgreSQL-backed HTTP integration tests for Books."""

from starlette.testclient import TestClient


def test_book_crud_and_member_relationship(
    database_client: TestClient,
    admin_headers: dict[str, str],
    member_headers: dict[str, str],
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
    payload = {
        "title": "Book",
        "author": "Writer",
        "isbn": "12345",
        "published_year": 2000,
        "member_id": member["id"],
    }
    created = database_client.post("/books", json=payload, headers=admin_headers)
    assert created.status_code == 201
    book = created.json()
    assert database_client.get("/books", headers=member_headers).json() == [book]
    assert (
        database_client.get(f"/books/{book['id']}", headers=member_headers).json()
        == book
    )
    assert database_client.get(
        f"/members/{member['id']}/books", headers=member_headers
    ).json() == [book]

    updated = database_client.put(
        f"/books/{book['id']}",
        json={**payload, "title": "Updated"},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated"
    assert (
        database_client.delete(
            f"/books/{book['id']}", headers=admin_headers
        ).status_code
        == 204
    )
    assert database_client.get("/books", headers=member_headers).json() == []

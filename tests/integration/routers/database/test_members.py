"""PostgreSQL-backed HTTP integration tests for Members."""

from starlette.testclient import TestClient


def test_member_crud_and_blocked_deletion(
    database_client: TestClient,
    admin_headers: dict[str, str],
    member_headers: dict[str, str],
) -> None:
    payload = {
        "name": "Pat",
        "email": "pat@example.com",
        "membership_id": "1",
        "phone": "1234567890",
    }
    created = database_client.post("/members", json=payload, headers=admin_headers)
    assert created.status_code == 201
    member = created.json()
    assert database_client.get("/members", headers=member_headers).json() == [member]
    assert (
        database_client.get(f"/members/{member['id']}", headers=member_headers).json()
        == member
    )
    book = database_client.post(
        "/books",
        json={
            "title": "Book",
            "author": "Writer",
            "isbn": "12345",
            "published_year": 2000,
            "member_id": member["id"],
        },
        headers=admin_headers,
    ).json()
    blocked = database_client.delete(f"/members/{member['id']}", headers=admin_headers)
    assert blocked.status_code == 409
    assert (
        database_client.get(f"/books/{book['id']}", headers=member_headers).status_code
        == 200
    )

    updated = database_client.put(
        f"/members/{member['id']}",
        json={**payload, "name": "Updated Pat"},
        headers=admin_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated Pat"
    assert (
        database_client.delete(
            f"/books/{book['id']}", headers=admin_headers
        ).status_code
        == 204
    )
    assert (
        database_client.delete(
            f"/members/{member['id']}", headers=admin_headers
        ).status_code
        == 204
    )

"""In-memory HTTP integration tests for Member routes."""

from starlette.testclient import TestClient


def test_memory_member_crud_and_blocked_deletion(
    memory_client: TestClient,
    admin_headers: dict[str, str],
    member_headers: dict[str, str],
) -> None:
    payload = {
        "name": "Pat",
        "email": "pat@example.com",
        "membership_id": "1",
        "phone": "1234567890",
    }
    created = memory_client.post("/members", json=payload, headers=admin_headers)
    assert created.status_code == 201
    member = created.json()
    assert memory_client.get("/members", headers=member_headers).json() == [member]
    book = memory_client.post(
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
    assert (
        memory_client.delete(
            f"/members/{member['id']}", headers=admin_headers
        ).status_code
        == 409
    )
    assert memory_client.get(
        f"/members/{member['id']}/books", headers=member_headers
    ).json() == [book]
    assert (
        memory_client.delete(f"/books/{book['id']}", headers=admin_headers).status_code
        == 204
    )
    assert (
        memory_client.delete(
            f"/members/{member['id']}", headers=admin_headers
        ).status_code
        == 204
    )

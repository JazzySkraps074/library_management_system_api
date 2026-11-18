"""Unit tests for Book request validation."""

import pytest
from pydantic import ValidationError

from app.schemas.books import BookCreate


def test_book_trims_whitespace_and_accepts_valid_boundaries():
    book = BookCreate(
        title="  A  ",
        author="B",
        isbn="1234567890123",
        published_year=1450,
        member_id=1,
    )
    assert book.title == "A"
    assert book.published_year == 1450
    upper = BookCreate(
        title="T" * 200, author="A" * 120, isbn="1", published_year=2026, member_id=1
    )
    assert len(upper.title) == 200


@pytest.mark.parametrize(
    "payload",
    [
        {"author": "Author", "isbn": "1", "published_year": 2000, "member_id": 1},
        {
            "title": " ",
            "author": "Author",
            "isbn": "1",
            "published_year": 2000,
            "member_id": 1,
        },
        {
            "title": "Book",
            "author": "Author",
            "isbn": "12345678901234",
            "published_year": 2000,
            "member_id": 1,
        },
        {
            "title": "T" * 201,
            "author": "Author",
            "isbn": "1",
            "published_year": 2000,
            "member_id": 1,
        },
        {
            "title": "Book",
            "author": "A" * 121,
            "isbn": "1",
            "published_year": 2000,
            "member_id": 1,
        },
        {
            "title": "Book",
            "author": "Author",
            "isbn": "1",
            "published_year": 1449,
            "member_id": 1,
        },
        {
            "title": "Book",
            "author": "Author",
            "isbn": "1",
            "published_year": 2027,
            "member_id": 1,
        },
        {
            "title": "Book",
            "author": "Author",
            "isbn": "1",
            "published_year": 2000,
            "member_id": 0,
        },
        {
            "title": "Book",
            "author": "Author",
            "isbn": "1",
            "published_year": 2000,
            "member_id": 1,
            "unexpected": True,
        },
    ],
)
def test_book_rejects_missing_invalid_boundaries_and_unknown_fields(payload):
    with pytest.raises(ValidationError):
        BookCreate.model_validate(payload)

"""Unit tests for the in-memory Book service."""

import pytest

from app.exceptions import BookNotFoundError, DuplicateRecordError, MemberNotFoundError
from app.schemas.books import BookCreate
from app.schemas.members import MemberCreate
from app.services.books import InMemoryBookService
from app.services.in_memory_store import InMemoryStore
from app.services.members import InMemoryMemberService


def test_book_service_checks_relationships_duplicates_and_missing_records():
    store = InMemoryStore()
    books, members = InMemoryBookService(store), InMemoryMemberService(store)
    book_data = BookCreate(
        title="Book", author="Writer", isbn="1", published_year=2000, member_id=1
    )
    with pytest.raises(MemberNotFoundError):
        books.create_book(book_data)
    member = members.create_member(
        MemberCreate(
            name="Pat", email="pat@example.com", membership_id="1", phone="1234567890"
        )
    )
    book = books.create_book(book_data)
    assert book.member_id == member.id
    assert books.list_books() == [book]
    with pytest.raises(DuplicateRecordError):
        books.create_book(
            BookCreate(
                title="Copy",
                author="Writer",
                isbn="1",
                published_year=2001,
                member_id=member.id,
            )
        )
    books.delete_book(book.id)
    with pytest.raises(BookNotFoundError):
        books.get_book(book.id)

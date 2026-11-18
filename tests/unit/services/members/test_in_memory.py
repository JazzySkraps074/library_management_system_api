"""Unit tests for the in-memory Member service."""

import pytest

from app.exceptions import MemberHasBooksError, MemberNotFoundError
from app.schemas.books import BookCreate
from app.schemas.members import MemberCreate
from app.services.books import InMemoryBookService
from app.services.in_memory_store import InMemoryStore
from app.services.members import InMemoryMemberService


def test_member_service_lists_related_books_and_blocks_deletion():
    store = InMemoryStore()
    books, members = InMemoryBookService(store), InMemoryMemberService(store)
    member = members.create_member(
        MemberCreate(
            name="Pat", email="pat@example.com", membership_id="1", phone="1234567890"
        )
    )
    book = books.create_book(
        BookCreate(
            title="Book",
            author="Writer",
            isbn="1",
            published_year=2000,
            member_id=member.id,
        )
    )
    assert members.list_member_books(member.id) == [book]
    with pytest.raises(MemberHasBooksError):
        members.delete_member(member.id)
    books.delete_book(book.id)
    members.delete_member(member.id)
    with pytest.raises(MemberNotFoundError):
        members.get_member(member.id)

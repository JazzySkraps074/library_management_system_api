"""Book repository integration tests against disposable PostgreSQL."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Book
from app.repositories.books import BookRepository
from app.repositories.members import MemberRepository
from app.schemas.books import BookCreate
from app.schemas.members import MemberCreate


def test_book_repository_generates_ids_and_reads_member_books(
    db_session: Session,
) -> None:
    member = MemberRepository(db_session).create(
        MemberCreate(
            name="Pat", email="pat@example.com", membership_id="1", phone="1234567890"
        )
    )
    db_session.commit()
    books = BookRepository(db_session)
    book = books.create(
        BookCreate(
            title="Book",
            author="Writer",
            isbn="12345",
            published_year=2000,
            member_id=member.id,
        )
    )
    db_session.commit()
    assert book.id > 0
    assert books.exists_for_member(member.id)
    assert books.list_by_member(member.id)[0].id == book.id


def test_postgres_enforces_book_isbn_uniqueness_and_member_foreign_key(
    db_session: Session,
) -> None:
    member = MemberRepository(db_session).create(
        MemberCreate(
            name="Pat", email="pat@example.com", membership_id="1", phone="1234567890"
        )
    )
    db_session.commit()
    books = BookRepository(db_session)
    books.create(
        BookCreate(
            title="First",
            author="Writer",
            isbn="777",
            published_year=2000,
            member_id=member.id,
        )
    )
    db_session.commit()
    with pytest.raises(IntegrityError):
        books.create(
            BookCreate(
                title="Duplicate",
                author="Writer",
                isbn="777",
                published_year=2001,
                member_id=member.id,
            )
        )
    db_session.rollback()
    with pytest.raises(IntegrityError):
        db_session.add(
            Book(
                title="Invalid",
                author="Writer",
                isbn="999",
                published_year=2000,
                member_id=99999,
            )
        )
        db_session.flush()
    db_session.rollback()

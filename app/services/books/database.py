"""PostgreSQL implementation of the Book use cases."""

from sqlalchemy.orm import Session, sessionmaker

from app.exceptions import BookNotFoundError, MemberNotFoundError
from app.models.book import Book
from app.repositories.books import BookRepository
from app.repositories.members import MemberRepository
from app.schemas.books import BookCreate, BookUpdate

from .base import BookService


class DatabaseBookService(BookService):
    def __init__(self, session_factory: sessionmaker[Session]):
        self._session_factory = session_factory

    def list_books(self) -> list[Book]:
        with self._session_factory() as session:
            return BookRepository(session).list_all()

    def get_book(self, book_id: int) -> Book:
        with self._session_factory() as session:
            book = BookRepository(session).get_by_id(book_id)
            if book is None:
                raise BookNotFoundError
            return book

    def create_book(self, data: BookCreate) -> Book:
        with self._session_factory.begin() as session:
            if MemberRepository(session).get_by_id(data.member_id) is None:
                raise MemberNotFoundError
            book = BookRepository(session).create(data)
            session.refresh(book)
            return book

    def replace_book(self, book_id: int, data: BookUpdate) -> Book:
        with self._session_factory.begin() as session:
            repository = BookRepository(session)
            book = repository.get_by_id(book_id)
            if book is None:
                raise BookNotFoundError
            if MemberRepository(session).get_by_id(data.member_id) is None:
                raise MemberNotFoundError
            updated = repository.replace(book, data)
            session.refresh(updated)
            return updated

    def delete_book(self, book_id: int) -> None:
        with self._session_factory.begin() as session:
            repository = BookRepository(session)
            book = repository.get_by_id(book_id)
            if book is None:
                raise BookNotFoundError
            repository.delete(book)

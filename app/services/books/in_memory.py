"""In-memory implementation of the Book use cases."""

from app.exceptions import BookNotFoundError, DuplicateRecordError, MemberNotFoundError
from app.models.book import Book
from app.schemas.books import BookCreate, BookUpdate
from app.services.in_memory_store import InMemoryStore

from .base import BookService


class InMemoryBookService(BookService):
    def __init__(self, store: InMemoryStore):
        self._store = store

    def list_books(self) -> list[Book]:
        with self._store.lock:
            return list(self._store.books)

    def get_book(self, book_id: int) -> Book:
        with self._store.lock:
            for book in self._store.books:
                if book.id == book_id:
                    return book
            raise BookNotFoundError

    def create_book(self, data: BookCreate) -> Book:
        with self._store.lock:
            if not any(member.id == data.member_id for member in self._store.members):
                raise MemberNotFoundError
            if any(book.isbn == data.isbn for book in self._store.books):
                raise DuplicateRecordError
            book = Book(
                id=max((item.id for item in self._store.books), default=0) + 1,
                **data.model_dump(),
            )
            self._store.books.append(book)
            return book

    def replace_book(self, book_id: int, data: BookUpdate) -> Book:
        with self._store.lock:
            book = self.get_book(book_id)
            if not any(member.id == data.member_id for member in self._store.members):
                raise MemberNotFoundError
            if any(
                item.id != book_id and item.isbn == data.isbn
                for item in self._store.books
            ):
                raise DuplicateRecordError
            for field, value in data.model_dump().items():
                setattr(book, field, value)
            return book

    def delete_book(self, book_id: int) -> None:
        with self._store.lock:
            self._store.books.remove(self.get_book(book_id))

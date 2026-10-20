"""Business operations for Books."""

from sqlalchemy.orm import Session

from app.exceptions import MemberNotFoundError, BookNotFoundError
from app.models.book import Book
from app.repositories.members import MemberRepository
from app.repositories.books import BookRepository
from app.schemas.books import BookCreate, BookUpdate


class BookService:
    """Coordinate Book rules, repositories, and transactions."""

    def __init__(self, session: Session):
        self.session = session
        self.member_repository = MemberRepository(session)
        self.book_repository = BookRepository(session)

    def _require_member(self, member_id: int) -> None:
        if self.member_repository.get_by_id(member_id) is None:
            raise MemberNotFoundError

    def list_books(self) -> list[Book]:
        return self.book_repository.list_all()

    def get_book(self, book_id: int) -> Book:
        book = self.book_repository.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError
        return book

    def create_book(self, data: BookCreate) -> Book:
        self._require_member(data.member_id)
        try:
            book = self.book_repository.create(data)
            self.session.commit()
            self.session.refresh(book)
            return book
        except Exception:
            self.session.rollback()
            raise

    def replace_book(self, book_id: int, data: BookUpdate) -> Book:
        book = self.get_book(book_id)
        self._require_member(data.member_id)
        try:
            updated_book = self.book_repository.replace(book, data)
            self.session.commit()
            self.session.refresh(updated_book)
            return updated_book
        except Exception:
            self.session.rollback()
            raise

    def delete_book(self, book_id: int) -> None:
        book = self.get_book(book_id)
        try:
            self.book_repository.delete(book)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

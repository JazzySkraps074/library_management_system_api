"""Abstract Book service contract shared by every storage backend."""

from abc import ABC, abstractmethod

from app.models.book import Book
from app.schemas.books import BookCreate, BookUpdate


class BookService(ABC):
    @abstractmethod
    def list_books(self) -> list[Book]:
        pass

    @abstractmethod
    def get_book(self, book_id: int) -> Book:
        pass

    @abstractmethod
    def create_book(self, data: BookCreate) -> Book:
        pass

    @abstractmethod
    def replace_book(self, book_id: int, data: BookUpdate) -> Book:
        pass

    @abstractmethod
    def delete_book(self, book_id: int) -> None:
        pass

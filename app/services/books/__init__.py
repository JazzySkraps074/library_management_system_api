"""Book service contract and backend implementations."""

from .base import BookService
from .database import DatabaseBookService
from .in_memory import InMemoryBookService

__all__ = ["BookService", "DatabaseBookService", "InMemoryBookService"]

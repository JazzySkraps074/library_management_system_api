"""Shared in-memory records for the alternative service implementations."""

from dataclasses import dataclass, field
from threading import RLock

from app.models.book import Book
from app.models.member import Member


@dataclass
class InMemoryStore:
    books: list[Book] = field(default_factory=list)
    members: list[Member] = field(default_factory=list)
    lock: RLock = field(default_factory=RLock, repr=False)

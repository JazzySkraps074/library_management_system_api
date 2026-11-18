"""Unit tests for database Book service decisions using repository doubles."""

from types import SimpleNamespace

import pytest

from app.exceptions import BookNotFoundError, MemberNotFoundError
from app.services.books import DatabaseBookService


class SessionDouble:
    def __init__(self):
        self.refreshed = []

    def refresh(self, item):
        self.refreshed.append(item)


class TransactionDouble:
    def __init__(self, session, factory):
        self.session, self.factory = session, factory

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc, traceback):
        if exc_type is None:
            self.factory.commits += 1
        else:
            self.factory.rollbacks += 1


class SessionFactoryDouble:
    def __init__(self):
        self.session = SessionDouble()
        self.commits = 0
        self.rollbacks = 0

    def __call__(self):
        return TransactionDouble(self.session, self)

    def begin(self):
        return TransactionDouble(self.session, self)


def test_database_book_create_checks_member_and_commits(monkeypatch):
    factory = SessionFactoryDouble()
    expected = object()
    monkeypatch.setattr(
        "app.services.books.database.MemberRepository",
        lambda _: type("Members", (), {"get_by_id": lambda self, _: object()})(),
    )
    monkeypatch.setattr(
        "app.services.books.database.BookRepository",
        lambda _: type("Books", (), {"create": lambda self, _: expected})(),
    )

    result = DatabaseBookService(factory).create_book(SimpleNamespace(member_id=1))

    assert result is expected
    assert factory.commits == 1
    assert factory.rollbacks == 0


def test_database_book_create_rolls_back_when_member_is_missing(monkeypatch):
    factory = SessionFactoryDouble()
    monkeypatch.setattr(
        "app.services.books.database.MemberRepository",
        lambda _: type("Members", (), {"get_by_id": lambda self, _: None})(),
    )
    monkeypatch.setattr(
        "app.services.books.database.BookRepository",
        lambda _: pytest.fail("must not insert a Book"),
    )

    with pytest.raises(MemberNotFoundError):
        DatabaseBookService(factory).create_book(SimpleNamespace(member_id=999))

    assert factory.commits == 0
    assert factory.rollbacks == 1


def test_database_book_get_reports_missing_record(monkeypatch):
    factory = SessionFactoryDouble()
    monkeypatch.setattr(
        "app.services.books.database.BookRepository",
        lambda _: type("Books", (), {"get_by_id": lambda self, _: None})(),
    )

    with pytest.raises(BookNotFoundError):
        DatabaseBookService(factory).get_book(999)

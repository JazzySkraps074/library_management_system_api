"""Unit tests for database Member service decisions using repository doubles."""

import pytest

from app.exceptions import MemberHasBooksError, MemberNotFoundError
from app.services.members import DatabaseMemberService


class SessionDouble:
    def refresh(self, item):
        pass


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


def test_database_member_create_commits_success(monkeypatch):
    factory = SessionFactoryDouble()
    member = object()
    repository = type("Members", (), {"create": lambda self, _: member})()
    monkeypatch.setattr(
        "app.services.members.database.MemberRepository", lambda _: repository
    )

    assert DatabaseMemberService(factory).create_member(object()) is member
    assert factory.commits == 1


def test_database_member_delete_rolls_back_when_books_exist(monkeypatch):
    factory = SessionFactoryDouble()
    member_repository = type("Members", (), {"get_by_id": lambda self, _: object()})()
    book_repository = type("Books", (), {"exists_for_member": lambda self, _: True})()
    monkeypatch.setattr(
        "app.services.members.database.MemberRepository", lambda _: member_repository
    )
    monkeypatch.setattr(
        "app.services.members.database.BookRepository", lambda _: book_repository
    )

    with pytest.raises(MemberHasBooksError):
        DatabaseMemberService(factory).delete_member(1)

    assert factory.commits == 0
    assert factory.rollbacks == 1


def test_database_member_delete_reports_missing_member(monkeypatch):
    factory = SessionFactoryDouble()
    monkeypatch.setattr(
        "app.services.members.database.MemberRepository",
        lambda _: type("Members", (), {"get_by_id": lambda self, _: None})(),
    )
    monkeypatch.setattr(
        "app.services.members.database.BookRepository",
        lambda _: pytest.fail("relationship query is not needed"),
    )

    with pytest.raises(MemberNotFoundError):
        DatabaseMemberService(factory).delete_member(999)

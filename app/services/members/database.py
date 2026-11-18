"""PostgreSQL implementation of the Member use cases."""

from sqlalchemy.orm import Session, sessionmaker

from app.exceptions import MemberHasBooksError, MemberNotFoundError
from app.models.book import Book
from app.models.member import Member
from app.repositories.books import BookRepository
from app.repositories.members import MemberRepository
from app.schemas.members import MemberCreate, MemberUpdate

from .base import MemberService


class DatabaseMemberService(MemberService):
    def __init__(self, session_factory: sessionmaker[Session]):
        self._session_factory = session_factory

    def list_members(self) -> list[Member]:
        with self._session_factory() as session:
            return MemberRepository(session).list_all()

    def get_member(self, member_id: int) -> Member:
        with self._session_factory() as session:
            member = MemberRepository(session).get_by_id(member_id)
            if member is None:
                raise MemberNotFoundError
            return member

    def create_member(self, data: MemberCreate) -> Member:
        with self._session_factory.begin() as session:
            member = MemberRepository(session).create(data)
            session.refresh(member)
            return member

    def replace_member(self, member_id: int, data: MemberUpdate) -> Member:
        with self._session_factory.begin() as session:
            repository = MemberRepository(session)
            member = repository.get_by_id(member_id)
            if member is None:
                raise MemberNotFoundError
            updated = repository.replace(member, data)
            session.refresh(updated)
            return updated

    def delete_member(self, member_id: int) -> None:
        with self._session_factory.begin() as session:
            repository = MemberRepository(session)
            member = repository.get_by_id(member_id)
            if member is None:
                raise MemberNotFoundError
            if BookRepository(session).exists_for_member(member_id):
                raise MemberHasBooksError
            repository.delete(member)

    def list_member_books(self, member_id: int) -> list[Book]:
        with self._session_factory() as session:
            if MemberRepository(session).get_by_id(member_id) is None:
                raise MemberNotFoundError
            return BookRepository(session).list_by_member(member_id)

"""In-memory implementation of the Member use cases."""

from app.exceptions import (
    DuplicateRecordError,
    MemberHasBooksError,
    MemberNotFoundError,
)
from app.models.book import Book
from app.models.member import Member
from app.schemas.members import MemberCreate, MemberUpdate
from app.services.in_memory_store import InMemoryStore

from .base import MemberService


class InMemoryMemberService(MemberService):
    def __init__(self, store: InMemoryStore):
        self._store = store

    def list_members(self) -> list[Member]:
        with self._store.lock:
            return list(self._store.members)

    def get_member(self, member_id: int) -> Member:
        with self._store.lock:
            for member in self._store.members:
                if member.id == member_id:
                    return member
            raise MemberNotFoundError

    def create_member(self, data: MemberCreate) -> Member:
        with self._store.lock:
            if any(
                item.email == data.email or item.membership_id == data.membership_id
                for item in self._store.members
            ):
                raise DuplicateRecordError
            member = Member(
                id=max((item.id for item in self._store.members), default=0) + 1,
                **data.model_dump(),
            )
            self._store.members.append(member)
            return member

    def replace_member(self, member_id: int, data: MemberUpdate) -> Member:
        with self._store.lock:
            member = self.get_member(member_id)
            if any(
                item.id != member_id
                and (
                    item.email == data.email or item.membership_id == data.membership_id
                )
                for item in self._store.members
            ):
                raise DuplicateRecordError
            for field, value in data.model_dump().items():
                setattr(member, field, value)
            return member

    def delete_member(self, member_id: int) -> None:
        with self._store.lock:
            member = self.get_member(member_id)
            if any(book.member_id == member_id for book in self._store.books):
                raise MemberHasBooksError
            self._store.members.remove(member)

    def list_member_books(self, member_id: int) -> list[Book]:
        with self._store.lock:
            self.get_member(member_id)
            return [book for book in self._store.books if book.member_id == member_id]

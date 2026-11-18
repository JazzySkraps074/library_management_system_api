"""Abstract Member service contract shared by every storage backend."""

from abc import ABC, abstractmethod

from app.models.book import Book
from app.models.member import Member
from app.schemas.members import MemberCreate, MemberUpdate


class MemberService(ABC):
    @abstractmethod
    def list_members(self) -> list[Member]:
        pass

    @abstractmethod
    def get_member(self, member_id: int) -> Member:
        pass

    @abstractmethod
    def create_member(self, data: MemberCreate) -> Member:
        pass

    @abstractmethod
    def replace_member(self, member_id: int, data: MemberUpdate) -> Member:
        pass

    @abstractmethod
    def delete_member(self, member_id: int) -> None:
        pass

    @abstractmethod
    def list_member_books(self, member_id: int) -> list[Book]:
        pass

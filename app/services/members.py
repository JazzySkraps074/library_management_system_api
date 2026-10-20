"""Business operations for Members."""

from sqlalchemy.orm import Session

from app.exceptions import MemberHasBooksError, MemberNotFoundError
from app.models.member import Member
from app.models.book import Book
from app.repositories.members import MemberRepository
from app.repositories.books import BookRepository
from app.schemas.members import MemberCreate, MemberUpdate


class MemberService:
    """Coordinate Member rules, repositories, and transactions."""

    def __init__(self, session: Session):
        self.session = session
        self.member_repository = MemberRepository(session)
        self.book_repository = BookRepository(session)

    def list_members(self) -> list[Member]:
        return self.member_repository.list_all()

    def get_member(self, member_id: int) -> Member:
        member = self.member_repository.get_by_id(member_id)
        if member is None:
            raise MemberNotFoundError
        return member

    def create_member(self, data: MemberCreate) -> Member:
        try:
            member = self.member_repository.create(data)
            self.session.commit()
            self.session.refresh(member)
            return member
        except Exception:
            self.session.rollback()
            raise

    def replace_member(self, member_id: int, data: MemberUpdate) -> Member:
        member = self.get_member(member_id)
        try:
            updated_member = self.member_repository.replace(member, data)
            self.session.commit()
            self.session.refresh(updated_member)
            return updated_member
        except Exception:
            self.session.rollback()
            raise

    def delete_member(self, member_id: int) -> None:
        member = self.get_member(member_id)
        if self.book_repository.exists_for_member(member_id):
            raise MemberHasBooksError
        try:
            self.member_repository.delete(member)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def list_member_books(self, member_id: int) -> list[Book]:
        self.get_member(member_id)
        return self.book_repository.list_by_member(member_id)

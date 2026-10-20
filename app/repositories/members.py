"""Database operations for Member records."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.member import Member
from app.schemas.members import MemberCreate, MemberUpdate


class MemberRepository:
    """Read and write Member rows through one SQLAlchemy session."""

    def __init__(self, session: Session):
        self.session = session

    def list_all(self) -> list[Member]:
        statement = select(Member).order_by(Member.id)
        return list(self.session.scalars(statement))

    def get_by_id(self, member_id: int) -> Member | None:
        return self.session.get(Member, member_id)

    def create(self, data: MemberCreate) -> Member:
        member = Member(**data.model_dump())
        self.session.add(member)
        self.session.flush()
        return member

    def replace(self, member: Member, data: MemberUpdate) -> Member:
        member.name = data.name
        member.email = data.email
        member.membership_id = data.membership_id
        member.phone = data.phone
        self.session.flush()
        return member

    def delete(self, member: Member) -> None:
        self.session.delete(member)

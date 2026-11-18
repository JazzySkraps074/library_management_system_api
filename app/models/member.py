"""SQLAlchemy model for the members table."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.book import Book


class Member(Base):
    """Map Member objects to rows in the members table."""

    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    membership_id: Mapped[str] = mapped_column(nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(10), nullable=False)

    # The relationship lets Python navigate member.books. The foreign key is
    # stored on Book because Book is the "many" side of the relationship.
    books: Mapped[list[Book]] = relationship(back_populates="member")


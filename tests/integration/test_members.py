"""Member repository integration tests against disposable PostgreSQL."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.members import MemberRepository
from app.schemas.members import MemberCreate


def test_member_repository_generates_id(db_session: Session) -> None:
    member = MemberRepository(db_session).create(
        MemberCreate(
            name="Pat", email="pat@example.com", membership_id="1", phone="1234567890"
        )
    )
    db_session.commit()
    assert member.id > 0


@pytest.mark.parametrize(
    "data",
    [
        MemberCreate(
            name="Other", email="pat@example.com", membership_id="2", phone="1234567890"
        ),
        MemberCreate(
            name="Other",
            email="other@example.com",
            membership_id="1",
            phone="1234567890",
        ),
    ],
    ids=["duplicate-email", "duplicate-membership-id"],
)
def test_postgres_enforces_member_unique_constraints(
    db_session: Session, data: MemberCreate
) -> None:
    repository = MemberRepository(db_session)
    repository.create(
        MemberCreate(
            name="Pat", email="pat@example.com", membership_id="1", phone="1234567890"
        )
    )
    db_session.commit()
    with pytest.raises(IntegrityError):
        repository.create(data)
    db_session.rollback()

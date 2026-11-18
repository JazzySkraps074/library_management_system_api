"""Unit tests for Member request validation."""

import pytest
from pydantic import ValidationError

from app.schemas.members import MemberCreate


def test_member_trims_whitespace_and_accepts_valid_values():
    member = MemberCreate(
        name=" Pat ", email="pat@example.com", membership_id="1", phone="1234567890"
    )
    assert member.name == "Pat"


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "Pat", "email": "bad", "membership_id": "1", "phone": "1234567890"},
        {
            "name": "Pat",
            "email": "pat@example.com",
            "membership_id": "1",
            "phone": "123456789x",
        },
        {
            "name": "Pat",
            "email": "pat@example.com",
            "membership_id": "",
            "phone": "1234567890",
        },
        {
            "name": " ",
            "email": "pat@example.com",
            "membership_id": "1",
            "phone": "1234567890",
        },
        {
            "name": "Pat",
            "email": "pat@example.com",
            "membership_id": "12",
            "phone": "1234567890",
        },
        {
            "name": "Pat",
            "email": "pat@example.com",
            "membership_id": "1",
            "phone": "123456789",
        },
        {
            "name": "Pat",
            "email": "pat@example.com",
            "membership_id": "1",
            "phone": "1" * 11,
        },
        {
            "name": "Pat",
            "email": "pat@example.com",
            "membership_id": "1",
            "phone": "12345abcde",
        },
        {"email": "pat@example.com", "membership_id": "1", "phone": "1234567890"},
        {
            "name": "Pat",
            "email": "pat@example.com",
            "membership_id": "1",
            "phone": "1234567890",
            "extra": 1,
        },
    ],
)
def test_member_rejects_invalid_email_phone_missing_fields_and_unknown_fields(payload):
    with pytest.raises(ValidationError):
        MemberCreate.model_validate(payload)

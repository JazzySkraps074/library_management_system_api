"""Unit tests for demo-token identity mapping and role enforcement."""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.auth.dependencies import get_current_user, require_admin
from app.auth.users import Role, get_demo_token_for_role, get_user_for_token
from app.config import Settings, StorageBackend


@pytest.fixture
def settings():
    return Settings(
        storage_backend=StorageBackend.MEMORY,
        demo_member_token="member-x",
        demo_admin_token="admin-x",
    )


@pytest.mark.parametrize(
    ("role", "expected"), [(Role.MEMBER, "member-x"), (Role.ADMIN, "admin-x")]
)
def test_role_maps_to_configured_token(settings, role, expected):
    assert get_demo_token_for_role(role, settings) == expected
    assert get_user_for_token(expected, settings).role is role


@pytest.mark.parametrize(
    "credentials",
    [
        None,
        HTTPAuthorizationCredentials(scheme="Basic", credentials="member-x"),
        HTTPAuthorizationCredentials(scheme="Bearer", credentials="unknown"),
    ],
)
def test_missing_malformed_and_unknown_credentials_receive_401(settings, credentials):
    with pytest.raises(HTTPException) as error:
        get_current_user(credentials, settings)
    assert error.value.status_code == 401
    assert error.value.headers["WWW-Authenticate"] == "Bearer"


def test_member_cannot_pass_administrator_check(settings):
    user = get_user_for_token("member-x", settings)
    with pytest.raises(HTTPException) as error:
        require_admin(user)
    assert error.value.status_code == 403


def test_administrator_passes_role_check(settings):
    user = get_user_for_token("admin-x", settings)
    assert require_admin(user) is user

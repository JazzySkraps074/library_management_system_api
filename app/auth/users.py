"""Predefined classroom identities mapped to configured Bearer tokens."""

from dataclasses import dataclass
from enum import Enum

from app.config import Settings


class Role(str, Enum):
    MEMBER = "member"
    ADMIN = "admin"


@dataclass(frozen=True)
class AuthenticatedUser:
    username: str
    role: Role


def get_demo_token_for_role(role: Role, settings: Settings) -> str:
    return (
        settings.demo_member_token if role is Role.MEMBER else settings.demo_admin_token
    )


def get_user_for_token(token: str, settings: Settings) -> AuthenticatedUser | None:
    if settings.demo_member_token and token == settings.demo_member_token:
        return AuthenticatedUser(username="member", role=Role.MEMBER)
    if settings.demo_admin_token and token == settings.demo_admin_token:
        return AuthenticatedUser(username="admin", role=Role.ADMIN)
    return None

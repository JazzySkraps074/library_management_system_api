"""FastAPI dependencies that expose startup-selected application services."""

from fastapi import Request

from app.config import Settings
from app.services.books import BookService
from app.services.members import MemberService


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_book_service(request: Request) -> BookService:
    return request.app.state.book_service


def get_member_service(request: Request) -> MemberService:
    return request.app.state.member_service

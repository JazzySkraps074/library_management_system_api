"""HTTP endpoints for the Member resource."""

from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import (
    ADMIN_RESPONSES,
    AUTHENTICATED_RESPONSES,
    AdminUser,
    CurrentUser,
)
from app.dependencies import get_member_service
from app.exceptions import (
    DuplicateRecordError,
    MemberHasBooksError,
    MemberNotFoundError,
)
from app.models.book import Book
from app.models.member import Member
from app.routers.http_errors import duplicate_record, member_has_books, member_not_found
from app.schemas.books import BookResponse
from app.schemas.members import MemberCreate, MemberResponse, MemberUpdate
from app.services.members import MemberService

router = APIRouter(prefix="/members", tags=["Members"])


@router.get("", response_model=list[MemberResponse], responses=AUTHENTICATED_RESPONSES)
def list_members(
    _current_user: CurrentUser, service: MemberService = Depends(get_member_service)
) -> list[Member]:
    return service.list_members()


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    responses={**AUTHENTICATED_RESPONSES, 404: {"description": "Member not found"}},
)
def get_member(
    member_id: int,
    _current_user: CurrentUser,
    service: MemberService = Depends(get_member_service),
) -> Member:
    try:
        return service.get_member(member_id)
    except MemberNotFoundError:
        raise member_not_found() from None


@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        **ADMIN_RESPONSES,
        409: {"description": "Email or membership ID already exists"},
    },
)
def create_member(
    data: MemberCreate,
    _admin_user: AdminUser,
    service: MemberService = Depends(get_member_service),
) -> Member:
    try:
        return service.create_member(data)
    except DuplicateRecordError:
        raise duplicate_record() from None


@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    responses={
        **ADMIN_RESPONSES,
        404: {"description": "Member not found"},
        409: {"description": "Email or membership ID already exists"},
    },
)
def replace_member(
    member_id: int,
    data: MemberUpdate,
    _admin_user: AdminUser,
    service: MemberService = Depends(get_member_service),
) -> Member:
    try:
        return service.replace_member(member_id, data)
    except MemberNotFoundError:
        raise member_not_found() from None
    except DuplicateRecordError:
        raise duplicate_record() from None


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **ADMIN_RESPONSES,
        404: {"description": "Member not found"},
        409: {"description": "Member still has Books"},
    },
)
def delete_member(
    member_id: int,
    _admin_user: AdminUser,
    service: MemberService = Depends(get_member_service),
) -> Response:
    try:
        service.delete_member(member_id)
    except MemberNotFoundError:
        raise member_not_found() from None
    except MemberHasBooksError:
        raise member_has_books() from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    responses={**AUTHENTICATED_RESPONSES, 404: {"description": "Member not found"}},
)
def list_member_books(
    member_id: int,
    _current_user: CurrentUser,
    service: MemberService = Depends(get_member_service),
) -> list[Book]:
    try:
        return service.list_member_books(member_id)
    except MemberNotFoundError:
        raise member_not_found() from None

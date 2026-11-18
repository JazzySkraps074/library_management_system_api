"""HTTP endpoints for the Book resource."""

from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import (
    ADMIN_RESPONSES,
    AUTHENTICATED_RESPONSES,
    AdminUser,
    CurrentUser,
)
from app.dependencies import get_book_service
from app.exceptions import BookNotFoundError, DuplicateRecordError, MemberNotFoundError
from app.models.book import Book
from app.routers.http_errors import book_not_found, duplicate_record, member_not_found
from app.schemas.books import BookCreate, BookResponse, BookUpdate
from app.services.books import BookService

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=list[BookResponse], responses=AUTHENTICATED_RESPONSES)
def list_books(
    _current_user: CurrentUser, service: BookService = Depends(get_book_service)
) -> list[Book]:
    return service.list_books()


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    responses={**AUTHENTICATED_RESPONSES, 404: {"description": "Book not found"}},
)
def get_book(
    book_id: int,
    _current_user: CurrentUser,
    service: BookService = Depends(get_book_service),
) -> Book:
    try:
        return service.get_book(book_id)
    except BookNotFoundError:
        raise book_not_found() from None


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        **ADMIN_RESPONSES,
        404: {"description": "Referenced Member not found"},
        409: {"description": "Book ISBN already exists"},
    },
)
def create_book(
    data: BookCreate,
    _admin_user: AdminUser,
    service: BookService = Depends(get_book_service),
) -> Book:
    try:
        return service.create_book(data)
    except MemberNotFoundError:
        raise member_not_found() from None
    except DuplicateRecordError:
        raise duplicate_record() from None


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    responses={
        **ADMIN_RESPONSES,
        404: {"description": "Book or referenced Member not found"},
        409: {"description": "Book ISBN already exists"},
    },
)
def replace_book(
    book_id: int,
    data: BookUpdate,
    _admin_user: AdminUser,
    service: BookService = Depends(get_book_service),
) -> Book:
    try:
        return service.replace_book(book_id, data)
    except BookNotFoundError:
        raise book_not_found() from None
    except MemberNotFoundError:
        raise member_not_found() from None
    except DuplicateRecordError:
        raise duplicate_record() from None


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**ADMIN_RESPONSES, 404: {"description": "Book not found"}},
)
def delete_book(
    book_id: int,
    _admin_user: AdminUser,
    service: BookService = Depends(get_book_service),
) -> Response:
    try:
        service.delete_book(book_id)
    except BookNotFoundError:
        raise book_not_found() from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)

"""Translate application outcomes into HTTP responses at the route boundary."""

from fastapi import HTTPException, status


def book_not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


def member_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
    )


def member_has_books() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Delete the member's books before deleting the member",
    )


def duplicate_record() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT, detail="A unique value is already in use"
    )

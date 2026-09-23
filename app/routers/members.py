from fastapi import APIRouter, HTTPException, status
from app.schemas import MemberBase, MemberResponse
from app.schemas import BookResponse
from app import storage

router = APIRouter(prefix="/members", tags=["members"])


def find_member(member_id: int) -> MemberResponse:
    """Find one member or return an HTTP 404 error to the client."""
    for member in storage.members:
        if member.id == member_id:
            return member

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Member not found",
    )


# POST creates a new member
@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a member",
    description="Create a libary member from validated information.",
)
def create_member(data: MemberBase) -> MemberResponse:
    """Check if email already exists"""
    for member in storage.members:
        if member.email == data.email:
            raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists",
                )

    """Check if Membership ID already exists"""
    for member in storage.members:
        if member.membership_id == data.membership_id:
            raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Membership ID already exists",
                )

    """Create a Member."""
    next_member_id = max((member.id for member in storage.members), 
                       default=0) + 1
    member = MemberResponse(
        id=next_member_id,
        **data.model_dump(),
    )
    storage.members.append(member)
    return member

# GET /members retrieves all the members in the collection.
@router.get(
    "",
    response_model=list[MemberResponse],
    summary="List all members",
    description="Return every member currently stored by the management system.",
)

def list_members() -> list[MemberResponse]:
    """Return every member currently stored in memory."""
    return storage.members


# The value inside {member_id} is supplied by the URL path.
# GET /members/{member_id} retrieves a single member based on the requested id number
@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Get one member",
    description="Return the member identified by the path parameter.",
    responses={404: {"description": "Member not found"}},
)

def get_member(member_id: int) -> MemberResponse:
    """Return the member with the requested ID."""
    return find_member(member_id)


# PUT replaces the editable values of the member identified by the URL.
@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="Replace a member",
    description="Replace all editable fields of an existing member.",
    responses={404: {"description": "Member not found"}},
)

def replace_member(
    member_id: int,
    data: MemberBase,
) -> MemberResponse:
    """Replace the name and description of an existing member."""
    member = find_member(member_id)
    updated_member = MemberResponse(
        id=member_id,
        **data.model_dump(),
    )
    storage.members[storage.members.index(member)] = updated_member
    return updated_member


# A successful DELETE removes the member and returns no response body.
@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a member",
    description="Delete the member identified by the path parameter.",
    responses={404: {"description": "Member not found"},
               409: {"description": "Member still has checked out books"},
               },
)

def delete_member(member_id: int) -> MemberResponse:
    """Remove a member from the in-memory collection."""
    member = find_member(member_id)

    # Do not leave books pointing to a member that no longer exists.
    if any(member_id == member_id for task in storage.books):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Delete the member's books before deleting the member",
        )

    storage.members.remove(member)
    return MemberResponse(status_code=status.HTTP_204_NO_CONTENT)


# This nested URL reads the books that belong to one member.
@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    summary="List a member's checked out books",
    description="Return every book checked out by the requested member.",
    responses={404: {"description": "Member not found"}},
)
def list_member_books(member_id: int) -> list[BookResponse]:
    """Return every member associated with the requested member."""
    find_member(member_id)
    return [book for book in storage.books if book.member_id == member_id]
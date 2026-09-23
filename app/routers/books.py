from fastapi import APIRouter, HTTPException, status
from app.schemas import BookBase, BookResponse
from app import storage

router = APIRouter(prefix="/books", tags=["Books"])

def find_book(book_id: int) -> BookResponse:
    """Find one book or return an HTTP 404 error to the client."""
    for book in storage.books:
        if book.id == book_id:
            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found",
    )

# POST creates a new Book.
@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a book",
    description="Create a book from validated information.",
)

def create_book(data: BookBase) -> BookResponse:
    """Check if ISBN already exists"""
    for book in storage.books:
        if book.isbn == data.isbn:
            raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="ISBN already exists",
                )

    """Create a book."""
    next_book_id = max((book.id for book in storage.books), 
                       default=0) + 1  
    book = BookResponse(
        id=next_book_id,
        **data.model_dump(),
    )
    storage.books.append(book)
    return book



# GET /books retrieves all the books in the collection.
@router.get(
    "",
    response_model=list[BookResponse],
    summary="List all Books",
    description="Return every book currently stored by the management system.",
)

def list_Books() -> list[BookResponse]:
    """Return every book currently stored in memory."""
    return storage.books


# The value inside {book_id} is supplied by the URL path.
# GET /books/{book_id} retrieves a single book based on the requested id number
@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get one Book",
    description="Return the book identified by the path parameter.",
    responses={404: {"description": "Book not found"}},
)

def get_Book(book_id: int) -> BookResponse:
    """Return the Book with the requested ID."""
    return find_book(book_id)


# PUT replaces the editable values of the book identified by the URL.
@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Replace a book",
    description="Replace all editable fields of an existing book.",
    responses={404: {"description": "Book not found"}},
)

def replace_Book(
    book_id: int,
    data: BookBase,
) -> BookResponse:
    """Replace the name and description of an existing Book."""
    Book = find_book(book_id)
    updated_book = BookResponse(
        id=book_id,
        **data.model_dump(),
    )
    storage.books[storage.books.index(Book)] = updated_book
    return updated_book


# A successful DELETE removes the book and returns no response body.
@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
    description="Delete the book identified by the path parameter.",
    responses={404: {"description": "Book not found"}},
)
def delete_book(book_id: int) -> BookResponse:
    """Remove a book from the in-memory collection."""
    book = find_book(book_id)
    storage.books.remove(book)
    return BookResponse(status_code=status.HTTP_204_NO_CONTENT)
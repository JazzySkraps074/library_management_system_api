"""FastAPI application for the Library Management System API."""

from fastapi import FastAPI

from app.routers.books import router as books_router
from app.routers.members import router as members_router

# Tag descriptions organize related operations and explain each resource group
# in Swagger UI and ReDoc.
tags_metadata = [
    {
        "name": "General",
        "description": "Basic application information and health checks.",
    },
    {
        "name": "Books",
        "description": "Create and manage books and view the respective members who checked them out.",
    },
    {
        "name": "Members",
        "description": "Create and manage library members and their checked out books.",
    },
]

# Create the FastAPI application object that Uvicorn will load and run.
# This metadata is also displayed in the generated API documentation.
app = FastAPI(
    title="Library Management System API",
    description=(
        "A REST API for managing library books and members."
        "The API uses FastAPI, Pydantic schemas, and in-memory storage"
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# Register the Books and Members routers.
app.include_router(books_router)
app.include_router(members_router)


# This decorator connects an HTTP GET request for "/" to read_root().
@app.get("/", tags=["General"], summary="Introduce the API")
def read_root() -> dict[str, str]:
    """Return a short introduction to the API."""
    return {"message": "Library Management System API"}


# The health endpoint gives clients a simple way to confirm the API is running.
@app.get("/health", tags=["General"], summary="Check API health")
def health_check() -> dict[str, str]:
    """Confirm that the API process is running."""
    # A successful request receives HTTP 200 and this JSON response body.
    return {"status": "healthy"}
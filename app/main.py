"""FastAPI application for the Library Management System API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app import models  # noqa: F401 - register mappings before create_all
from app.config import Settings, StorageBackend
from app.database.session import create_database
from app.models.base import Base
from app.routers.books import router as books_router
from app.routers.members import router as members_router
from app.services.books import DatabaseBookService, InMemoryBookService
from app.services.in_memory_store import InMemoryStore
from app.services.members import DatabaseMemberService, InMemoryMemberService


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = Settings()
    application.state.settings = settings
    application.state.database = None

    if settings.storage_backend is StorageBackend.MEMORY:
        store = InMemoryStore()
        application.state.book_service = InMemoryBookService(store)
        application.state.member_service = InMemoryMemberService(store)
    else:
        database = create_database(settings)
        Base.metadata.create_all(bind=database.engine)
        application.state.database = database
        application.state.book_service = DatabaseBookService(database.session_factory)
        application.state.member_service = DatabaseMemberService(
            database.session_factory
        )
    try:
        yield
    finally:
        database = application.state.database
        if database is not None:
            database.engine.dispose()


app = FastAPI(
    title="Library Management System API",
    description="Manage library books and members with replaceable storage services.",
    version="3.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "General",
            "description": "Application information and health checks.",
        },
        {"name": "Books", "description": "Create and manage books."},
        {"name": "Members", "description": "Create and manage library members."},
    ],
)

app.include_router(books_router)
app.include_router(members_router)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, __: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "A unique value is already in use or a relationship constraint failed"
        },
    )


@app.get("/", tags=["General"], summary="Introduce the API")
def read_root() -> dict[str, str]:
    return {"message": "Library Management System API"}


@app.get("/health", tags=["General"], summary="Check API health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}

"""Shared fixtures for unit, integration, and conformance tests."""

import os
from collections.abc import Generator

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient
from testcontainers.community.postgres import PostgresContainer

from app.auth.users import Role, get_demo_token_for_role
from app.config import Settings, StorageBackend


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    previous_url = os.environ.get("DATABASE_URL")
    previous_backend = os.environ.get("STORAGE_BACKEND")
    with PostgresContainer(
        "postgres:16-alpine",
        username="postgres",
        password="postgres",
        dbname="library_test",
        driver="psycopg",
    ) as container:
        os.environ["DATABASE_URL"] = container.get_connection_url()
        os.environ["STORAGE_BACKEND"] = "database"
        yield container
    if previous_url is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = previous_url
    if previous_backend is None:
        os.environ.pop("STORAGE_BACKEND", None)
    else:
        os.environ["STORAGE_BACKEND"] = previous_backend


@pytest.fixture(scope="session")
def db_engine(postgres_container: PostgresContainer) -> Generator[Engine, None, None]:
    from app import models  # noqa: F401 - register mappings
    from app.database.session import create_database

    database = create_database(Settings())
    yield database.engine
    database.engine.dispose()


@pytest.fixture
def reset_database(db_engine: Engine) -> Generator[None, None, None]:
    from app.models.base import Base

    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)
    yield
    Base.metadata.drop_all(bind=db_engine)


@pytest.fixture
def db_session(
    reset_database: None, db_engine: Engine
) -> Generator[Session, None, None]:
    factory = sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)
    with factory() as session:
        yield session
        session.rollback()


@pytest.fixture
def database_client(reset_database: None) -> Generator[TestClient, None, None]:
    from app.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def memory_client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("STORAGE_BACKEND", "memory")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    from app.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def demo_settings() -> Settings:
    return Settings(storage_backend=StorageBackend.MEMORY)


@pytest.fixture
def member_headers(demo_settings: Settings) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_demo_token_for_role(Role.MEMBER, demo_settings)}"
    }


@pytest.fixture
def admin_headers(demo_settings: Settings) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_demo_token_for_role(Role.ADMIN, demo_settings)}"
    }


@pytest.fixture
def admin_client(
    database_client: TestClient, admin_headers: dict[str, str]
) -> TestClient:
    database_client.headers.update(admin_headers)
    return database_client


@pytest.fixture
def member_client(
    database_client: TestClient, member_headers: dict[str, str]
) -> TestClient:
    database_client.headers.update(member_headers)
    return database_client

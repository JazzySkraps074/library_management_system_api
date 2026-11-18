"""PostgreSQL engine and session-factory construction."""

from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings


@dataclass(frozen=True)
class DatabaseInfrastructure:
    engine: Engine
    session_factory: sessionmaker[Session]


def create_database(settings: Settings) -> DatabaseInfrastructure:
    if not settings.database_url:
        raise ValueError("DATABASE_URL is required to create database infrastructure")
    engine = create_engine(settings.database_url, echo=settings.database_echo_sql)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return DatabaseInfrastructure(engine=engine, session_factory=session_factory)

import os
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

# Use env variables for configuration. These must be provided via .env by the orchestrator:
#   MYSQL_URL, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT

class Base(DeclarativeBase):
    """SQLAlchemy Declarative Base for ORM models."""


def _build_mysql_url() -> URL:
    """Build a SQLAlchemy URL object from environment variables for MySQL connection."""
    mysql_url = os.getenv("MYSQL_URL", "").strip()
    mysql_user = os.getenv("MYSQL_USER", "").strip()
    mysql_password = os.getenv("MYSQL_PASSWORD", "").strip()
    mysql_db = os.getenv("MYSQL_DB", "").strip()
    mysql_port = os.getenv("MYSQL_PORT", "").strip()

    # Prefer a full DSN if provided (e.g., mysql+pymysql://user:pass@host:3306/dbname)
    if mysql_url:
        return URL.create(mysql_url)

    if not (mysql_user and mysql_password and mysql_db):
        raise RuntimeError(
            "Database configuration missing. Please set either MYSQL_URL or all of "
            "MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, and optionally MYSQL_PORT."
        )

    host = "localhost"
    # Allow MYSQL_URL to just be host if others provided, but we used empty -> fallback.
    # If MYSQL_URL was empty, we keep default host. If MYSQL_URL contains a host only (rare), ignore.
    try:
        port: Optional[int] = int(mysql_port) if mysql_port else 3306
    except ValueError:
        port = 3306

    # Default driver: pymysql (pure python). Ensure it's available via requirements.
    return URL.create(
        drivername="mysql+pymysql",
        username=mysql_user,
        password=mysql_password,
        host=host,
        port=port,
        database=mysql_db,
    )


# Create engine and session factory
DATABASE_URL = _build_mysql_url()
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=280,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a SQLAlchemy session per request."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except SQLAlchemyError:
            pass

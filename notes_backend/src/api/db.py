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
        # If a full DSN string is provided, create URL from string
        return URL.create(mysql_url)

    # If required discrete parts are missing, we can't connect to MySQL. Defer raising until first DB use.
    if not (mysql_user and mysql_password and mysql_db):
        raise RuntimeError(
            "Database configuration missing. Please set either MYSQL_URL or all of "
            "MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, and optionally MYSQL_PORT."
        )

    host = os.getenv("MYSQL_HOST", "localhost").strip() or "localhost"
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


# Lazily initialized engine/session to avoid import-time failures when env is missing.
_engine = None
_SessionLocal = None


def _ensure_engine():
    """Create the engine and session factory once, when first needed."""
    global _engine, _SessionLocal
    if _engine is not None and _SessionLocal is not None:
        return
    # Attempt to build URL; this may raise if env is missing. We let request/startup handlers catch that.
    database_url = _build_mysql_url()
    _engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=280,
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


# PUBLIC_INTERFACE
def get_engine():
    """Return the SQLAlchemy engine, initializing it if necessary."""
    _ensure_engine()
    return _engine


# PUBLIC_INTERFACE
def get_session_factory():
    """Return the SQLAlchemy session factory, initializing it if necessary."""
    _ensure_engine()
    return _SessionLocal


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a SQLAlchemy session per request.

    This defers session creation until the first actual request, avoiding application
    import-time crashes when DB env vars are not set. If configuration is invalid,
    a SQLAlchemyError or RuntimeError may be raised on first request.
    """
    # Initialize engine/session lazily
    SessionLocal = get_session_factory()
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except SQLAlchemyError:
            # Swallow close errors to avoid masking underlying issues.
            pass

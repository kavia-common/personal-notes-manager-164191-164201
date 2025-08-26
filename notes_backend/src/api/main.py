from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

from .db import Base, get_engine
from .models import Note  # noqa: F401  # Ensure model is imported so metadata includes it
from .routers_notes import router as notes_router

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notes_backend")

openapi_tags = [
    {"name": "Health", "description": "Service health and diagnostics"},
    {"name": "Notes", "description": "Operations for managing personal notes"},
]

# PUBLIC_INTERFACE
app = FastAPI(
    title="Notes Backend API",
    description="RESTful API for managing personal notes. Provides CRUD endpoints for notes.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)
app.__doc__ = """FastAPI application entrypoint for the Notes Backend API.

Environment variables:
- ALLOWED_ORIGINS: Comma-separated list of allowed CORS origins (e.g., "http://localhost:3000,http://127.0.0.1:3000").
  Defaults to those two local dev origins if not set.

Routes:
- GET / (Health)
- Notes CRUD under /notes
"""

# Build CORS allowed origins from environment (comma-separated)
def _get_allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "").strip()
    if raw:
        # Split by comma and strip spaces
        return [o.strip() for o in raw.split(",") if o.strip()]
    # Default to common localhost dev origins
    return ["http://localhost:3000", "http://127.0.0.1:3000"]

allowed_origins = _get_allowed_origins()

# Note: Using explicit origins avoids invalid combination of allow_credentials=True with wildcard.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database schema (idempotent). In production consider alembic.
# We attempt to create the tables if DB configuration is present. If not, we log and continue.
try:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema ensured.")
except RuntimeError as e:
    # Likely missing env vars; keep the app running for health and docs.
    logger.warning(f"Database not configured at startup: {e}")
except SQLAlchemyError as e:
    # DB might be unreachable; keep app up to allow health checks and later retries.
    logger.error(f"Failed to initialize database schema: {e}")


@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Returns a simple JSON payload indicating the service is up.",
)
def health_check():
    """Health check endpoint that returns a simple status payload."""
    return {"message": "Healthy"}

# Register Notes routes
app.include_router(notes_router)

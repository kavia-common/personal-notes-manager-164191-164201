from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
import os

from .db import Base, engine
from .models import Note  # noqa: F401  # Ensure model is imported so metadata includes it
from .routers_notes import router as notes_router

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
try:
    Base.metadata.create_all(bind=engine)
except SQLAlchemyError:
    # Let app start; individual requests will return clear DB errors if config is wrong.
    pass


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

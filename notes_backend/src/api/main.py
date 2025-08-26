from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from .db import Base, engine
from .models import Note  # noqa: F401  # Ensure model is imported so metadata includes it
from .routers_notes import router as notes_router

openapi_tags = [
    {"name": "Health", "description": "Service health and diagnostics"},
    {"name": "Notes", "description": "Operations for managing personal notes"},
]

app = FastAPI(
    title="Notes Backend API",
    description="RESTful API for managing personal notes. Provides CRUD endpoints for notes.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for frontend host
    allow_credentials=True,
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

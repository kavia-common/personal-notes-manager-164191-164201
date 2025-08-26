from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .db import get_db
from .models import Note
from .schemas import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
)


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[NoteOut],
    summary="List all notes",
    description="Retrieve a list of all notes ordered by most recently updated.",
    responses={
        200: {"description": "List of notes returned successfully"},
        500: {"description": "Internal server error"},
    },
)
def list_notes(db: Session = Depends(get_db)) -> List[NoteOut]:
    """Return all notes."""
    try:
        notes = db.query(Note).order_by(Note.updated_at.desc()).all()
        return notes
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch notes") from e


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
    description="Create a new note with a title and optional content.",
    responses={
        201: {"description": "Note created successfully"},
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"},
    },
)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteOut:
    """Create a new note record."""
    try:
        note = Note(title=payload.title, content=payload.content)
        db.add(note)
        db.commit()
        db.refresh(note)
        return note
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create note") from e


# PUBLIC_INTERFACE
@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get a note by ID",
    description="Retrieve a single note by its unique identifier.",
    responses={
        200: {"description": "Note returned successfully"},
        404: {"description": "Note not found"},
        500: {"description": "Internal server error"},
    },
)
def get_note(
    note_id: int = Path(..., description="ID of the note to retrieve", ge=1),
    db: Session = Depends(get_db),
) -> NoteOut:
    """Fetch a single note by ID."""
    try:
        note: Optional[Note] = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Failed to fetch note") from e


# PUBLIC_INTERFACE
@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update a note",
    description="Update an existing note's title and/or content.",
    responses={
        200: {"description": "Note updated successfully"},
        400: {"description": "Invalid input"},
        404: {"description": "Note not found"},
        500: {"description": "Internal server error"},
    },
)
def update_note(
    payload: NoteUpdate,
    note_id: int = Path(..., description="ID of the note to update", ge=1),
    db: Session = Depends(get_db),
) -> NoteOut:
    """Update fields of an existing note."""
    try:
        note: Optional[Note] = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        if payload.title is not None:
            note.title = payload.title
        if payload.content is not None:
            note.content = payload.content

        db.add(note)
        db.commit()
        db.refresh(note)
        return note
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update note") from e


# PUBLIC_INTERFACE
@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="Delete a note by its unique identifier.",
    responses={
        204: {"description": "Note deleted successfully"},
        404: {"description": "Note not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_note(
    note_id: int = Path(..., description="ID of the note to delete", ge=1),
    db: Session = Depends(get_db),
) -> None:
    """Delete an existing note by ID."""
    try:
        note: Optional[Note] = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        db.delete(note)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete note") from e

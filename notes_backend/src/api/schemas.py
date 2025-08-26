from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Base fields for Note payloads."""
    title: str = Field(..., description="Title of the note", min_length=1, max_length=255)
    content: Optional[str] = Field(None, description="Content/body of the note")


class NoteCreate(NoteBase):
    """Payload for creating a new note."""
    pass


class NoteUpdate(BaseModel):
    """Payload for updating an existing note."""
    title: Optional[str] = Field(None, description="Updated title of the note", min_length=1, max_length=255)
    content: Optional[str] = Field(None, description="Updated content/body of the note")


class NoteOut(BaseModel):
    """Response model representing a note."""
    id: int = Field(..., description="Unique identifier for the note")
    title: str = Field(..., description="Title of the note")
    content: Optional[str] = Field(None, description="Content/body of the note")
    created_at: datetime = Field(..., description="Timestamp when the note was created (UTC)")
    updated_at: datetime = Field(..., description="Timestamp when the note was last updated (UTC)")

    class Config:
        from_attributes = True

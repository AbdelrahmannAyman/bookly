from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    publisher: str = Field(..., min_length=1, max_length=255)
    page_count: int = Field(..., gt=0)
    language: str = Field(..., min_length=1, max_length=50)


class BookCreate(BookBase):
    publisher_date: Optional[datetime] = None  # Make it optional with default


class Book(BookBase):
    id: str  # Changed from UUID4 to str to match model
    publisher_date: datetime
    created_at: Optional[datetime] = None  # Added missing field

    class Config:
        from_attributes = True
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from src.dto.timemixin import TimestampMixin
from uuid import UUID, uuid4

class BookLinkDTO(BaseModel):
    book_id: UUID
    primary_author: bool

class AuthorCreateDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: Optional[str] = None
    bio: Optional[str] = None
    birth_date: Optional[date]
    death_date: Optional[date]
    books: List[BookLinkDTO]

class AuthorUpdateDTO(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    birth_date: Optional[date]
    death_date: Optional[date]
    books: List[BookLinkDTO]

class AuthorDTO(TimestampMixin):
    id: UUID
    first_name: str
    last_name: Optional[str] = None
    bio: Optional[str] = None
    birth_date: Optional[date]
    death_date: Optional[date]
    books: List[BookLinkDTO]

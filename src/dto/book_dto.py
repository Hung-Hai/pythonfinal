from typing import List, Optional

from pydantic import BaseModel, Field
from src.dto.timemixin import TimestampMixin
from uuid import UUID, uuid4

class AuthorBookLinkDTO(BaseModel):
    author_id: UUID
    primary_author: bool

class BookCreateDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    isbn: Optional[str] = None
    title: str
    published_year: Optional[int] = None
    language: Optional[str] = None
    edition: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    publisher_id: UUID
    authors: List[AuthorBookLinkDTO]

class BookUpdateDTO(BaseModel):
    isbn: Optional[str] = None
    title: Optional[str] = None
    published_year: Optional[int] = None
    language: Optional[str] = None
    edition: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    publisher_id: UUID
    authors: List[AuthorBookLinkDTO]

class BookDTO(TimestampMixin):
    id: UUID
    isbn: Optional[str] = None
    title: str
    published_year: Optional[int] = None
    language: Optional[str] = None
    edition: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    publisher_id: UUID
    authors: List[AuthorBookLinkDTO]

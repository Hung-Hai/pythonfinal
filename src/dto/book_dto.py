from typing import Optional

from pydantic import BaseModel, Field
from src.dto.timemixin import TimestampMixin
from uuid import UUID, uuid4

class BookCreateDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    isbn: Optional[str] = None
    title: str
    author: Optional[str] = None
    published_year: Optional[int] = None
    total_quantity: Optional[int] = None
    current_quantity: Optional[int] = None
    publisher: Optional[str] = None
    image_url_s: Optional[str] = None
    image_url_m: Optional[str] = None
    image_url_l: Optional[str] = None

class BookUpdateDTO(BaseModel):
    isbn: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    published_year: Optional[int] = None
    total_quantity: Optional[int] = None
    current_quantity: Optional[int] = None
    publisher: Optional[str] = None
    image_url_s: Optional[str] = None
    image_url_m: Optional[str] = None
    image_url_l: Optional[str] = None

class BookDTO(TimestampMixin):
    id: UUID
    isbn: Optional[str] = None
    title: str
    author: Optional[str] = None
    published_year: Optional[int] = None
    total_quantity: Optional[int] = None
    current_quantity: Optional[int] = None
    publisher: Optional[str] = None
    image_url_s: Optional[str] = None
    image_url_m: Optional[str] = None
    image_url_l: Optional[str] = None
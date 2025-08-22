from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional
from src.dto.book_dto import BookDTO
from src.dto.timemixin import TimestampMixin

class PublisherDTO(TimestampMixin):
    id: UUID
    name: str
    address: str
    phone: str
    email: EmailStr
    website: HttpUrl

class PublisherCreateDTO(BaseModel):
    name: str
    address: str
    phone: str
    email: EmailStr
    website: HttpUrl

class PublisherUpdateDTO(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None

class PublisherWithBooksDTO(PublisherDTO):
    books: List[BookDTO] = []
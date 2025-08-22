from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from src.models.relationship_models import BookStatus
from src.dto.timemixin import TimestampMixin

class BooksPhysicalDTO(TimestampMixin):
    id: UUID
    barcode: str
    shelf_location: str
    status: Optional[BookStatus]
    book_id: Optional[UUID]

class BooksPhysicalCreateDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    barcode: str
    shelf_location: str
    status: Optional[BookStatus] = None
    book_id: Optional[UUID]

class BooksPhysicalUpdateDTO(BaseModel):
    barcode: Optional[str] = None
    shelf_location: Optional[str] = None
    status: Optional[BookStatus] = None
    book_id: Optional[UUID] = None

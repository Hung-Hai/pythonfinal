from uuid import UUID
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, HttpUrl
from typing import Optional
from src.models.relationship_models import BookStatus
from src.dto.timemixin import TimestampMixin

class FileFormat(str, Enum):
    EPUB = "EPUB"
    PDF = "PDF"
    MOBI = "MOBI"

class LicenseType(str, Enum):
    ONE = "ONEUSER"
    UNLI = "UNLIMITED"
    METER = "METERED"

class BooksDigitalDTO(TimestampMixin):
    id: UUID
    file_format: Optional[FileFormat]
    file_url: HttpUrl
    status: Optional[BookStatus]
    license_type: LicenseType
    license_expiration: datetime
    book_id: Optional[UUID]

class BooksDigitalCreateDTO(BaseModel):
    file_format: FileFormat
    file_url: HttpUrl
    status: Optional[BookStatus] = None
    license_type: LicenseType
    license_expiration: Optional[datetime] = None
    book_id: Optional[UUID]

class BooksDigitalUpdateDTO(BaseModel):
    file_format: Optional[FileFormat] = None
    file_url: Optional[HttpUrl] = None
    status: Optional[BookStatus] = None
    license_type: Optional[LicenseType] = None
    license_expiration: Optional[datetime] = None
    book_id: Optional[UUID] = None

from typing import Optional

from pydantic import BaseModel, Field
from src.dto.timemixin import TimestampMixin
from uuid import UUID, uuid4

class CustomerCreateDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class CustomerUpdateDTO(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class CustomerDTO(TimestampMixin):
    id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from src.dto.timemixin import TimestampMixin
from uuid import UUID, uuid4

class CategoryCreateDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None

class CategoryUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class CategoryDTO(TimestampMixin):
    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None

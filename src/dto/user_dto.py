from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from src.dto.timemixin import TimestampMixin
from uuid import UUID, uuid4

class UserCreateDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    password: str
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class UserUpdateDTO(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    last_login: Optional[datetime] = None

class UserDTO(TimestampMixin):
    id: UUID
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = Field(None, description="Hashed password (optional)")
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    last_login: datetime

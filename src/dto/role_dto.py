from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from src.dto.timemixin import TimestampMixin
from src.dto.user_dto import UserDTO

class RoleCreateDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    users: List[UserDTO]

class RoleUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    user_ids: Optional[List[UUID]] = None

class RoleDTO(TimestampMixin):
    id: UUID
    name: str
    description: Optional[str] = None
    users: List[UserDTO]

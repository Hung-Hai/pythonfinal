from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field
from src.dto.timemixin import TimestampMixin
from uuid import UUID, uuid4

class BorrowStatusDTO(str, Enum):
    CHECKOUT = "checkout"
    RETURNED = "returned"
    OVERDUE = "overdue"

class BorrowCreateDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    borrow_date: datetime
    due_date: datetime
    user_id: UUID
    book_id: UUID
    status: Optional[BorrowStatusDTO] = BorrowStatusDTO.CHECKOUT

class BorrowUpdateDTO(BaseModel):
    return_date: Optional[datetime] = None
    status: Optional[BorrowStatusDTO] = None

class BorrowDTO(TimestampMixin):
    id: UUID
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: BorrowStatusDTO
    user_id: UUID
    book_id: UUID
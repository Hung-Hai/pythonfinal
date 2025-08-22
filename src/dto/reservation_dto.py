from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from src.dto.timemixin import TimestampMixin

class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class ReservationDTO(TimestampMixin):
    id: UUID
    reservation_date: datetime
    expiration_date: datetime
    status: ReservationStatus
    position: int
    user_id: Optional[UUID]
    book_id: Optional[UUID]

class ReservationCreateDTO(BaseModel):
    reservation_date: datetime
    expiration_date: datetime
    status: ReservationStatus = ReservationStatus.PENDING
    position: int
    user_id: Optional[UUID] = None
    book_id: Optional[UUID] = None

class ReservationUpdateDTO(BaseModel):
    reservation_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    status: Optional[ReservationStatus] = None
    position: Optional[int] = None
    user_id: Optional[UUID] = None
    book_id: Optional[UUID] = None
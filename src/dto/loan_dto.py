from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field
from src.dto.timemixin import TimestampMixin
from uuid import UUID

class LoanStatus(str, Enum):
    CHECKOUT = "CHECKOUT"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"
    EXPIRED = "EXPIRED"


class LoanBaseDTO(BaseModel):
    loan_date: datetime
    due_date: datetime
    status: LoanStatus
    user_id: UUID


class PhysicalLoanDTO(LoanBaseDTO):
    id: UUID
    return_date: Optional[datetime] = None
    book_id: UUID


class DigitalLoanDTO(LoanBaseDTO):
    id: UUID
    access_token: str
    book_id: UUID


class PhysicalLoanCreateDTO(LoanBaseDTO):
    return_date: datetime = None
    book_id: UUID


class DigitalLoanCreateDTO(LoanBaseDTO):
    access_token: Optional[str] = None
    book_id: UUID


class PhysicalLoanUpdateDTO(TimestampMixin):
    loan_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Optional[LoanStatus] = None
    user_id: Optional[UUID] = None
    return_date: Optional[datetime] = None
    book_id: Optional[UUID] = None


class DigitalLoanUpdateDTO(TimestampMixin):
    loan_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Optional[LoanStatus] = None
    user_id: Optional[UUID] = None
    access_token: Optional[str] = None
    book_id: Optional[UUID] = None

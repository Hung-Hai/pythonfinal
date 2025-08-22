from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import secrets
from datetime import datetime
from typing import List, Optional

from src.service.base_service import BaseService
from src.repository.loan_repository import PhysicalLoanRepository, DigitalLoanRepository
from src.dto.loan_dto import (
    PhysicalLoanDTO, PhysicalLoanCreateDTO, PhysicalLoanUpdateDTO,
    DigitalLoanDTO, DigitalLoanCreateDTO, DigitalLoanUpdateDTO, LoanStatus
)


# ---------------- Physical Loan Service ---------------- #
class PhysicalLoanService(
    BaseService[PhysicalLoanCreateDTO, PhysicalLoanUpdateDTO, PhysicalLoanDTO, PhysicalLoanRepository]
):
    def __init__(self):
        super().__init__(PhysicalLoanRepository(), response_model=PhysicalLoanDTO)

    async def get_by_user(self, db: AsyncSession, user_id: UUID):
        return await self.repo.get_by_user(db, user_id)

    async def get_by_book(self, db: AsyncSession, book_id: UUID):
        return await self.repo.get_by_book(db, book_id)

    async def get_active_by_user_and_book(self, db: AsyncSession, user_id: UUID, book_id: UUID):
        return await self.repo.get_active_by_user_and_book(db, user_id, book_id)

    async def mark_returned(self, db: AsyncSession, loan_id: UUID):
        return await self.repo.mark_returned(db, loan_id)

    async def mark_overdue(self, db: AsyncSession, loan_id: UUID):
        return await self.repo.mark_overdue(db, loan_id)

    async def get_by_status(self, db: AsyncSession, status: LoanStatus) -> List[PhysicalLoanDTO]:
        return await self.repo.get_by_status(db, status)

    async def get_overdue_loans(self, db: AsyncSession) -> List[PhysicalLoanDTO]:
        return await self.repo.get_overdue_loans(db)

    async def get_active_by_user(self, db: AsyncSession, user_id: UUID) -> List[PhysicalLoanDTO]:
        return await self.repo.get_active_by_user(db, user_id)

    async def renew_loan(self, db: AsyncSession, loan_id: UUID, new_due_date: Optional[datetime] = None) -> Optional[PhysicalLoanDTO]:
        return await self.repo.renew_loan(db, loan_id, new_due_date)

    async def get_user_loan_stats(self, db: AsyncSession, user_id: UUID):
        return await self.repo.get_user_loan_stats(db, user_id)

    async def get_loans_by_date_range(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> List[PhysicalLoanDTO]:
        return await self.repo.get_loans_by_date_range(db, start_date, end_date)

    async def bulk_return_loans(self, db: AsyncSession, loan_ids: List[UUID]):
        return await self.repo.bulk_return_loans(db, loan_ids)

    async def bulk_update_status(self, db: AsyncSession, loan_ids: List[UUID], new_status: LoanStatus):
        return await self.repo.bulk_update_status(db, loan_ids, new_status)


# ---------------- Digital Loan Service ---------------- #
def generate_access_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)

class DigitalLoanService(
    BaseService[DigitalLoanCreateDTO, DigitalLoanUpdateDTO, DigitalLoanDTO, DigitalLoanRepository]
):
    def __init__(self):
        super().__init__(DigitalLoanRepository(), response_model=DigitalLoanDTO)
        
    async def create(self, db: AsyncSession, obj_in: DigitalLoanCreateDTO) -> DigitalLoanDTO:
        # Always generate a secure token if not provided
        if not obj_in.access_token:
            obj_in.access_token = generate_access_token()
        return await super().create(db, obj_in)

    async def get_by_user(self, db: AsyncSession, user_id: UUID):
        return await self.repo.get_by_user(db, user_id)

    async def get_by_book(self, db: AsyncSession, book_id: UUID):
        return await self.repo.get_by_book(db, book_id)

    async def get_active_by_user_and_book(self, db: AsyncSession, user_id: UUID, book_id: UUID):
        return await self.repo.get_active_by_user_and_book(db, user_id, book_id)

    async def mark_overdue(self, db: AsyncSession, loan_id: UUID):
        return await self.repo.mark_overdue(db, loan_id)

    async def get_by_status(self, db: AsyncSession, status: LoanStatus) -> List[DigitalLoanDTO]:
        return await self.repo.get_by_status(db, status)

    async def get_overdue_loans(self, db: AsyncSession) -> List[DigitalLoanDTO]:
        return await self.repo.get_overdue_loans(db)

    async def get_active_by_user(self, db: AsyncSession, user_id: UUID) -> List[DigitalLoanDTO]:
        return await self.repo.get_active_by_user(db, user_id)

    async def renew_loan(self, db: AsyncSession, loan_id: UUID, new_due_date: Optional[datetime] = None) -> Optional[DigitalLoanDTO]:
        return await self.repo.renew_loan(db, loan_id, new_due_date)

    async def get_user_loan_stats(self, db: AsyncSession, user_id: UUID):
        return await self.repo.get_user_loan_stats(db, user_id)

    async def get_loans_by_date_range(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> List[DigitalLoanDTO]:
        return await self.repo.get_loans_by_date_range(db, start_date, end_date)

    async def bulk_update_status(self, db: AsyncSession, loan_ids: List[UUID], new_status: LoanStatus):
        return await self.repo.bulk_update_status(db, loan_ids, new_status)
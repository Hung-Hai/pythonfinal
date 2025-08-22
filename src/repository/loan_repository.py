from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, select, and_, or_, update, func
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from src.repository.base_repository import BaseRepository
from src.models.loan_physical_models import PhysicalLoansModel
from src.models.loan_digital_models import DigitalLoansModel
from src.dto.loan_dto import (
    PhysicalLoanDTO, DigitalLoanDTO,
    PhysicalLoanCreateDTO, DigitalLoanCreateDTO,
    PhysicalLoanUpdateDTO, DigitalLoanUpdateDTO,
    LoanStatus
)

# ---------------- Physical Loan ---------------- #
class PhysicalLoanRepository(
    BaseRepository[
        PhysicalLoansModel,
        PhysicalLoanCreateDTO,
        PhysicalLoanUpdateDTO,
        PhysicalLoanDTO
    ]
):
    def __init__(self):
        super().__init__(PhysicalLoansModel)

    def _model_to_dto(self, db_obj: PhysicalLoansModel) -> PhysicalLoanDTO:
        if not db_obj:
            return None
        return PhysicalLoanDTO.from_orm(db_obj)

    async def get_by_user(self, db: AsyncSession, user_id: UUID) -> List[PhysicalLoanDTO]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def get_by_book(self, db: AsyncSession, book_id: UUID) -> List[PhysicalLoanDTO]:
        stmt = select(self.model).where(self.model.book_id == book_id)
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def get_active_by_user_and_book(
        self, db: AsyncSession, user_id: UUID, book_id: UUID
    ) -> Optional[PhysicalLoanDTO]:
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.book_id == book_id,
                self.model.status != LoanStatus.RETURNED
            )
        )
        result = await db.execute(stmt)
        db_obj = result.scalars().first()
        return self._model_to_dto(db_obj)

    async def mark_returned(
        self, db: AsyncSession, id: UUID, return_date: datetime = datetime.now()
    ) -> Optional[PhysicalLoanDTO]:
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        db_obj = result.scalars().first()
        if not db_obj:
            return None

        db_obj.status = LoanStatus.RETURNED
        db_obj.return_date = return_date
        await db.commit()
        await db.refresh(db_obj)
        return self._model_to_dto(db_obj)

    async def mark_overdue(self, db: AsyncSession, id: UUID) -> Optional[PhysicalLoanDTO]:
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        db_obj = result.scalars().first()
        if not db_obj:
            return None

        db_obj.status = LoanStatus.OVERDUE
        await db.commit()
        await db.refresh(db_obj)
        return self._model_to_dto(db_obj)

    # New repository methods
    async def get_by_status(self, db: AsyncSession, status: LoanStatus) -> List[PhysicalLoanDTO]:
        stmt = select(self.model).where(self.model.status == status)
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def get_overdue_loans(self, db: AsyncSession) -> List[PhysicalLoanDTO]:
        stmt = select(self.model).where(
            and_(
                self.model.status == LoanStatus.OVERDUE,
                self.model.return_date.is_(None)
            )
        )
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def get_active_by_user(self, db: AsyncSession, user_id: UUID) -> List[PhysicalLoanDTO]:
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.status.in_([LoanStatus.CHECKOUT, LoanStatus.OVERDUE])
            )
        )
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def renew_loan(self, db: AsyncSession, id: UUID, new_due_date: Optional[datetime] = None) -> Optional[PhysicalLoanDTO]:
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        db_obj = result.scalars().first()
        if not db_obj:
            return None

        if new_due_date:
            db_obj.due_date = new_due_date
        else:
            # Default renewal: extend by 14 days
            db_obj.due_date = datetime.now() + timedelta(days=14)
        
        db_obj.status = LoanStatus.CHECKOUT
        await db.commit()
        await db.refresh(db_obj)
        return self._model_to_dto(db_obj)

    async def get_user_loan_stats(self, db: AsyncSession, user_id: UUID) -> dict:
        stmt = select(
            func.count(self.model.id).label('total_loans'),
            func.count(case((self.model.status.in_([LoanStatus.CHECKOUT, LoanStatus.OVERDUE]), 1))).label('active_loans'),
            func.count(case((self.model.status == LoanStatus.OVERDUE, 1))).label('overdue_loans'),
            func.count(case((self.model.status == LoanStatus.RETURNED, 1))).label('returned_loans')
        ).where(self.model.user_id == user_id)
        
        result = await db.execute(stmt)
        stats = result.first()
        return {
            'total_loans': stats.total_loans or 0,
            'active_loans': stats.active_loans or 0,
            'overdue_loans': stats.overdue_loans or 0,
            'returned_loans': stats.returned_loans or 0
        }

    async def get_loans_by_date_range(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> List[PhysicalLoanDTO]:
        stmt = select(self.model).where(
            and_(
                self.model.loan_date >= start_date,
                self.model.loan_date <= end_date
            )
        )
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def bulk_return_loans(self, db: AsyncSession, loan_ids: List[UUID]) -> List[PhysicalLoanDTO]:
        results = []
        for loan_id in loan_ids:
            loan = await self.mark_returned(db, loan_id)
            if loan:
                results.append(loan)
        return results

    async def bulk_update_status(self, db: AsyncSession, loan_ids: List[UUID], new_status: LoanStatus) -> List[PhysicalLoanDTO]:
        stmt = update(self.model).where(
            self.model.id.in_(loan_ids)
        ).values(status=new_status).returning(self.model)
        
        result = await db.execute(stmt)
        await db.commit()
        return [self._model_to_dto(obj) for obj in result.scalars().all()]


# ---------------- Digital Loan ---------------- #
class DigitalLoanRepository(
    BaseRepository[
        DigitalLoansModel,
        DigitalLoanCreateDTO,
        DigitalLoanUpdateDTO,
        DigitalLoanDTO
    ]
):
    def __init__(self):
        super().__init__(DigitalLoansModel)

    def _model_to_dto(self, db_obj: DigitalLoansModel) -> DigitalLoanDTO | None:
        if not db_obj:
            return None
        return DigitalLoanDTO.from_orm(db_obj)

    async def get_by_user(self, db: AsyncSession, user_id: UUID) -> List[DigitalLoanDTO]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def get_by_book(self, db: AsyncSession, book_id: UUID) -> List[DigitalLoanDTO]:
        stmt = select(self.model).where(self.model.book_id == book_id)
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def get_active_by_user_and_book(
        self, db: AsyncSession, user_id: UUID, book_id: UUID
    ) -> Optional[DigitalLoanDTO]:
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.book_id == book_id,
                self.model.status.in_([LoanStatus.CHECKOUT, LoanStatus.OVERDUE])
            )
        )
        result = await db.execute(stmt)
        db_obj = result.scalars().first()
        return self._model_to_dto(db_obj)

    async def mark_overdue(self, db: AsyncSession, id: UUID) -> Optional[DigitalLoanDTO]:
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        db_obj = result.scalars().first()
        if not db_obj:
            return None

        db_obj.status = LoanStatus.EXPIRED
        await db.commit()
        await db.refresh(db_obj)
        return self._model_to_dto(db_obj)

    # New repository methods
    async def get_by_status(self, db: AsyncSession, status: LoanStatus) -> List[DigitalLoanDTO]:
        stmt = select(self.model).where(self.model.status == status)
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def get_overdue_loans(self, db: AsyncSession) -> List[DigitalLoanDTO]:
        stmt = select(self.model).where(self.model.status == LoanStatus.EXPIRED)
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def get_active_by_user(self, db: AsyncSession, user_id: UUID) -> List[DigitalLoanDTO]:
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.status.in_([LoanStatus.CHECKOUT])
            )
        )
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def renew_loan(self, db: AsyncSession, id: UUID, new_due_date: Optional[datetime] = None) -> Optional[DigitalLoanDTO]:
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        db_obj = result.scalars().first()
        if not db_obj:
            return None

        if new_due_date:
            db_obj.due_date = new_due_date
        else:
            # Default renewal: extend by 7 days for digital loans
            db_obj.due_date = datetime.now() + timedelta(days=7)
        
        db_obj.status = LoanStatus.CHECKOUT
        await db.commit()
        await db.refresh(db_obj)
        return self._model_to_dto(db_obj)

    async def get_user_loan_stats(self, db: AsyncSession, user_id: UUID) -> dict:
        stmt = select(
            func.count(self.model.id).label('total_loans'),
            func.count(case((self.model.status == LoanStatus.CHECKOUT, 1))).label('active_loans'),
            func.count(case((self.model.status == LoanStatus.EXPIRED, 1))).label('expired_loans')
        ).where(self.model.user_id == user_id)
        
        result = await db.execute(stmt)
        stats = result.first()
        return {
            'total_loans': stats.total_loans or 0,
            'active_loans': stats.active_loans or 0,
            'expired_loans': stats.expired_loans or 0
        }

    async def get_loans_by_date_range(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> List[DigitalLoanDTO]:
        stmt = select(self.model).where(
            and_(
                self.model.loan_date >= start_date,
                self.model.loan_date <= end_date
            )
        )
        result = await db.execute(stmt)
        return [self._model_to_dto(obj) for obj in result.scalars().all()]

    async def bulk_update_status(self, db: AsyncSession, loan_ids: List[UUID], new_status: LoanStatus) -> List[DigitalLoanDTO]:
        stmt = update(self.model).where(
            self.model.id.in_(loan_ids)
        ).values(status=new_status).returning(self.model)
        
        result = await db.execute(stmt)
        await db.commit()
        return [self._model_to_dto(obj) for obj in result.scalars().all()]
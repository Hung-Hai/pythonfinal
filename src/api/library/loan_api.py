from datetime import datetime
from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from src.api.library.base_api import BaseAPI
from src.service.loan_service import PhysicalLoanService, DigitalLoanService
from src.dto.loan_dto import (
    LoanStatus, PhysicalLoanDTO, PhysicalLoanCreateDTO, PhysicalLoanUpdateDTO,
    DigitalLoanDTO, DigitalLoanCreateDTO, DigitalLoanUpdateDTO
)
from src.utils.db_utils import create_database_session


# ---------------- Physical Loan API ---------------- #
physical_loan_api = BaseAPI[
    PhysicalLoanDTO, PhysicalLoanCreateDTO, PhysicalLoanUpdateDTO, PhysicalLoanService
](
    prefix="/physical-loans",
    service_provider=PhysicalLoanService,
    tags=["Physical Loans"],
)

physical_loan_api.register_crud_routes()

@physical_loan_api.router.get("/user/{user_id}", response_model=List[PhysicalLoanDTO])
async def get_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    return await service.get_by_user(db, user_id)


@physical_loan_api.router.get("/book/{book_id}", response_model=List[PhysicalLoanDTO])
async def get_by_book(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    return await service.get_by_book(db, book_id)


@physical_loan_api.router.get(
    "/active/user/{user_id}/book/{book_id}", response_model=PhysicalLoanDTO
)
async def get_active_by_user_and_book(
    user_id: UUID,
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    loan = await service.get_active_by_user_and_book(db, user_id, book_id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active loan found")
    return loan

@physical_loan_api.router.put("/{loan_id}/return", response_model=PhysicalLoanDTO)
async def mark_returned(
    loan_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    loan = await service.mark_returned(db, loan_id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan


@physical_loan_api.router.put("/{loan_id}/overdue", response_model=PhysicalLoanDTO)
async def mark_overdue(
    loan_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    loan = await service.mark_overdue(db, loan_id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan

@physical_loan_api.router.get("/status/{status}", response_model=List[PhysicalLoanDTO])
async def get_by_status(
    status: LoanStatus,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    """Get all physical loans with a specific status"""
    return await service.get_by_status(db, status)

@physical_loan_api.router.get("/overdue", response_model=List[PhysicalLoanDTO])
async def get_overdue_loans(
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    """Get all currently overdue physical loans"""
    return await service.get_overdue_loans(db)

@physical_loan_api.router.get("/active/user/{user_id}", response_model=List[PhysicalLoanDTO])
async def get_active_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    """Get all active physical loans for a user"""
    return await service.get_active_by_user(db, user_id)

@physical_loan_api.router.put("/{loan_id}/renew", response_model=PhysicalLoanDTO)
async def renew_loan(
    loan_id: UUID,
    new_due_date: Optional[datetime] = None,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    """Renew a physical loan with optional new due date"""
    loan = await service.renew_loan(db, loan_id, new_due_date)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found or cannot be renewed")
    return loan

@physical_loan_api.router.get("/stats/user/{user_id}")
async def get_user_loan_stats(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    """Get loan statistics for a specific user"""
    stats = await service.get_user_loan_stats(db, user_id)
    return {
        "total_loans": stats.total_loans,
        "active_loans": stats.active_loans,
        "overdue_loans": stats.overdue_loans,
        "returned_loans": stats.returned_loans
    }

@physical_loan_api.router.get("/date-range", response_model=List[PhysicalLoanDTO])
async def get_loans_by_date_range(
    start_date: datetime,
    end_date: datetime,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    """Get loans within a specific date range"""
    return await service.get_loans_by_date_range(db, start_date, end_date)

@physical_loan_api.router.post("/bulk-return")
async def bulk_return_loans(
    loan_ids: List[UUID],
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    """Mark multiple loans as returned in bulk"""
    results = await service.bulk_return_loans(db, loan_ids)
    return {"processed": len(results), "results": results}


# ---------------- Digital Loan API ---------------- #
digital_loan_api = BaseAPI[
    DigitalLoanDTO, DigitalLoanCreateDTO, DigitalLoanUpdateDTO, DigitalLoanService
](
    prefix="/digital-loans",
    service_provider=DigitalLoanService,
    tags=["Digital Loans"],
)

digital_loan_api.register_crud_routes()

@digital_loan_api.router.get("/user/{user_id}", response_model=List[DigitalLoanDTO])
async def get_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: DigitalLoanService = Depends(DigitalLoanService),
):
    return await service.get_by_user(db, user_id)


@digital_loan_api.router.get("/book/{book_id}", response_model=List[DigitalLoanDTO])
async def get_by_book(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: DigitalLoanService = Depends(DigitalLoanService),
):
    return await service.get_by_book(db, book_id)


@digital_loan_api.router.get(
    "/active/user/{user_id}/book/{book_id}", response_model=DigitalLoanDTO
)
async def get_active_by_user_and_book(
    user_id: UUID,
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: DigitalLoanService = Depends(DigitalLoanService),
):
    loan = await service.get_active_by_user_and_book(db, user_id, book_id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active loan found")
    return loan


@digital_loan_api.router.put("/{loan_id}/overdue", response_model=DigitalLoanDTO)
async def mark_overdue(
    loan_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: DigitalLoanService = Depends(DigitalLoanService),
):
    loan = await service.mark_overdue(db, loan_id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan

@digital_loan_api.router.get("/status/{status}", response_model=List[DigitalLoanDTO])
async def get_by_status(
    status: LoanStatus,
    db: AsyncSession = Depends(create_database_session),
    service: DigitalLoanService = Depends(DigitalLoanService),
):
    """Get all digital loans with a specific status"""
    return await service.get_by_status(db, status)

@digital_loan_api.router.get("/overdue", response_model=List[DigitalLoanDTO])
async def get_overdue_loans(
    db: AsyncSession = Depends(create_database_session),
    service: DigitalLoanService = Depends(DigitalLoanService),
):
    """Get all currently overdue digital loans"""
    return await service.get_overdue_loans(db)

@digital_loan_api.router.get("/active/user/{user_id}", response_model=List[DigitalLoanDTO])
async def get_active_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: DigitalLoanService = Depends(DigitalLoanService),
):
    """Get all active digital loans for a user"""
    return await service.get_active_by_user(db, user_id)

@digital_loan_api.router.put("/{loan_id}/renew", response_model=DigitalLoanDTO)
async def renew_loan(
    loan_id: UUID,
    new_due_date: Optional[datetime] = None,
    db: AsyncSession = Depends(create_database_session),
    service: DigitalLoanService = Depends(DigitalLoanService),
):
    """Renew a digital loan with optional new due date"""
    loan = await service.renew_loan(db, loan_id, new_due_date)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found or cannot be renewed")
    return loan

@digital_loan_api.router.get("/stats/user/{user_id}")
async def get_user_loan_stats(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: DigitalLoanService = Depends(DigitalLoanService),
):
    """Get loan statistics for a specific user"""
    stats = await service.get_user_loan_stats(db, user_id)
    return {
        "total_loans": stats.total_loans,
        "active_loans": stats.active_loans,
        "overdue_loans": stats.overdue_loans,
        "expired_loans": stats.expired_loans
    }

@digital_loan_api.router.get("/date-range", response_model=List[DigitalLoanDTO])
async def get_loans_by_date_range(
    start_date: datetime,
    end_date: datetime,
    db: AsyncSession = Depends(create_database_session),
    service: DigitalLoanService = Depends(DigitalLoanService),
):
    """Get loans within a specific date range"""
    return await service.get_loans_by_date_range(db, start_date, end_date)

@physical_loan_api.router.put("/bulk-status")
async def bulk_update_status(
    loan_ids: List[UUID],
    new_status: LoanStatus,
    db: AsyncSession = Depends(create_database_session),
    service: PhysicalLoanService = Depends(PhysicalLoanService),
):
    """Update status for multiple loans in bulk"""
    results = await service.bulk_update_status(db, loan_ids, new_status)
    return {"processed": len(results), "results": results}


# ---------------- Combine Routers ---------------- #
loan_router = APIRouter()
loan_router.include_router(physical_loan_api.router)
loan_router.include_router(digital_loan_api.router)
router = loan_router
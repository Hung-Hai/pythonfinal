from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from src.api.library.base_api import BaseAPI
from src.service.reservation_service import ReservationService
from src.dto.reservation_dto import ReservationCreateDTO, ReservationStatus, ReservationUpdateDTO, ReservationDTO
from src.utils.db_utils import create_database_session

def get_reservation_service() -> ReservationService:
    return ReservationService()

# Base CRUD endpoints
reservation_api = BaseAPI[ReservationCreateDTO, ReservationUpdateDTO, ReservationDTO, ReservationService](
    prefix="/reservations",
    service_provider=get_reservation_service,
    tags=["Reservation"],
)

reservation_api.register_crud_routes()

router = reservation_api.router


# --- Extra routes ---
@router.get("/user/{user_id}", response_model=List[ReservationDTO])
async def get_reservations_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(ReservationService),
):
    return await service.get_by_user(db, user_id)


@router.get("/book/{book_id}", response_model=List[ReservationDTO])
async def get_reservations_by_book(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(ReservationService),
):
    return await service.get_by_book(db, book_id)


@router.get("/book/{book_id}/active", response_model=List[ReservationDTO])
async def get_active_reservations(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(ReservationService),
):
    return await service.get_active(db, book_id)


@router.get("/book/{book_id}/queue/{user_id}", response_model=Optional[int])
async def get_queue_position(
    book_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(ReservationService),
):
    return await service.get_queue_position(db, user_id, book_id)

@router.get("/user/{user_id}/active", response_model=List[ReservationDTO])
async def get_active_reservations_by_user(
    user_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(get_reservation_service),
):
    """Get all active reservations for a specific user"""
    return await service.get_active_by_user(db, user_id)


@router.get("/user/{user_id}/status/{status}", response_model=List[ReservationDTO])
async def get_reservations_by_user_and_status(
    user_id: UUID,
    status: ReservationStatus,
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(get_reservation_service),
):
    """Get reservations for a user filtered by status"""
    return await service.get_by_user_and_status(db, user_id, status)


@router.get("/book/{book_id}/status/{status}", response_model=List[ReservationDTO])
async def get_reservations_by_book_and_status(
    book_id: UUID,
    status: ReservationStatus,
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(get_reservation_service),
):
    """Get reservations for a book filtered by status"""
    return await service.get_by_book_and_status(db, book_id, status)


@router.get("/expiring-soon", response_model=List[ReservationDTO])
async def get_expiring_soon_reservations(
    days: int = 7,
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(get_reservation_service),
):
    """Get reservations that are expiring soon"""
    return await service.get_expiring_soon(db, days)


@router.patch("/{reservation_id}/cancel", response_model=ReservationDTO)
async def cancel_reservation(
    reservation_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(get_reservation_service),
):
    """Cancel a specific reservation"""
    return await service.cancel_reservation(db, reservation_id)

@router.patch("/{reservation_id}/fulfill", response_model=ReservationDTO)
async def fulfill_reservation(
    reservation_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(get_reservation_service),
):
    """Mark a reservation as fulfilled"""
    return await service.fulfill_reservation(db, reservation_id)


@router.post("/bulk", response_model=List[ReservationDTO])
async def create_bulk_reservations(
    reservations: List[ReservationCreateDTO],
    db: AsyncSession = Depends(create_database_session),
    service: ReservationService = Depends(get_reservation_service),
):
    """Create multiple reservations at once"""
    return await service.create_bulk(db, reservations)



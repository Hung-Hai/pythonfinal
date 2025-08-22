from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.base_service import BaseService
from src.repository.reservation_repository import ReservationRepository
from src.dto.reservation_dto import (
    ReservationCreateDTO,
    ReservationStatus,
    ReservationUpdateDTO,
    ReservationDTO,
)


class ReservationService(
    BaseService[ReservationCreateDTO, ReservationUpdateDTO, ReservationDTO, ReservationRepository]
):
    def __init__(self):
        super().__init__(ReservationRepository(), response_model=ReservationDTO)

    async def get_by_user(self, db: AsyncSession, user_id: UUID) -> List[ReservationDTO]:
        return await self.repo.get_by_user(db, user_id)

    async def get_by_book(self, db: AsyncSession, book_id: UUID) -> List[ReservationDTO]:
        return await self.repo.get_by_book(db, book_id)

    async def get_active(self, db: AsyncSession, book_id: UUID) -> List[ReservationDTO]:
        return await self.repo.get_active(db, book_id)

    async def get_active_by_user(self, db: AsyncSession, user_id: UUID) -> List[ReservationDTO]:
        """Get all active reservations for a specific user"""
        return await self.repo.get_active_by_user(db, user_id)

    async def get_by_user_and_status(
        self, db: AsyncSession, user_id: UUID, status: ReservationStatus
    ) -> List[ReservationDTO]:
        """Get reservations for a user filtered by status"""
        return await self.repo.get_by_user_and_status(db, user_id, status)

    async def get_by_book_and_status(
        self, db: AsyncSession, book_id: UUID, status: ReservationStatus
    ) -> List[ReservationDTO]:
        """Get reservations for a book filtered by status"""
        return await self.repo.get_by_book_and_status(db, book_id, status)

    async def get_expiring_soon(self, db: AsyncSession, days: int = 7) -> List[ReservationDTO]:
        """Get reservations that are expiring within the specified number of days"""
        return await self.repo.get_expiring_soon(db, days)

    async def update_status(
        self, db: AsyncSession, reservation_id: UUID, status: ReservationStatus
    ) -> ReservationDTO:
        """Update the status of a reservation"""
        return await self.repo.update_status(db, reservation_id, status)

    async def cancel_reservation(self, db: AsyncSession, reservation_id: UUID) -> ReservationDTO:
        """Cancel a specific reservation"""
        return await self.update_status(db, reservation_id, ReservationStatus.CANCELLED)

    async def fulfill_reservation(self, db: AsyncSession, reservation_id: UUID) -> ReservationDTO:
        """Mark a reservation as fulfilled"""
        return await self.update_status(db, reservation_id, ReservationStatus.FULFILLED)

    async def expire_reservation(self, db: AsyncSession, reservation_id: UUID) -> ReservationDTO:
        """Mark a reservation as expired"""
        return await self.update_status(db, reservation_id, ReservationStatus.EXPIRED)
    
    async def create_bulk(
        self, db: AsyncSession, reservations_data: List[ReservationCreateDTO]
    ) -> List[ReservationDTO]:
        """Create multiple reservations at once"""
        results = []
        for reservation_data in reservations_data:
            result = await self.create(db, reservation_data)
            results.append(result)
        return results

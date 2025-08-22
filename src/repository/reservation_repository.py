# src/repositories/reservation_repository.py
from datetime import datetime, timedelta
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.reservation_models import ReservationModel
from src.dto.reservation_dto import (
    ReservationCreateDTO,
    ReservationUpdateDTO,
    ReservationDTO,
    ReservationStatus,
)
from src.repository.base_repository import BaseRepository


class ReservationRepository(
    BaseRepository[ReservationModel, ReservationCreateDTO, ReservationUpdateDTO, ReservationDTO]
):
    def __init__(self):
        super().__init__(ReservationModel)

    def _model_to_dto(self, db_obj: ReservationModel) -> Optional[ReservationDTO]:
        """Convert SQLAlchemy model to ReservationDTO."""
        return ReservationDTO.from_orm(db_obj) if db_obj else None

    async def get(self, db: AsyncSession, id: UUID) -> Optional[ReservationDTO]:
        """Get a reservation by ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return self._model_to_dto(result.scalars().first())

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict[str, Any]] = None,
    ) -> List[ReservationDTO]:
        """Get multiple reservations with optional filters."""
        query = select(self.model)
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_user(self, db: AsyncSession, user_id: UUID) -> List[ReservationDTO]:
        """Get all reservations made by a specific user."""
        result = await db.execute(select(self.model).filter(self.model.user_id == user_id))
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_book(self, db: AsyncSession, book_id: UUID) -> List[ReservationDTO]:
        """Get all reservations for a specific book."""
        result = await db.execute(select(self.model).filter(self.model.book_id == book_id))
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_active(self, db: AsyncSession, book_id: UUID) -> List[ReservationDTO]:
        """Get active (pending/fulfilled) reservations for a given book."""
        result = await db.execute(
            select(self.model).filter(
                self.model.book_id == book_id,
                self.model.status.in_([ReservationStatus.PENDING, ReservationStatus.FUFILLED]),
            )
        )
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_expiring_soon(self, db: AsyncSession, days: int = 7) -> List[ReservationDTO]:
        """Get reservations that are expiring within the specified number of days."""
        expiration_threshold = datetime.utcnow() + timedelta(days=days)
        result = await db.execute(
            select(self.model).filter(
                self.model.expiration_date <= expiration_threshold,
                self.model.expiration_date >= datetime.utcnow(),
                self.model.status == ReservationStatus.PENDING
            )
        )
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_book_and_status(
        self, db: AsyncSession, book_id: UUID, status: ReservationStatus
    ) -> List[ReservationDTO]:
        """Get reservations for a book filtered by status."""
        result = await db.execute(
            select(self.model).filter(
                self.model.book_id == book_id,
                self.model.status == status
            )
        )
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_user_and_status(
        self, db: AsyncSession, user_id: UUID, status: ReservationStatus
    ) -> List[ReservationDTO]:
        """Get reservations for a user filtered by status."""
        result = await db.execute(
            select(self.model).filter(
                self.model.user_id == user_id,
                self.model.status == status
            )
        )
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_active_by_user(self, db: AsyncSession, user_id: UUID) -> List[ReservationDTO]:
        """Get all active reservations for a specific user."""
        result = await db.execute(
            select(self.model).filter(
                self.model.user_id == user_id,
                self.model.status.in_([ReservationStatus.PENDING, ReservationStatus.FULFILLED])
            )
        )
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def update_status(
        self, db: AsyncSession, reservation_id: UUID, status: ReservationStatus
    ) -> ReservationDTO:
        """Update the status of a reservation."""
        reservation = await db.get(self.model, reservation_id)
        if reservation:
            reservation.status = status
            await db.commit()
            await db.refresh(reservation)
        return self._model_to_dto(reservation)
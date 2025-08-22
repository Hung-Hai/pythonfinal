# src/repositories/rating_repository.py
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.rating_models import RatingModel
from src.dto.rating_dto import RatingCreateDTO, RatingUpdateDTO, RatingDTO
from src.repository.base_repository import BaseRepository


class RatingRepository(
    BaseRepository[RatingModel, RatingCreateDTO, RatingUpdateDTO, RatingDTO]
):
    def __init__(self):
        super().__init__(RatingModel)

    def _model_to_dto(self, db_obj: RatingModel) -> Optional[RatingDTO]:
        """Convert SQLAlchemy model to RatingDTO."""
        return RatingDTO.from_orm(db_obj) if db_obj else None

    async def get(self, db: AsyncSession, id: UUID) -> Optional[RatingDTO]:
        """Get a rating by ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return self._model_to_dto(result.scalars().first())

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict[str, Any]] = None,
    ) -> List[RatingDTO]:
        """Get multiple ratings with optional filters."""
        query = select(self.model)
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_user(self, db: AsyncSession, user_id: UUID) -> List[RatingDTO]:
        """Get all ratings by a specific user."""
        result = await db.execute(select(self.model).filter(self.model.user_id == user_id))
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_book(self, db: AsyncSession, book_id: UUID) -> List[RatingDTO]:
        """Get all ratings for a specific book."""
        result = await db.execute(select(self.model).filter(self.model.book_id == book_id))
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_approved(self, db: AsyncSession, book_id: UUID) -> List[RatingDTO]:
        """Get only approved ratings for a given book."""
        result = await db.execute(
            select(self.model).filter(
                self.model.book_id == book_id, self.model.is_approved == True
            )
        )
        return [self._model_to_dto(row) for row in result.scalars().all()]
    
    async def get_average_rating(
        self, db: AsyncSession, book_id: UUID
    ) -> Optional[float]:
        result = await db.execute(
            select(func.avg(self.model.rating)).where(
                self.model.book_id == book_id,
                self.model.is_approved == True
            )
        )
        return result.scalar()

# src/repositories/books_physical_repository.py
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.books_physical_models import BooksPhysicalModel
from src.dto.book_physical_dto import (
    BooksPhysicalCreateDTO,
    BooksPhysicalUpdateDTO,
    BooksPhysicalDTO
)
from src.models.relationship_models import BookStatus
from src.repository.base_repository import BaseRepository


class BooksPhysicalRepository(
    BaseRepository[BooksPhysicalModel, BooksPhysicalCreateDTO, BooksPhysicalUpdateDTO, BooksPhysicalDTO]
):
    def __init__(self):
        super().__init__(BooksPhysicalModel)

    def _model_to_dto(self, db_obj: BooksPhysicalModel) -> Optional[BooksPhysicalDTO]:
        """Convert SQLAlchemy model to DTO."""
        return BooksPhysicalDTO.from_orm(db_obj) if db_obj else None

    async def get(self, db: AsyncSession, id: UUID) -> Optional[BooksPhysicalDTO]:
        """Get a single physical book by ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return self._model_to_dto(result.scalars().first())

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict[str, Any]] = None
    ) -> List[BooksPhysicalDTO]:
        """Get multiple physical books with optional filters."""
        query = select(self.model)
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_barcode(self, db: AsyncSession, barcode: str) -> Optional[BooksPhysicalDTO]:
        """Find a physical book by barcode."""
        result = await db.execute(select(self.model).filter(self.model.barcode == barcode))
        return self._model_to_dto(result.scalars().first())

    async def get_by_book_id(self, db: AsyncSession, book_id: UUID) -> List[BooksPhysicalDTO]:
        """Get all physical copies of a given book."""
        result = await db.execute(select(self.model).filter(self.model.book_id == book_id))
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_status(self, db: AsyncSession, status: BookStatus) -> List[BooksPhysicalDTO]:
        query = select(self.model).where(self.model.status == status)
        result = await db.execute(query)
        return [self.response_model.from_orm(row) for row in result.scalars().all()]

    async def get_available_by_book_id(self, db: AsyncSession, book_id: UUID) -> List[BooksPhysicalDTO]:
        query = select(self.model).where(
            self.model.book_id == book_id,
            self.model.status == BookStatus.AVAILABLE
        )
        result = await db.execute(query)
        return [self.response_model.from_orm(row) for row in result.scalars().all()]
# src/repositories/publisher_repository.py
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.models.publisher_models import PublishersModel
from src.dto.publisher_dto import PublisherCreateDTO, PublisherUpdateDTO, PublisherDTO
from src.repository.base_repository import BaseRepository


class PublisherRepository(
    BaseRepository[PublishersModel, PublisherCreateDTO, PublisherUpdateDTO, PublisherDTO]
):
    def __init__(self):
        super().__init__(PublishersModel)

    def _model_to_dto(self, db_obj: PublishersModel) -> Optional[PublisherDTO]:
        """Convert SQLAlchemy model to PublisherDTO."""
        return PublisherDTO.from_orm(db_obj) if db_obj else None

    async def get(self, db: AsyncSession, id: UUID) -> Optional[PublisherDTO]:
        """Get a single publisher by ID."""
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return self._model_to_dto(result.scalars().first())

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict[str, Any]] = None
    ) -> List[PublisherDTO]:
        """Get multiple publishers with optional filters."""
        query = select(self.model)
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_name(self, db: AsyncSession, name: str) -> List[PublisherDTO]:
        """Find publishers by (partial) name."""
        result = await db.execute(
            select(self.model).filter(self.model.name.ilike(f"%{name}%"))
        )
        return [self._model_to_dto(row) for row in result.scalars().all()]
    
    async def get_with_books(self, db: AsyncSession, id: UUID) -> Optional[PublishersModel]:
        """Get a publisher with all related books (raw model, not DTO)."""
        result = await db.execute(
            select(self.model)
            .options(joinedload(self.model.books))
            .filter(self.model.id == id)
        )
        return result.scalars().first()

    async def get_all_with_books(self, db: AsyncSession) -> List[PublishersModel]:
        """Get all publishers with their related books."""
        result = await db.execute(
            select(self.model).options(joinedload(self.model.books))
        )
        return result.scalars().all()

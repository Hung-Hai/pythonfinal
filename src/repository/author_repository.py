# src/repositories/author_repository.py
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.models.author_models import AuthorModel
from src.dto.author_dto import AuthorCreateDTO, AuthorUpdateDTO, AuthorDTO, BookLinkDTO
from src.repository.base_repository import BaseRepository


class AuthorRepository(BaseRepository[AuthorModel, AuthorCreateDTO, AuthorUpdateDTO, AuthorDTO]):
    def __init__(self):
        super().__init__(AuthorModel)

    def _model_to_dto(self, db_obj: AuthorModel) -> Optional[AuthorDTO]:
        """Convert SQLAlchemy model to AuthorDTO including books."""
        if not db_obj:
            return None
        dto_data = db_obj.__dict__.copy()

        # Map books relationship to BookLinkDTO list
        dto_data["books"] = [
            BookLinkDTO(
                book_id=link.book_id,
                primary_author=link.primary_author
            )
            for link in getattr(db_obj, "books", [])
        ]
        return AuthorDTO(**dto_data)

    async def get(self, db: AsyncSession, id: UUID) -> Optional[AuthorDTO]:
        """Get an author by ID with eager-loaded books."""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.books))
            .filter(self.model.id == id)
        )
        return self._model_to_dto(result.scalars().first())

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict[str, Any]] = None
    ) -> List[AuthorDTO]:
        """Get multiple authors with eager-loaded books."""
        query = select(self.model).options(selectinload(self.model.books))
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_name(self, db: AsyncSession, first_name: str, last_name: Optional[str] = None) -> List[AuthorDTO]:
        """Find authors by first name and optionally last name."""
        query = select(self.model).options(selectinload(self.model.books))
        query = query.where(self.model.first_name.ilike(f"%{first_name}%"))
        if last_name:
            query = query.where(self.model.last_name.ilike(f"%{last_name}%"))

        result = await db.execute(query)
        return [self._model_to_dto(row) for row in result.scalars().all()]

# src/repositories/book_repository.py
from typing import Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.models.books_models import BooksModel
from src.dto.book_dto import BookCreateDTO, BookUpdateDTO, BookDTO, AuthorBookLinkDTO
from src.repository.base_repository import BaseRepository


class BookRepository(BaseRepository[BooksModel, BookCreateDTO, BookUpdateDTO, BookDTO]):
    def __init__(self):
        super().__init__(BooksModel)

    def _model_to_dto(self, db_obj: BooksModel) -> Optional[BookDTO]:
        """Convert SQLAlchemy model instance to Pydantic DTO, including authors."""
        if not db_obj:
            return None
        dto_data = db_obj.__dict__.copy()

        # Map authors relationship to AuthorBookLinkDTO list
        dto_data["authors"] = [
            AuthorBookLinkDTO(
                author_id=link.author_id,
                primary_author=link.primary_author
            )
            for link in getattr(db_obj, "authors", [])
        ]
        return BookDTO(**dto_data)

    async def get(self, db: AsyncSession, id: UUID) -> Optional[BookDTO]:
        """Get a single book by ID, eager-loading authors."""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.authors))
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
    ) -> List[BookDTO]:
        """Get multiple books, eager-loading authors."""
        query = select(self.model).options(selectinload(self.model.authors))
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return [self._model_to_dto(row) for row in result.scalars().all()]

    async def get_by_isbn(self, db: AsyncSession, isbn: str) -> Optional[BookDTO]:
        """Find a book by its ISBN, eager-loading authors."""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.authors))
            .filter(self.model.isbn == isbn)
        )
        return self._model_to_dto(result.scalars().first())

    async def get_by_field(
        self,
        db: AsyncSession,
        field_name: str,
        value: Any,
        operator: str = "eq"
    ) -> List[BookDTO]:
        """
        Search books by any field with optional comparison operator.
        Supported operators: eq, contains, gt, lt, gte, lte.
        """
        if not hasattr(self.model, field_name):
            return []

        field = getattr(self.model, field_name)
        query = select(self.model).options(selectinload(self.model.authors))

        match operator:
            case "eq":
                query = query.where(field == value)
            case "contains":
                query = query.where(field.contains(value))
            case "gt":
                query = query.where(field > value)
            case "lt":
                query = query.where(field < value)
            case "gte":
                query = query.where(field >= value)
            case "lte":
                query = query.where(field <= value)
            case _:
                query = query.where(field == value)  # Default to equality

        result = await db.execute(query)
        return [self._model_to_dto(row) for row in result.scalars().all()]

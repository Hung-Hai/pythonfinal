from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.category_models import CategoriesModel
from src.models.relationship_models import book_category_table
from src.dto.category_dto import CategoryDTO, CategoryCreateDTO, CategoryUpdateDTO
from src.repository.base_repository import BaseRepository


class CategoryRepository(BaseRepository[CategoriesModel, CategoryCreateDTO, CategoryUpdateDTO, CategoryDTO]):

    def __init__(self):
        super().__init__(CategoriesModel)

    def _model_to_dto(self, db_obj: CategoriesModel) -> CategoryDTO:
        if not db_obj:
            return None

        # Collect related book_ids from relationship (via association table)
        book_ids = [book.id for book in db_obj.books] if hasattr(db_obj, "books") else []

        return CategoryDTO(
            id=db_obj.id,
            name=db_obj.name,
            description=db_obj.description,
            book_ids=book_ids,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at,
        )

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[CategoryDTO]:
        """Find a category by its name."""
        result = await db.execute(select(CategoriesModel).where(CategoriesModel.name == name))
        db_obj = result.scalar_one_or_none()
        return self._model_to_dto(db_obj)

    async def add_book_to_category(self, db: AsyncSession, category_id: str, book_id: str) -> None:
        """Attach a book to a category (many-to-many)."""
        await db.execute(
            book_category_table.insert().values(category_id=category_id, book_id=book_id)
        )
        await db.commit()

    async def remove_book_from_category(self, db: AsyncSession, category_id: str, book_id: str) -> None:
        """Detach a book from a category (many-to-many)."""
        await db.execute(
            book_category_table.delete().where(
                (book_category_table.c.category_id == category_id) &
                (book_category_table.c.book_id == book_id)
            )
        )
        await db.commit()

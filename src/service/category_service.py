# src/services/category_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from src.service.base_service import BaseService
from src.dto.category_dto import CategoryDTO, CategoryCreateDTO, CategoryUpdateDTO
from src.repository.category_repository import CategoryRepository


class CategoryService(BaseService[CategoryCreateDTO, CategoryUpdateDTO, CategoryDTO, CategoryRepository]):
    def __init__(self):
        super().__init__(CategoryRepository(), response_model=CategoryDTO)

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[CategoryDTO]:
        return await self.repo.get_by_name(db, name)

    async def add_book_to_category(self, db: AsyncSession, category_id: UUID, book_id: UUID) -> None:
        await self.repo.add_book_to_category(db, category_id, book_id)

    async def remove_book_from_category(self, db: AsyncSession, category_id: UUID, book_id: UUID) -> None:
        await self.repo.remove_book_from_category(db, category_id, book_id)

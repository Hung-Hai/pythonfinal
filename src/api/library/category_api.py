# src/api/category_api.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.api.library.base_api import BaseAPI
from src.dto.category_dto import CategoryDTO, CategoryCreateDTO, CategoryUpdateDTO
from src.service.category_service import CategoryService
from src.utils.db_utils import create_database_session


def get_category_service() -> CategoryService:
    return CategoryService()


category_api = BaseAPI[CategoryDTO, CategoryCreateDTO, CategoryUpdateDTO, CategoryService](
    prefix="/categories", service_provider=get_category_service, tags=["Categories"]
)

# register generic CRUD
category_api.register_crud_routes()

router = category_api.router

# ----- Custom endpoints -----

@category_api.router.get("/by-name/{name}", response_model=CategoryDTO)
async def get_category_by_name(
    name: str,
    db: AsyncSession = Depends(create_database_session),
    service: CategoryService = Depends(get_category_service),
):
    category = await service.get_by_name(db, name)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@category_api.router.post("/{category_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_book_to_category(
    category_id: UUID,
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: CategoryService = Depends(get_category_service),
):
    await service.add_book_to_category(db, category_id, book_id)


@category_api.router.delete("/{category_id}/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_book_from_category(
    category_id: UUID,
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: CategoryService = Depends(get_category_service),
):
    await service.remove_book_from_category(db, category_id, book_id)

from fastapi import Depends, Query
from typing import List
from uuid import UUID

from src.api.library.base_api import BaseAPI
from src.service.book_digital_service import BooksDigitalService
from src.dto.book_digital_dto import (
    BooksDigitalDTO,
    BooksDigitalCreateDTO,
    BooksDigitalUpdateDTO,
    FileFormat,
)
from src.utils.db_utils import create_database_session
from sqlalchemy.ext.asyncio import AsyncSession


def get_books_digital_service() -> BooksDigitalService:
    return BooksDigitalService()


books_digital_api = BaseAPI[BooksDigitalDTO, BooksDigitalCreateDTO, BooksDigitalUpdateDTO, BooksDigitalService](
    prefix="/digital-books",
    service_provider=get_books_digital_service,
    tags=["Digital Books"],
)

# Register standard CRUD routes
books_digital_api.register_crud_routes()

router = books_digital_api.router

# Extend with custom endpoints
@books_digital_api.router.get("/by-book/{book_id}", response_model=List[BooksDigitalDTO])
async def get_digital_books_by_book_id(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: BooksDigitalService = Depends(get_books_digital_service),
):
    return await service.get_by_book_id(db, book_id)


@books_digital_api.router.get("/by-format/{file_format}", response_model=List[BooksDigitalDTO])
async def get_digital_books_by_format(
    file_format: FileFormat,
    db: AsyncSession = Depends(create_database_session),
    service: BooksDigitalService = Depends(get_books_digital_service),
):
    return await service.get_by_file_format(db, file_format)

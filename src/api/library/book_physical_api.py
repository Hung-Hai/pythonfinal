from fastapi import Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from src.api.library.base_api import BaseAPI
from src.service.book_physical_service import BooksPhysicalService
from src.dto.book_physical_dto import (
    BooksPhysicalDTO,
    BooksPhysicalCreateDTO,
    BooksPhysicalUpdateDTO,
)
from src.utils.db_utils import create_database_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.relationship_models import BookStatus


def get_books_physical_service() -> BooksPhysicalService:
    return BooksPhysicalService()


books_physical_api = BaseAPI[BooksPhysicalDTO, BooksPhysicalCreateDTO, BooksPhysicalUpdateDTO, BooksPhysicalService](
    prefix="/physical-books",
    service_provider=get_books_physical_service,
    tags=["Physical Books"],
)

# Register standard CRUD routes
books_physical_api.register_crud_routes()

router = books_physical_api.router

# Custom endpoints
@router.get("/by-barcode/{barcode}", response_model=BooksPhysicalDTO)
async def get_physical_book_by_barcode(
    barcode: str,
    db: AsyncSession = Depends(create_database_session),
    service: BooksPhysicalService = Depends(get_books_physical_service),
):
    book = await service.get_by_barcode(db, barcode)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Physical book with barcode {barcode} not found"
        )
    return book


@router.get("/by-book/{book_id}", response_model=List[BooksPhysicalDTO])
async def get_physical_books_by_book_id(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: BooksPhysicalService = Depends(get_books_physical_service),
):
    return await service.get_by_book_id(db, book_id)


@router.patch("/{book_physical_id}/status", response_model=BooksPhysicalDTO)
async def update_physical_book_status(
    book_physical_id: UUID,
    status: BookStatus,
    db: AsyncSession = Depends(create_database_session),
    service: BooksPhysicalService = Depends(get_books_physical_service),
):
    try:
        return await service.update_status(db, book_physical_id, status)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/status/{status}", response_model=List[BooksPhysicalDTO])
async def get_physical_books_by_status(
    status: BookStatus,
    db: AsyncSession = Depends(create_database_session),
    service: BooksPhysicalService = Depends(get_books_physical_service),
):
    return await service.get_by_status(db, status)


@router.post("/bulk", response_model=List[BooksPhysicalDTO])
async def create_multiple_physical_books(
    books_data: List[BooksPhysicalCreateDTO],
    db: AsyncSession = Depends(create_database_session),
    service: BooksPhysicalService = Depends(get_books_physical_service),
):
    try:
        return await service.create_bulk(db, books_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/available/by-book/{book_id}", response_model=List[BooksPhysicalDTO])
async def get_available_physical_books_by_book_id(
    book_id: UUID,
    db: AsyncSession = Depends(create_database_session),
    service: BooksPhysicalService = Depends(get_books_physical_service),
):
    return await service.get_available_by_book_id(db, book_id)


@router.post("/with-validation", response_model=BooksPhysicalDTO)
async def create_physical_book_with_validation(
    book_data: BooksPhysicalCreateDTO,
    db: AsyncSession = Depends(create_database_session),
    service: BooksPhysicalService = Depends(get_books_physical_service),
):
    try:
        return await service.create_with_barcode_check(db, book_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
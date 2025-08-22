# src/api/book_api.py
from fastapi import Depends, HTTPException, Path, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.api.library.base_api import BaseAPI
from src.dto.book_dto import BookCreateDTO, BookUpdateDTO, BookDTO
from src.service.book_service import BookService
from src.utils.db_utils import create_database_session


def get_book_service() -> BookService:
    return BookService()


book_api = BaseAPI[BookDTO, BookCreateDTO, BookUpdateDTO, BookService](
    prefix="/books", service_provider=get_book_service, tags=["Books"]
)

# register base CRUD
book_api.register_crud_routes()

router = book_api.router

# custom route
@router.get("/search/", response_model=List[BookDTO])
async def search_books(
    field: str = Query(..., description="Field to search by (e.g., title, author, isbn)"),
    value: str = Query(..., description="Value to search for"),
    db: AsyncSession = Depends(create_database_session),
    service: BookService = Depends(get_book_service),
):
    books = await service.search_books(db, field, value)
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No books found with {field}={value}")
    return books

# Add these to src/api/book_api.py

@router.get("/author/{author_name}", response_model=List[BookDTO])
async def get_books_by_author(
    author_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(create_database_session),
    service: BookService = Depends(get_book_service),
):
    """Get books by specific author"""
    books = await service.get_books_by_author(db, author_name, skip, limit)
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No books found by author {author_name}")
    return books

@router.get("/genre/{genre}", response_model=List[BookDTO])
async def get_books_by_genre(
    genre: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(create_database_session),
    service: BookService = Depends(get_book_service),
):
    """Get books by genre"""
    books = await service.get_books_by_genre(db, genre, skip, limit)
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No books found in genre {genre}")
    return books

@router.get("/published/{year}", response_model=List[BookDTO])
async def get_books_by_year(
    year: int = Path(..., ge=1000, le=9999, description="Publication year (4 digits)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(create_database_session),
    service: BookService = Depends(get_book_service),
):
    """Get books published in a specific year"""
    books = await service.get_books_by_year(db, year, skip, limit)
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No books found published in {year}")
    return books

@router.get("/stats/count", response_model=dict)
async def get_book_count(
    db: AsyncSession = Depends(create_database_session),
    service: BookService = Depends(get_book_service),
):
    """Get total count of books"""
    count = await service.get_count(db)
    return {"total_books": count}
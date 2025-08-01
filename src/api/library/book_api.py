# src/api/book_api.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from src.utils.db_utils import create_database_session
from src.dto.book_dto import BookCreateDTO, BookUpdateDTO, BookDTO
from src.repository.book_repository import BookRepository

router = APIRouter(prefix="/books")

async def get_book_repo(db: AsyncSession = Depends(create_database_session)) -> BookRepository:
    return BookRepository()

@router.get("/", response_model=List[BookDTO], summary="List all books")
async def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000), 
    repo: BookRepository = Depends(get_book_repo),
    db: AsyncSession = Depends(create_database_session)
):
    books = await repo.get_multi(db, skip=skip, limit=limit)
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books found")
    return books

@router.get("/All", response_model=List[BookDTO], summary="List all books")
async def list_books(
    repo: BookRepository = Depends(get_book_repo),
    db: AsyncSession = Depends(create_database_session)
):
    books = await repo.get_all(db)
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books found")
    return books

@router.get("/{book_id}", response_model=BookDTO, summary="Get book by ID")
async def get_book(
    book_id: UUID,
    repo: BookRepository = Depends(get_book_repo),
    db: AsyncSession = Depends(create_database_session)
):
    book = await repo.get(db, id=book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@router.get("/search/", response_model=List[BookDTO], summary="Search books by field")
async def search_books(
    field: str = Query(..., description="Field name to search"),
    value: str = Query(..., description="Value to search for"),
    repo: BookRepository = Depends(get_book_repo),
    db: AsyncSession = Depends(create_database_session)
):
    books = await repo.get_by_field(db, field_name=field, value=value)
    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No books found with {field}={value}"
        )
    return books

@router.post("/", response_model=BookDTO, status_code=status.HTTP_201_CREATED, summary="Create a new book")
async def create_book(
    book: BookCreateDTO,
    repo: BookRepository = Depends(get_book_repo),
    db: AsyncSession = Depends(create_database_session)
):
    try:
        return await repo.create(db, obj_in=book)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.put("/{book_id}", response_model=BookDTO, summary="Update a book")
async def update_book(
    book_id: UUID, 
    book_data: BookUpdateDTO,
    repo: BookRepository = Depends(get_book_repo),
    db: AsyncSession = Depends(create_database_session)
):
    book = await repo.update(db, id=book_id, obj_in=book_data)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found or update failed"
        )
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a book")
async def delete_book(
    book_id: UUID,
    repo: BookRepository = Depends(get_book_repo),
    db: AsyncSession = Depends(create_database_session)
):
    success = await repo.delete(db, id=book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found or deletion failed"
        )
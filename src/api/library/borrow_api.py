from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timedelta

from src.utils.db_utils import create_database_session
from src.dto.borrow_dto import BorrowCreateDTO, BorrowStatusDTO, BorrowUpdateDTO, BorrowDTO
from src.repository.borrow_repository import BorrowRepository

router = APIRouter(prefix="/borrows")

async def get_borrow_repo(db: AsyncSession = Depends(create_database_session)) -> BorrowRepository:
    return BorrowRepository()

@router.get("/", response_model=List[BorrowDTO])
async def list_borrows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    repo: BorrowRepository = Depends(get_borrow_repo),
    db: AsyncSession = Depends(create_database_session)
):
    borrows = await repo.get_multi(db, skip=skip, limit=limit)
    if not borrows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No borrows found"
        )
    return borrows

@router.get("/{borrow_id}", response_model=BorrowDTO)
async def get_borrow(
    borrow_id: UUID,
    repo: BorrowRepository = Depends(get_borrow_repo)
):
    borrow = await repo.get_by_id(borrow_id)
    if not borrow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow not found"
        )
    return borrow

@router.get("/user/{user_id}", response_model=List[BorrowDTO])
async def get_borrows_by_user(
    user_id: int,
    repo: BorrowRepository = Depends(get_borrow_repo),
    db: AsyncSession = Depends(create_database_session)
):
    borrows = await repo.get_by_user(db, user_id)
    if not borrows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No borrows found for user {user_id}"
        )
    return borrows

@router.get("/book/{book_id}", response_model=List[BorrowDTO])
async def get_borrows_by_book(
    book_id: int,
    repo: BorrowRepository = Depends(get_borrow_repo),
    db: AsyncSession = Depends(create_database_session)
):
    borrows = await repo.get_by_book(db, book_id)
    if not borrows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No borrows found for book {book_id}"
        )
    return borrows

@router.get("/active/user-book/", response_model=Optional[BorrowDTO])
async def get_active_borrow(
    user_id: int = Query(..., description="User ID"),
    book_id: int = Query(..., description="Book ID"),
    repo: BorrowRepository = Depends(get_borrow_repo),
    db: AsyncSession = Depends(create_database_session)
):
    borrow = await repo.get_active_by_user_and_book(db, user_id, book_id)
    return borrow

@router.post("/", response_model=BorrowDTO, status_code=status.HTTP_201_CREATED)
async def create_borrow(
    borrow: BorrowCreateDTO,
    repo: BorrowRepository = Depends(get_borrow_repo),
    db: AsyncSession = Depends(create_database_session)
):
    # Check for existing active borrow
    existing_borrow = await repo.get_active_by_user_and_book(db,
        user_id=borrow.user_id,
        book_id=borrow.book_id
    )
    
    if existing_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active borrow for this book"
        )
    
    try:
        return await repo.create(obj_in=borrow)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    
@router.post("/rent", response_model=BorrowDTO, status_code=status.HTTP_201_CREATED)
async def rent_new_book(
    user_id: str = Query(..., description="book id"),
    book_id: str = Query(..., description="user od"),
    repo: BorrowRepository = Depends(get_borrow_repo),
    db: AsyncSession = Depends(create_database_session)
):
    existing_borrow = await repo.get_active_by_user_and_book(db,
        user_id=user_id,
        book_id=book_id
    )
    if existing_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active borrow for this book"
        )
    now = datetime.now()
    due_date = now + timedelta(days=7)
    new_borrow = BorrowCreateDTO(
        borrow_date=now,
        due_date=due_date,
        user_id=user_id,
        book_id=book_id,
        status=BorrowStatusDTO.CHECKOUT
    )
    
    try:
        return await repo.create(db, obj_in=new_borrow)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.put("/{borrow_id}", response_model=BorrowDTO)
async def update_borrow(
    borrow_id: UUID,
    borrow_data: BorrowUpdateDTO,
    repo: BorrowRepository = Depends(get_borrow_repo),
    db: AsyncSession = Depends(create_database_session)
):
    borrow = await repo.update(db, id=borrow_id, obj_in=borrow_data)
    if not borrow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow not found or update failed"
        )
    return borrow

@router.put("/{borrow_id}/return", response_model=BorrowDTO)
async def return_borrow(
    borrow_id: UUID,
    return_date: Optional[datetime] = None,
    repo: BorrowRepository = Depends(get_borrow_repo),
    db: AsyncSession = Depends(create_database_session)
):
    borrow = await repo.mark_returned(db, return_date, id=borrow_id)
    if not borrow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow not found"
        )
    return borrow

@router.put("/{borrow_id}/overdue", response_model=BorrowDTO)
async def mark_borrow_overdue(
    borrow_id: UUID,
    repo: BorrowRepository = Depends(get_borrow_repo),
    db: AsyncSession = Depends(create_database_session)
):
    borrow = await repo.mark_overdue(db, id=borrow_id)
    if not borrow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow not found"
        )
    return borrow

@router.delete("/{borrow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_borrow(
    borrow_id: UUID,
    repo: BorrowRepository = Depends(get_borrow_repo),
    db: AsyncSession = Depends(create_database_session)
):
    success = await repo.delete(db, id=borrow_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow not found or deletion failed"
        )
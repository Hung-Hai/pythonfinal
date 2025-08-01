from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from sqlalchemy.orm import selectinload
from src.models.borrow_models import *
from src.dto.borrow_dto import *
from src.repository.base_repository import BaseRepository

class BorrowRepository(BaseRepository[BorrowModel, BorrowCreateDTO, BorrowUpdateDTO, BorrowDTO]):
    def __init__(self):
        super().__init__(BorrowModel)

    def _model_to_dto(self, db_obj: BorrowModel) -> BorrowDTO:
        if not db_obj:
            return None
        return BorrowDTO.from_orm(db_obj) 

    async def get_by_user(self, db: AsyncSession, user_id: int) -> List[BorrowDTO]:
        """Get all borrows for a specific user"""
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await db.execute(stmt)
        db_objs = result.scalars().all()
        return [self._model_to_dto(db_obj) for db_obj in db_objs]

    async def get_by_book(self, db: AsyncSession, book_id: int) -> List[BorrowDTO]:
        """Get all borrows for a specific book"""
        stmt = select(self.model).where(self.model.book_id == book_id)
        result = await db.execute(stmt)
        db_objs = result.scalars().all()
        return [self._model_to_dto(db_obj) for db_obj in db_objs]

    async def get_active_by_user_and_book(
        self,
        db: AsyncSession,
        user_id: int,
        book_id: int
    ) -> Optional[BorrowDTO]:
        """Get active borrow (not returned) for a user-book pair"""
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.book_id == book_id,
                self.model.status != BorrowStatus.RETURNED
            )
        )
        result = await db.execute(stmt)
        db_obj = result.scalars().first()
        return self._model_to_dto(db_obj)

    async def mark_returned(
        self,
        db: AsyncSession,
        id: UUID,
        return_date: datetime = datetime.now()
    ) -> Optional[BorrowDTO]:
        """Mark a borrow as returned and set return date"""
        # Get the borrow first
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        db_obj = result.scalars().first()
        
        if not db_obj:
            return None
            
        # Update the borrow
        db_obj.status = BorrowStatus.RETURNED
        db_obj.return_date = return_date
        
        # Commit changes
        await db.commit()
        await db.refresh(db_obj)
        return self._model_to_dto(db_obj)

    async def mark_overdue(self, db: AsyncSession, id: UUID) -> Optional[BorrowDTO]:
        """Mark a borrow as overdue"""
        # Get the borrow first
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        db_obj = result.scalars().first()
        
        if not db_obj:
            return None
            
        # Update the borrow
        db_obj.status = BorrowStatus.OVERDUE
        
        # Commit changes
        await db.commit()
        await db.refresh(db_obj)
        return self._model_to_dto(db_obj)